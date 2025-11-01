from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

def generateResponse(question,chat_id=None,document_id=None):
    load_dotenv()
    response=""
    llm= ChatGoogleGenerativeAI(model='gemini-2.5-flash')
    parser= StrOutputParser()
    prompt= PromptTemplate(
        template='''
            You are a helpful AI Assistant.
            Answer the following question
            Question: {question}
        ''',
        input_variables=['question']
    )
    final_chain= prompt | llm | parser
    response= final_chain.invoke(question)
        
    return response
    

