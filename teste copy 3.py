from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
import pandas as pd
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from datetime import datetime
load_dotenv()


class ExtrairDados(BaseTool):
    name: str = "DadosAtracacao"  # nome da ferramenta com anotação de tipo
    description: str = """Esta ferramenta extrai os dados de atracação de uma tabela do excel de acordo com as datas informadas""" ## Descrição da ferramenta que auxiliará a IA a executar a tarefa
    

class Filter:
    def __init__(self):
       self.df = pd.read_excel('atracacao.xlsx')
       self.model = ChatOpenAI(model='gpt-3.5-turbo', api_key=os.getenv('TOKEN_OPENAI'), streaming=True)
       
       
    def filter_data_atracacao(self, datain, datafin):
        # Convertendo as datas de entrada para o formato datetime
        datain = pd.to_datetime(datain, format='%d/%m/%Y')
        datafin = pd.to_datetime(datafin, format='%d/%m/%Y')
        
        # Convertendo a coluna 'data_atracacao' para o formato datetime
        self.df['data_atracacao'] = pd.to_datetime(self.df['data_atracacao'])
        
        # Verificando se as datas estão na ordem correta
        if datain > datafin:
            raise ValueError("A data de início não pode ser posterior à data de fim.")
        
        # Filtrando o DataFrame entre as duas datas
        df_filtrado = self.df[(self.df['data_atracacao'] >= datain) & (self.df['data_atracacao'] <= datafin)]
        
        return df_filtrado
   
   
modelo = Filter()

print(modelo.filter_data_atracacao(datain='01/01/2024', datafin='05/01/2024'))
    
        
    # def _run(self):
    #     ...
        




# # Carregar variáveis de ambiente

# # Inicializar a memória para armazenar o contexto da conversa
# memory = ConversationBufferMemory()

# # Criar a instância do modelo com memória e verbose ativado
# conversation = ConversationChain(
#     llm=ChatOpenAI(model='gpt-4o', api_key=os.getenv('TOKEN_OPENAI'), streaming=True),  # Ativar streaming aqui
#     memory=memory,
#     verbose=False
# )

# # Carregar o dataframe do Excel



# # Criar o agente com o dataframe, modelo de linguagem, e memória, com streaming ativado
# agent = create_pandas_dataframe_agent(
#     ChatOpenAI(
#         model='gpt-3.5-turbo',
#         api_key=os.getenv('TOKEN_OPENAI'),
#         streaming=True  # Ativar o streaming aqui
#     ),
#     df,
#     verbose=True,
#     agent_type=AgentType.OPENAI_FUNCTIONS,
#     allow_dangerous_code=True,
#     memory=memory  # Configurar a memória no agente
# )

# try:
#     while True:
#         pergunta = input("Pergunta: ")
        
#         # Adicionar pergunta à memória para manter o contexto
#         conversation_input = conversation.predict(input=pergunta)

#         # Invocar o agente passando a pergunta com memória ativada
#         response = agent.invoke({"input": pergunta})
#         print()
#         print(response['output'])

# except KeyboardInterrupt:
#     print("Conversa encerrada.")
    
    
    
