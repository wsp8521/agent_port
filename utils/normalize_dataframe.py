import pandas as pd
 
 
def normalize_date(data):
        df = pd.DataFrame(data)
        # Remover as colunas que você quer normalizar e depois excluir
        remove_colunas = ['data_atracacao', 'data_inicio', 'data_termino', 'desatracacao']
        
        #adicionando nova coluna apenas apenas com a data
        df['atracacao'] = df['data_atracacao'].dt.normalize() 
        df['dataInicio'] = df['data_inicio'].dt.normalize() 
        df['dataTermino'] = df['data_termino'].dt.normalize() 
        df['_desatracacao'] = df['desatracacao'].dt.normalize() 
    
       # Remover as colunas de data
        df = df.drop(remove_colunas, axis=1)
        return df

