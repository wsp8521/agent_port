import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from langchain_groq import ChatGroq  # Biblioteca para usar Groq com LangChain
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.memory import ConversationBufferMemory
from utils.normalize_dataframe import normalize_date

# Carregar variáveis de ambiente
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('TOKEN_GROQ')  # Substituir pelo token correto

# Classe do agente de interação
class AgentTalkingCarga:
    def __init__(self, model, dataframe):
        self.dataframe = dataframe
        self.llm = ChatGroq(model=model, api_key=os.environ['GROQ_API_KEY'], streaming=True)  # Habilitando streaming
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.create_agent()

    def create_agent(self):
        agent_prompt_prefix = """
            Você é um assistente amigável especializado em fornecer informações estruturadas e precisas.
            [Instruções detalhadas de resposta, iguais ao exemplo anterior]
        """
        df = normalize_date(self.dataframe)
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type='tool-calling',  # Ajuste para usar ferramentas da Groq
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


# Função de interface do Streamlit
def chatbot_interface():
    # Criando o dataframe fictício (ou substitua por seu próprio)
    df = pd.read_excel('atracacao.xlsx')
    
    # Configuração inicial
    st.set_page_config(page_title='Agent Port', page_icon='🚢')
    
    # Sidebar
    st.sidebar.title("Configurações do Chatbot")
    models = ["llama-3.1-70b-versatile",
              "llama-3.2-90b-vision-preview",
              "gemma2-9b-it"]
    
    model_choice = st.sidebar.selectbox("Escolha o modelo", models, key="model_choice")

    # Inicializando o agente com o modelo e dataframe
    agent = AgentTalkingCarga(model_choice, df)

    # Central
    st.header('🤖 Agent Port 🚢')

    # Histórico da conversa
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibir mensagens na tela
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # Entrada do usuário
    user_input = st.chat_input("Digite sua pergunta:")
    if user_input:
        # Adicionar pergunta do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        # Preparar para exibir a resposta em streaming
        response_container = st.chat_message("assistant")
        response_text = ""

        # Exibir o spinner enquanto processa a resposta
        with st.spinner('Buscando informações. Aguarde!'):
            try:
                for chunk in agent.stream_response(user_input):
                    response_text += chunk
                    response_container.markdown(response_text)
            except Exception as e:
                st.error(f"Erro ao processar resposta: {e}")
        
        # Adicionar a resposta completa ao histórico
        st.session_state.messages.append({"role": "assistant", "content": response_text})


# Executar a interface do Streamlit
if __name__ == "__main__":
    chatbot_interface()
