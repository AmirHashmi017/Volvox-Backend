from .rag_utils import get_document_content,get_vector_store_retriever,format_docs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
from typing import List, Optional, Dict
import re
import os
import httpx

load_dotenv()

async def fetch_transcript_with_proxy(video_id: str) -> Optional[str]:
    """
    Alternative method using HTTP client with proxy support.
    This bypasses YouTube's bot detection by using residential proxies.
    """
    try:
        proxy_url = os.getenv('PROXY_URL')
        
        # Configure HTTP client with proxy
        client_config = {
            "timeout": 30.0,
            "follow_redirects": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        }
        
        # Add proxy if configured (httpx uses 'proxy' not 'proxies')
        if proxy_url:
            client_config["proxy"] = proxy_url
        
        async with httpx.AsyncClient(**client_config) as client:
            # Fetch video page
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = await client.get(url)
            
            if response.status_code != 200:
                return None
            
            # Extract caption tracks from ytInitialPlayerResponse
            html = response.text
            
            # Find caption tracks in the page
            import json
            caption_pattern = r'"captionTracks":(\[.*?\])'
            match = re.search(caption_pattern, html)
            
            if not match:
                return None
            
            caption_tracks = json.loads(match.group(1))
            
            # Prefer English captions
            caption_url = None
            for track in caption_tracks:
                lang_code = track.get('languageCode', '')
                if lang_code.startswith('en'):
                    caption_url = track.get('baseUrl')
                    break
            
            # Fallback to first available
            if not caption_url and caption_tracks:
                caption_url = caption_tracks[0].get('baseUrl')
            
            if not caption_url:
                return None
            
            # Fetch transcript XML
            transcript_response = await client.get(caption_url)
            if transcript_response.status_code != 200:
                return None
            
            # Parse and clean transcript
            transcript_xml = transcript_response.text
            text_pattern = r'<text[^>]*>(.*?)</text>'
            texts = re.findall(text_pattern, transcript_xml, re.DOTALL)
            
            # Clean HTML entities and combine
            full_text = ' '.join([
                re.sub(r'<[^>]+>', '', text)
                .replace('&amp;', '&')
                .replace('&lt;', '<')
                .replace('&gt;', '>')
                .replace('&quot;', '"')
                .replace('&#39;', "'")
                .strip()
                for text in texts
            ])
            
            return full_text if full_text else None
            
    except Exception as e:
        print(f"Proxy fetch error: {str(e)}")
        return None

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    raise ValueError("Invalid YouTube URL or Video ID")

async def SummarizeResearch(documents:List[str]):
    try:
        content_to_summarize=""
        for document in documents:
            document_content= await get_document_content(document)
            content_to_summarize+=document_content

        prompt= PromptTemplate(
        template="""
        You are a helpful AI Assistant summarize this {content}
        """,
        input_variables=['content']
        )
        llm= ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        parser= StrOutputParser()
        summarize_chain= prompt | llm | parser

        result= await summarize_chain.ainvoke(content_to_summarize)
        return result
    except Exception as e:
        return str(e)

async def SummarizeVideo(video_url:str):
    try:
        question= 'Summarize this Content of video'
        video_id = extract_video_id(video_url)
        transcript = None
        
        # Method 1: Try proxy-based HTTP fetch (works in production with proxy)
        print(f"Attempting proxy method for video {video_id}...")
        transcript = await fetch_transcript_with_proxy(video_id)
        
        # Method 2: Fallback to youtube-transcript-api (works locally, may fail in cloud)
        if not transcript:
            print("Proxy method failed, trying youtube-transcript-api...")
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)
                
                # Try multiple English variants
                preferred_languages = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
                transcript_data = None
                
                for transcript_obj in transcript_list:
                    if transcript_obj.language_code in preferred_languages:
                        transcript_data = transcript_obj.fetch()
                        break
                
                # Try any English variant
                if not transcript_data:
                    for transcript_obj in transcript_list:
                        if transcript_obj.language_code.startswith('en'):
                            transcript_data = transcript_obj.fetch()
                            break
                
                # Use first available language
                if not transcript_data:
                    first_transcript = list(transcript_list)[0]
                    transcript_data = first_transcript.fetch()
                
                if transcript_data:
                    transcript = " ".join([item.text for item in transcript_data])
                    
            except Exception as api_error:
                error_msg = str(api_error).lower()
                if "blocking" in error_msg or "bot" in error_msg or "cloud" in error_msg:
                    return """⚠️ YouTube is blocking transcript requests from this server.

**This is expected in production environments** (AWS, Azure, GCP, etc.)

**Solutions for Production Deployment:**

1. **Use Proxy Service** (Recommended):
   - Set PROXY_URL in .env: `PROXY_URL=http://your-proxy:8080`
   - Use residential proxy services like:
     • ScraperAPI (https://scraperapi.com)
     • Bright Data (https://brightdata.com)
     • Oxylabs (https://oxylabs.io)

2. **Alternative: YouTube Data API v3**:
   - Get API key from Google Cloud Console
   - More reliable for production
   - Has usage quotas

3. **Use yt-dlp Service**:
   - Deploy yt-dlp as separate microservice
   - Run on non-cloud IP or with proxy

**For Testing**: Run locally or use VPN.

Current error: """ + str(api_error)
        
        if not transcript or len(transcript.strip()) == 0:
            return "No transcript found. The video may not have captions enabled, or transcripts are region-restricted."
        
        print(f"Successfully retrieved transcript ({len(transcript)} chars)")
        
        # Continue with summarization
        retriever= await get_vector_store_retriever(transcript)
        prompt= PromptTemplate(
            template="""
            You are a helpful AI Assistant summarize this {content} of video. The content can 
            be irrelevant to each other because may it's different documents but you have to cover 
            all the aspects.
            """,
            input_variables=['content']
        )
        llm= ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        parser= StrOutputParser()
        video_summarize_chain= retriever | RunnableLambda(format_docs) | prompt | llm | parser
        result= await video_summarize_chain.ainvoke(question)
        return result

    except Exception as e:
        return f"Error summarizing video: {str(e)}"
        return str(e)
