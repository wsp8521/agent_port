from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar a memória para armazenar o contexto da conversa
memory = ConversationBufferMemory()

# Criar a instância do modelo com memória e verbose ativado
conversation = ConversationChain(
    llm=ChatOpenAI(model='gpt-4o', api_key=os.getenv('TOKEN_OPENAI'), streaming=True),  # Ativar streaming aqui
    memory=memory,
    verbose=False
)

# Carregar o dataframe do Excel
df = pd.read_excel('atracacao.xlsx')

# Criar o agente com o dataframe, modelo de linguagem, e memória, com streaming ativado
agent = create_pandas_dataframe_agent(
    ChatOpenAI(
        model='gpt-3.5-turbo',
        api_key=os.getenv('TOKEN_OPENAI'),
        streaming=True  # Ativar o streaming aqui
    ),
    df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True,
    memory=memory  # Configurar a memória no agente
)

try:
    while True:
        pergunta = input("Pergunta: ")
        
        # Adicionar pergunta à memória para manter o contexto
        conversation_input = conversation.predict(input=pergunta)

        # Invocar o agente passando a pergunta com memória ativada
        response = agent.invoke({"input": pergunta})
        print()
        print(response['output'])

except KeyboardInterrupt:
    print("Conversa encerrada.")
