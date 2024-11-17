import streamlit as st
from agents.agent_port_openai import AgentPort
import pandas as pd
from interface.agent_port import AgentPortInterface

# Configuração da página
st.set_page_config(
    page_title='Agent Port',
    page_icon='🚢'
)

st.header('🤖 Agent Port 🚢') # Exibição do título
df = pd.read_excel('atracacao.xlsx')
st.sidebar.title("Configurações do Chatbot")
model_choice = st.sidebar.selectbox("Escolha o modelo", ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini","gpt-3.5"], key="model_choice")

agent = AgentPort(model_choice, df)# Inicializando o agente com o modelo e dataframe
AgentPortInterface(agent_model=agent).run()


# df = pd.read_excel('atracacao.xlsx')
# agent_port_interface(df)
