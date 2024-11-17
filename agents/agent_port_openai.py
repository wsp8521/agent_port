import streamlit as st
import openai
from dotenv import load_dotenv
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory
from utils.normalize_dataframe import normalize_date
from agents.prompts_agents import prompts_dataFrame

# Carregar variáveis de ambiente
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')

# Classe do agente de interação
class AgentPort:
    def __init__(self, model, dataframe):
        self.dataframe = dataframe
        self.llm = ChatOpenAI(model=model, streaming=True, temperature=0.5)  # Habilitando streaming
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.create_agent()

    def create_agent(self):
        agent_prompt_prefix = prompts_dataFrame()
        
        df = normalize_date(self.dataframe)
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type='openai-tools',
            allow_dangerous_code=True
        )

    def stream_response(self, user_input):
        """Gera a resposta em streaming com validação de chunk."""
        try:
            for chunk in self.agent.stream(user_input):
                if isinstance(chunk, dict) and "output" in chunk:
                    yield chunk["output"]
                else:
                    print(f"Formato inesperado do chunk: {chunk}")  # Debugging
        except Exception as e:
            print(f"Erro no streaming: {e}")  # Debugging
            raise
