from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain.agents.agent_types import AgentType
import os

from dotenv import load_dotenv
load_dotenv()

df = pd.read_excel('atracacao.xlsx')


agent = create_pandas_dataframe_agent(
    ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENAI')),
    df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True  # Adicione esta linha
)

try:
    while True:
        pergunta = input("Pergunta: ")
        response = agent.invoke(pergunta)
        print(response['output'])

        
except KeyboardInterrupt:
    exit()
