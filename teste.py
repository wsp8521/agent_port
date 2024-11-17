import streamlit as st
import pandas as pd
import threading
from utils.normalize_dataframe import normalize_date
from your_code_module import AgentTalkingCarga  # Substitua pelo nome correto do seu módulo

# Configurando a página do Streamlit
st.set_page_config(page_title="Assistente de Carga", layout="wide")

# Função para carregar dados
@st.cache
def load_data(file):
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            st.error("Formato de arquivo não suportado.")
            return pd.DataFrame()
        return normalize_date(df)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Interface de upload de dados
st.sidebar.header("Configuração")
uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo (CSV ou Excel):", type=["csv", "xlsx", "xls"])
model = st.sidebar.selectbox("Modelo OpenAI", options=["gpt-3.5-turbo", "gpt-4"])
whisper_size = st.sidebar.selectbox("Modelo Whisper", options=["tiny", "base", "small", "medium", "large"])
voice_mode = st.sidebar.checkbox("Ativar Modo de Voz")

# Inicialização do agente
if uploaded_file:
    dataframe = load_data(uploaded_file)
    if not dataframe.empty:
        agent = AgentTalkingCarga(model=model, dataframe=dataframe, whisper_size=whisper_size, voice=voice_mode)
    else:
        st.error("O arquivo de dados é inválido ou está vazio.")
else:
    dataframe = None

# Funções de interação
def process_text_input():
    user_input = st.text_input("Digite sua pergunta:")
    if user_input:
        agent.memory.save_context({"input": user_input}, {"output": ""})
        response = agent.agent.invoke(user_input)
        agent.memory.save_context({"input": user_input}, {"output": response["output"]})
        st.write(f"**AI**: {response['output']}")

def process_voice_input():
    st.write("Modo de voz não suportado no Streamlit.")
    # Para implementar no futuro.

# Aba principal
st.title("Assistente de Carga")
if dataframe is not None:
    st.subheader("Dados Carregados")
    st.dataframe(dataframe.head(10))

    st.subheader("Interação")
    interaction_mode = st.radio("Escolha o modo de interação:", options=["Texto", "Voz"])
    if interaction_mode == "Texto":
        process_text_input()
    elif interaction_mode == "Voz" and voice_mode:
        process_voice_input()
    else:
        st.warning("O modo de voz está desativado.")
else:
    st.info("Por favor, faça upload de um arquivo CSV ou Excel para começar.")
