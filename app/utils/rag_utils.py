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
    chat= await chatHistoryModel.findOne({"_id":ObjectId(chat_id)})
    chat_history= chat.get('messages',[])
    history= "\n".join([f"User: {m['question']}\nAssistant: {m['response']}" for m in chat_history])
    print(chat_history)
    response=""
    llm= ChatGoogleGenerativeAI(model='gemini-2.5-flash')
    parser= StrOutputParser()

    prompt= PromptTemplate(
        template='''
            You are a helpful AI Assistant.
            Answer the following question
            Question: {question}
            This is all the previous Chat History {history}
        ''',
        input_variables=['question','history']
    )
    final_chain= prompt | llm | parser
    response= final_chain.invoke({"question":question,"history":history})
        
    return response
    

