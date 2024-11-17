from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent

class DataFrameTools:
    def __init__(self, model, dataframe):
        self.model = model  # Correção: remover vírgula
        self.dataframe = dataframe

    def data_frame_tool(self):
        agent_prompt_prefix = """
            Você é um assistente amigável.
            Se a resposta incluir o nome de um navio, retorne primeiramente o nome do navio.
            Se houver um valor numérico associado, formate-o no padrão brasileiro, onde os milhares são separados por pontos e as casas decimais por vírgula.
            Use a unidade de medida "tonelada" quando se referir à quantidade de movimentação.

            Exemplos:
            1. Qual a quantidade de movimentação?
            Resposta: 568 toneladas
            2. Qual a quantidade de movimentação de carga?
            Resposta: 568 toneladas
        """

        # Certifique-se de que o modelo é compatível
        self.tool = create_pandas_dataframe_agent(
            llm=self.model,  # Passar a instância correta
            df=self.dataframe,  # DataFrame formatado
            verbose=True,
            agent_type="zero-shot-react-description",  # Verifique a assinatura correta
            prefix=agent_prompt_prefix,
            allow_dangerous_code=True
        )
        return self.tool


