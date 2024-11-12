from agents.mov_carga import MovCarg
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()



model = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENAI'))
agent = MovCarg(model)

print( agent.run())
