from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import pandas as pd
from langchain.agents.agent_types import AgentType
import os

from dotenv import load_dotenv
load_dotenv()

class AgentMovCarga:
    def __init__(self,model):
        self.model = model,
       # self.data = self.__data_normalize(data)
        
        
    def data_normalize(self, data):
        # Remover as colunas que você quer normalizar e depois excluir
        remove_colunas = ['data_atracacao', 'data_inicio', 'data_termino', 'desatracacao']
        colunas_romalize = ['data_atracacao', 'data_inicio', 'data_termino', 'desatracacao']
        
        # Inicializando df com o valor de data para garantir que 'df' exista
        df = data.copy()  # Copiar data para df, para não modificar o original
        
        # Normalizando as colunas de data
        for col in colunas_romalize:
            if col in df.columns:  # Verificar se a coluna existe
                df[col] = df[col].dt.normalize()  # Aplica normalize na coluna
        
        # Remover as colunas de data
        df = df.drop(remove_colunas, axis=1)
        
        return df

        