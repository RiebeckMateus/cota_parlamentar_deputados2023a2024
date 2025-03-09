import firebase_admin
from firebase_admin import credentials, db, auth
import json
import os
from dotenv import load_dotenv

load_dotenv()

cred_data = st.secrets["FIREBASE_CREDENTIALS"]

if not cred_data:
    raise ValueError("Credenciais do Firebase não encontradas!")

cred_json = json.loads(cred_data)

class FirebaseApp:
    """
    Classe para gerenciar a interação com o Firebase Realtime Database.
    Permite carregar, enviar, recuperar e excluir dados.
    """
    
    def __init__(self):
        """
        Inicializa a conexão com o Firebase usando credenciais armazenadas em variáveis de ambiente.
        """
        
        cred_file = os.getenv('FIREBASE_CREDENTIALS')
        db_url = os.getenv('FIREBASE_DATABASE_URL')
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_json)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
            })
        
        self.ref = db.reference('projeto_deputados')
        self.DEPUTADOS_FILE = './data/deputados_com_salarios_e_despesas.json'
        self.DATA_PATH = './data/deputados_por_estado/'
        # self.RESUMO_CUSTO_POR_ESTADO = '.data/custo_por_estado.json'
    
    def _carregar_dados_deputados(self):
        """
        Carrega os dados dos deputados a partir de um arquivo JSON.
        
        Retorna:
            dict: Dados dos deputados carregados do arquivo JSON.
        """
        
        with open(self.DEPUTADOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _enviar_dados_firebase(self, deputados):
        """
        Envia um dicionário contendo os dados dos deputados para o Firebase.
        
        Parâmetros:
            deputados (dict): Dicionário contendo os dados a serem armazenados.
        """
        
        try:
            ref = self.ref
            ref.set(deputados)
            print('Dados armazenados no Firebase com sucesso!!')
        except Exception as e:
            print(f'Deu tilt ae mermão, dá uma olhada no que que deu: \n {e}')
    
    def _retornar_dados_deputados(self):
        """
        Retorna os dados armazenados no Firebase.
        
        Retorna:
            dict: Dados armazenados no Firebase.
        """
        
        try:
            data_ref = self.ref
            return data_ref.get()
        except Exception as e:
            print(f'Deu tilt aqui, mané. Olha o script retornar_dados_deputados pra ver se tem algo errado. \n{e}')

    def _enviar_dados_por_estado(self):
        """
        Lê arquivos JSON individuais para cada estado e armazena os dados no Firebase
        dentro de nós separados pelo nome do estado.
        """
        
        try:
            for filename in os.listdir(self.DATA_PATH):
                if filename.endswith('.json'):
                    estado = filename.replace('deputados_', '').replace('.json', '')
                    
                    with open(os.path.join(self.DATA_PATH, filename), 'r', encoding='utf-8') as f:
                        deputados = json.load(f)
                    
                    ref = self.ref.child(estado)
                    ref.set(deputados)
                    
                    print(f'Dados do estado {estado} armazenados no Firebase com sucesso!')
                    
        except Exception as e:
            print(f'Deu tilt ao subir os arquivos: \n {e}')

    def _excluir_dados_firebase(self):
        """
        Exclui todos os dados do Firebase.
        """
        try:
            self.ref.delete()
            print('Todos os dados foram excluídos do Firebase com sucesso!')
        except Exception as e:
            print(f'Erro ao excluir os dados: {e}')
            
    def _excluir_dados_estado_firebase(self, estado):
        """
        Exclui todos os dados do Firebase.
        """
        try:
            self.ref.child(estado).delete()
            print(f'O estado {estado} foi deletado com sucesso!')
        except Exception as e:
            print(f'Erro ao excluir os dados: {e}')

    def _retornar_dados_por_estado(self, estado):
        """
        Retorna os dados de um estado específico armazenado no Firebase.
        
        Parâmetros:
            estado (str): Nome do estado cujos dados devem ser recuperados.
        
        Retorna:
            dict: Dados do estado solicitado.
        """
        try:
            data_ref = self.ref.child(estado)
            return data_ref.get()
        except Exception as e:
            print(f'Deu tilt ao recuperar os dados do estado {estado}: \n{e}')
    
    # def _enviar_dados_resumo(self, arquivo='./data/custo_por_estado.json'):
    #     try:
    #         with open(arquivo, 'r', encoding='utf-8') as f:
    #             arquivo_json = json.load(f)
            
    #         for estado in arquivo_json:
    #             for ano in arquivo_json[estado]:
    #                 arquivo_json[estado][ano] = {str('m-'+mes): gastos for mes, gastos in arquivo_json[estado][ano].items()}
            
    #         ref = self.ref
    #         ref.child('resumo_gastos').set(arquivo_json)
    #         print(f'Deu bom, subiu o arquivo de resumo de despesas por estado!')
    #     except Exception as e:
    #         print(f'Noope. Deu ruim.\n{e}')
    
    # def _retornar_resumo_por_estado(self):
    #     try:
    #         data_ref = self.ref.child('resumo_gastos')
    #         return data_ref.get()
    #     except Exception as e:
    #         print(f'Deu tilt ao retornar os dados de resumo de por estado.\n{e}')

    def _enviar_dados_resumo_partido(self, arquivo='./data/custo_por_partido.json'):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                arquivo_json = json.load(f)
            
            for partido in arquivo_json:
                for estado in arquivo_json[partido]:
                    for ano in arquivo_json[partido][estado]:
                        arquivo_json[partido][estado][ano] = {str('m-'+mes): gastos for mes, gastos in arquivo_json[partido][estado][ano].items()}
            
            ref = self.ref
            ref.child('resumo_gastos_partido').set(arquivo_json)
            print(f'Deu bom, subiu o arquivo de resumo de despesas por partido!')
        except Exception as e:
            print(f'Noope. Deu ruim.\n{e}')
    
    def _retornar_resumo_por_partido(self):
        try:
            data_ref = self.ref.child('resumo_gastos_partido')
            return data_ref.get()
        except Exception as e:
            print(f'Deu tilt ao retornar os dados de resumo por partido.\n{e}')
    
    def _enviar_dados_deputados_base(self, arquivo='./data/deputados_base.json'):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                arquivo_json = json.load(f)
            
            ref = self.ref
            ref.child('deputados_base').set(arquivo_json)
            print('Deu bom, arquivo base dos deputados foi subido com sucesso!!!')
        except Exception as e:
            print(f'Noope. Deu ruim memo, dá uma oiada lá.\n{e}')
    
    def _retornar_dados_deputados_base(self):
        try:
            data_ref = self.ref.child('deputados_base')
            return data_ref.get()
        except Exception as e:
            print(f'Tiltchou.\n{e}')
    
    def _retornar_dados_deputados_individual(self, id):
        try:
            data_ref = self.ref.child('deputados_base').get()
            deputado = next((dep for dep in data_ref if int(dep['id']) == id), None)
            return deputado
        except Exception as e:
            print(f'Tiltchou.\n{e}')

if __name__ == '__main__':
    app = FirebaseApp()
    # excluir_dados = app._excluir_dados_firebase()
    # excluir_dados = app._excluir_dados_estado_firebase('AC')
    # excluir_dados = app._excluir_dados_estado_firebase('AL')
    # excluir_dados = app._excluir_dados_estado_firebase('AP')
    # excluir_dados = app._excluir_dados_estado_firebase('AM')
    # excluir_dados = app._excluir_dados_estado_firebase('BA')
    # excluir_dados = app._excluir_dados_estado_firebase('CE')
    # excluir_dados = app._excluir_dados_estado_firebase('DF')
    # excluir_dados = app._excluir_dados_estado_firebase('ES')
    # excluir_dados = app._excluir_dados_estado_firebase('GO')
    # excluir_dados = app._excluir_dados_estado_firebase('MA')
    # excluir_dados = app._excluir_dados_estado_firebase('MT')
    # excluir_dados = app._excluir_dados_estado_firebase('MS')
    # excluir_dados = app._excluir_dados_estado_firebase('MG')
    # excluir_dados = app._excluir_dados_estado_firebase('PA')
    # excluir_dados = app._excluir_dados_estado_firebase('PB')
    # excluir_dados = app._excluir_dados_estado_firebase('PR')
    # excluir_dados = app._excluir_dados_estado_firebase('PE')
    # excluir_dados = app._excluir_dados_estado_firebase('PI')
    # excluir_dados = app._excluir_dados_estado_firebase('RJ')
    # excluir_dados = app._excluir_dados_estado_firebase('RN')
    # excluir_dados = app._excluir_dados_estado_firebase('RS')
    # excluir_dados = app._excluir_dados_estado_firebase('RO')
    # excluir_dados = app._excluir_dados_estado_firebase('RR')
    # excluir_dados = app._excluir_dados_estado_firebase('SC')
    # excluir_dados = app._excluir_dados_estado_firebase('SP')
    # excluir_dados = app._excluir_dados_estado_firebase('SE')
    # excluir_dados = app._excluir_dados_estado_firebase('TO')
    # excluir_dados = app._excluir_dados_estado_firebase('resumo_gastos_partido')
    # # dados = app.carregar_dados_deputados()
    # enviar_dados = app.enviar_dados_firebase(dados)
    # enviar_dados_por_estado = app._enviar_dados_por_estado()
    enviar_dados_por_estado = app._enviar_dados_deputados_base()
    # print(app.retornar_dados_deputados())
    # app._enviar_dados_resumo_partido()
    # resumo_por_estado = app._retornar_resumo_por_estado()
    # print(resumo_por_estado)
