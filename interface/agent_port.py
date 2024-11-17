import streamlit as st
from agents.agent_port_openai import AgentPort


class AgentPortInterface:
    def __init__(self, agent_model):
        self.agent_model = agent_model
        

    def run(self):
        agent = self.agent_model # Inicializando o agente com o modelo e dataframe

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





