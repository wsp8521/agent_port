from agents.mov_carga import AgentMovCarga
from langchain.chat_models import ChatOpenAI
import pandas as pd
import os

agent = AgentMovCarga(
    model = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENAI'), streaming=True),
 
)

df = agent.data_normalize(data=pd.read_excel('atracacao.xlsx'))

print(df)