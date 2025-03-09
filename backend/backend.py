import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # isso aqui é um trampo regaçado, ta loco

import pandas as pd
from backend.bd_firebase import FirebaseApp
# from bd_firebase import FirebaseApp

class ProcessadorDados:
    def __init__(self, cred_data):
        self.firebase = FirebaseApp(cred_data)
    
    # def retornar_df_resumo_por_estado(self):
    #     '''Retorna os dados do Firebase como um DataFrame já tratado'''
    #     dados = self.firebase._retornar_resumo_por_estado()
        
    #     if not dados:
    #         print('Deu ruim, não retornou os dados.')
    #         return None
        
    #     dados_lista = []
        
    #     for estado, anos in dados.items():
    #         for ano, meses in anos.items():
    #             for mes, despesas in meses.items():
    #                 if despesas is None:
    #                     continue
    #                 for categoria, valor in despesas.items():
    #                     dados_lista.append({
    #                         'estado': estado,
    #                         'ano': int(ano),
    #                         'mes': mes,
    #                         'categoria': categoria,
    #                         'valor': valor
    #                     })
        
    #     df = pd.DataFrame(dados_lista)
    #     df['mes'] = df['mes'].apply(lambda x: x.replace('m-', ''))
    #     df['periodo'] = df.apply(lambda x: f'{int(x["mes"])}-{int(x["ano"])}', axis= 1)
    #     df['periodo'] = pd.to_datetime(df['periodo'], format='%m-%Y')
    #     # df = df.fillna(0)
    #     return df

    def retornar_df_resumo_por_partido(self):
        '''Retorna os dados do Firebase como um DataFrame já tratado'''
        dados = self.firebase._retornar_resumo_por_partido()
        
        if not dados:
            print('Deu ruim, não retornou os dados.')
            return None
        
        dados_lista = []
        
        for partido, estado in dados.items():
            for estado, anos in estado.items():
                for ano, meses in anos.items():
                    for mes, despesas in meses.items():
                        if despesas is None:
                            continue
                        for categoria, valor in despesas.items():
                            dados_lista.append({
                                'partido': partido,
                                'estado': estado,
                                'ano': int(ano),
                                'mes': mes,
                                'categoria': categoria,
                                'valor': valor
                            })
        
        df = pd.DataFrame(dados_lista)
        df['mes'] = df['mes'].apply(lambda x: x.replace('m-', ''))
        df['periodo'] = df.apply(lambda x: f'{int(x["mes"])}-{int(x["ano"])}', axis= 1)
        df['periodo'] = pd.to_datetime(df['periodo'], format='%m-%Y')
        # df = df.fillna(0)
        return df

    def processar_dados_deputados(self, estado):
        dados_json = self.firebase._retornar_dados_por_estado(estado)
        
        resultado = []
        
        for deputado in dados_json:
            for custo in deputado['despesa_parlamentar']:
                resultado.append({
                    'nome': deputado['nome'],
                    'link': deputado['link'],
                    'siglaPartido': deputado['siglaPartido'],
                    'siglaUF': deputado['siglaUF'],
                    'ano': custo['ano'],
                    'mes': custo['mes'],
                    'descricao': custo['descricao'],
                    'valor': float(custo['valorLiquido']),
                    'id': deputado['id'],
                    'link_imagem': deputado['link_imagem']
                })
        
        return pd.DataFrame(resultado)

    def retornar_df_deputados_base(self):
        dados_json = self.firebase._retornar_dados_deputados_base()
        
        retorno = []
        
        for deputado in dados_json:
            retorno.append({
                'nome' : deputado['nome'],
                'link' : deputado['link'],
                'id' : deputado['id'],
                'link_imagem' : deputado['link_imagem'],
                'partido' : deputado['siglaPartido'],
                'estado' : deputado['siglaUF']
            })
        return pd.DataFrame(retorno)

    def detalhe_deputado(self, id: int):
        dados_json = self.firebase._retornar_dados_deputados_individual(int(id))
        return dados_json

if __name__ == '__main__':
    app = ProcessadorDados()
    x = app.retornar_df_deputados_base()
    print(x)
