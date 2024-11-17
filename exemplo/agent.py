from tools import busca_wikipedia, retorna_temperatura_atual
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from langchain.agents.agent import AgentFinish 
from langchain.prompts import MessagesPlaceholder
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser 
from langchain.schema.runnable import RunnablePassthrough

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.memory import ConversationBufferMemory

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')

# Inicializando a memória do agente
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key='chat_history'
)

# Configuração do prompt do agente
prompt = ChatPromptTemplate.from_messages([
    ('system', 'Você é um assistente amigável chamado Isaac'),
    MessagesPlaceholder(variable_name='chat_history'),
    ('user', '{input}'),
    MessagesPlaceholder(variable_name='agent_scratchpad')
])

chat = ChatOpenAI(model='gpt-3.5-turbo', max_tokens=50)

# Lista de ferramentas
tools = [busca_wikipedia, retorna_temperatura_atual]
tools_json = [convert_to_openai_function(tool) for tool in tools]
tool_run = {tool.name: tool for tool in tools}

# Função de roteamento de ferramentas
def roteamento(resultado):
    if isinstance(resultado, AgentFinish):
        return resultado.return_values['output']
    else:
        return tool_run[resultado.tool].run(resultado.tool_input)

pass_through = RunnablePassthrough.assign(
    agent_scratchpad=lambda x: format_to_openai_function_messages(x.get('intermediate_steps', []))
)

# Definindo o pipeline do agente
agent_chain = pass_through | prompt | chat.bind(functions=tools_json) | OpenAIFunctionsAgentOutputParser()

# Função que executa o agente
def run_agent(input):
    passos_intermediarios = []
    chat_history = []  # inicializa o histórico de conversa
    while True:
        resposta = agent_chain.invoke({
            'input': input,
            'agent_scratchpad': format_to_openai_function_messages(passos_intermediarios),
            'chat_history': chat_history
        })
        if isinstance(resposta, AgentFinish):
            return resposta.return_values['output']
        
        observacao = tool_run[resposta.tool].run(resposta.tool_input)
        passos_intermediarios.append((resposta, observacao))
        chat_history.append({'role': 'assistant', 'content': observacao})

# Executando o agente        
agent_executor = AgentExecutor(
    agent=agent_chain,
    tools=tools,
    memory=memory,
    verbose=True
)

try:
    while True:
        pergunta = input("pergu'nta: ")
        resposta = agent_executor.invoke({'input': pergunta, 'chat_history': memory.load_memory_variables({})['chat_history']})
        print()
        print(resposta['output'])
except KeyboardInterrupt:
    print("Conversa encerrada.")
