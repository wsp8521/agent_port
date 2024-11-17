import requests
import datetime


from langchain.agents import tool
from pydantic import BaseModel, Field
import wikipedia
from dotenv import load_dotenv
import os
from langchain.agents.agent import AgentFinish


load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('TOKEN_OPENAI')
wikipedia.set_lang('pt')

class RetornTempArgs(BaseModel):
    latitude: float = Field(description='Latitude da localidade que buscamos a temperatura')
    longitude: float = Field(description='Longitude da localidade que buscamos a temperatura')


#criando uma tool de busca de temperatura
@tool(args_schema=RetornTempArgs)
def retorna_temperatura_atual(latitude: float, longitude: float):
    '''Retorna a temperatura atual para uma dada coordenada'''

    URL = 'https://api.open-meteo.com/v1/forecast'

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'temperature_2m',
        'forecast_days': 1,
    }

    resposta = requests.get(URL, params=params)
    if resposta.status_code == 200:
        resultado = resposta.json()
        
        hora_agora = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        lista_horas = [datetime.datetime.fromisoformat(temp_str) for temp_str in resultado['hourly']['time']]
        index_mais_prox = min(range(len(lista_horas)), key=lambda x: abs(lista_horas[x] - hora_agora))

        temp_atual = resultado['hourly']['temperature_2m'][index_mais_prox]
        return temp_atual
    else:
        raise Exception(f'Request para API {URL} falhou: {resposta.status_code}')
    
    
  
 #Criando tool wikipedia 

@tool
def busca_wikipedia(query: str):
    """Faz busca no wikipedia e retorna resumos de páginas para a query"""
    titulos_paginas = wikipedia.search(query)
    resumos = []
    for titulo in titulos_paginas[:3]:
        try:
            wiki_page = wikipedia.page(title=titulo, auto_suggest=True)
            resumos.append(f'Título da página: {titulo}\nResumo: {wiki_page.summary}')
        except:
            pass
    if not resumos:
        return 'Busca não teve retorno'
    else:
        return '\n\n'.join(resumos)

#print(tool_run['busca_wikipedia'].invoke({'query': 'Quem foi Napoleão'}))

#ROTEAMENTO DAS FERRAMENTAS