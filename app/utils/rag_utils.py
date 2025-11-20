from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from app.database import get_collection
from app.config import settings
from bson import ObjectId

async def generateResponse(question,chat_id=None,document_id=None):
    load_dotenv()

    chatHistoryModel= await get_collection(settings.CHATHISTORY_COLLECTION)
    chat= await chatHistoryModel.find_one({"_id":ObjectId(chat_id)})
    if(chat):
        chat_history= chat.get('messages',[])
        chat_history_str= "\n".join([f"User: {m['question']}\nAssistant: {m['response']}" for m in chat_history])
    else:
        chat_history_str=""
    response=""
    llm= ChatGoogleGenerativeAI(model='gemini-2.5-flash')
    parser= StrOutputParser()

    prompt= PromptTemplate(
        template='''
            You are a helpful AI Assistant.
            Answer the following question
            Question: {question}
            This is all the previous Chat History {chat_history}
        ''',
        input_variables=['question','chat_history']
    )
    final_chain= prompt | llm | parser
    response= final_chain.invoke({"question":question,"chat_history":chat_history_str})
        
    return response
    

