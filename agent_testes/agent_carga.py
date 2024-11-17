import os
from dotenv import load_dotenv
from utils.normalize_dataframe import normalize_date
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from utils.voice import  Voice

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')

class AgentMovCarga:
    def __init__(self, model, dataframe):
        self.model = ChatOpenAI(model=model, streaming=True, max_tokens=100, verbose=True)
        self.dataframe = normalize_date(dataframe)
        self.memory = ConversationBufferMemory(return_messages=True, memory_key='chat_history')
    
    def run(self, pergunta):
        prompt = self.__prompt_agent(input=pergunta)
        agent = self.__agent_executor()
        
        # Preparação da entrada com memória
        input_with_memory = {
            'input': prompt,
            'chat_history': self.memory.chat_memory.messages  # Mensagens armazenadas na memória
        }
       
        response = agent.invoke(input_with_memory)  # Geração da resposta
        
        # Certifica de que a resposta é uma string antes de adicioná-la à memória
        if isinstance(response, dict) and 'output' in response:
            response_content = response['output']
        elif isinstance(response, str):
            response_content = response
        else:
            response_content = str(response)
        
        # Atualização da memória
        self.memory.chat_memory.add_user_message(pergunta)
        self.memory.chat_memory.add_ai_message(response_content)
        
        return response_content
    
    def __agent_executor(self):
        agent_prompt_prefix = """
            Você se chama Itaqui, e está trabalhando com dataframe pandas no Python. O nome do Dataframe é atracaçao.
        """
        # Configuração do agente com memória
        agent = create_pandas_dataframe_agent(
            llm=self.model,
            df=self.dataframe,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type='openai-tools',
            allow_dangerous_code=True
        )
        return agent

    def __prompt_agent(self, input):
        # Template do sistema
        chat_system = '''
        Você é um assistente amigável.
        Se a resposta incluir o nome de um navio, retorne primeiramente o nome do navio.
        Se houver um valor numérico associado, formate-o no padrão brasileiro, onde os milhares são separados por pontos e as casas decimais por vírgula.
        Exemplo de formatação para valores: 22,976,277.58 deve ser formatado como 22.976.277,58.
        Use a unidade de medida "tonelada" quando se referir à quantidade de movimentação.
        
        Exemplos:
        1. Qual a quantidade de movimentação?
           Resposta: 568 toneladas
        2. Qual a quantidade de movimentação de carga?
           Resposta: 568 toneladas
        '''
        
        # Configuração do prompt com memória
        prompt_template = ChatPromptTemplate.from_messages([
            ('system', chat_system),
            MessagesPlaceholder(variable_name='chat_history'),  # Histórico de conversa
            ('user', '{input}')
        ])
        # Formatação do prompt com o histórico de memória
        chat_history = self.memory.chat_memory.messages if self.memory.chat_memory.messages else []
        prompt = prompt_template.format(input=input, chat_history=chat_history)
        return prompt
