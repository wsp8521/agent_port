import os
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()



modelo = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENAI'))

db = SQLDatabase.from_uri('sqlite:///ipca.db') #realizando conexão com o banco de dados

tookit = SQLDatabaseToolkit(
    db = db,
    llm = modelo
)

system_message = hub.pull('hwchase17/react') #baixando prompt prontos no hub langchain

#criando agentes
agente = create_react_agent(
    llm = modelo,
    tools=tookit.get_tools(),
    prompt=system_message,
)

#criando executor do agente
agente_executor = AgentExecutor(
    agent=agente,
    tools=tookit.get_tools(),
    verbose=True
)

prompt='''
        use as ferramentas necessárias para responder as perguntas relacionadas ao histórico do IPCA ao longo dos anos.
        Responda tudo em português.
        Pergunta: {q}
        
'''
prompt_template = PromptTemplate.from_template(prompt)


try:
    while True:
        question = input("Pergunta: ")   
        response = agente_executor.invoke(input={'input':prompt_template.format(q=question)})
        print(response.get('output'))

        
except KeyboardInterrupt:
    exit()

