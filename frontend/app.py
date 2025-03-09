import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # isso aqui é um trampo regaçado, ta loco

import streamlit as st
import plotly.express as px
from babel.numbers import format_currency
from backend.backend import ProcessadorDados

from datetime import datetime

ESTADOS_BRASIL = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins"
}


class UI:
    def __init__(self):
        self.processar = ProcessadorDados(st.secrets["FIREBASE_CREDENTIALS"])
    
    def parametros_id_deputados(self):
        dep_params = st.query_params.get('id_deputado')
        return dep_params
    
    def limpar_parametros(self):
        return st.query_params.clear()
    
    def despesa_estado_detalhado(self):
        estado = st.selectbox('estados', ESTADOS_BRASIL.keys())
        
        df = self.processar.processar_dados_deputados(estado)
        df['valor'] = df['valor'].abs()
        
        df['valor_formatado'] = df['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
        
        df_por_deputado_ano_mes_descricao = df.groupby(['nome', 'link', 'siglaPartido', 'ano', 'mes', 'descricao'])['valor'].sum().reset_index()
        df_por_deputado_ano_mes = df.groupby(['nome', 'link', 'siglaPartido', 'ano', 'mes'])['valor'].sum().reset_index()
        df_por_deputado_ano = df.groupby(['nome', 'link', 'siglaPartido', 'ano'])['valor'].sum().reset_index()
        df_por_deputado = df.groupby(['nome', 'link', 'siglaPartido'])['valor'].sum().reset_index().sort_values(by='valor', ascending=True)
        
        # df_deputado_agrupado_partido_nome = df.groupby(['siglaPartido', 'nome'])['valor'].sum().reset_index().sort_values(by='valor')
        # df_deputado_agrupado_partido_nome_categoria = df.groupby(['siglaPartido', 'nome', 'categoria'])['valor'].sum().reset_index().sort_values(by='valor')
        
        # top_10_maior_custo_partido_nome = df.sort_values(by='valor', ascending=False).head(10)
        # top_10_menor_custo_partido_nome = df.sort_values(by='valor', ascending=True).head(10)
        
        with st.expander('Filtros'):
            col1, col2 = st.columns([1, 2])
            with col1:
                df_de_uso = df.copy()
                
                selecao_ano = st.selectbox(label= 'Ano', options= [2023, 2024], index=None, placeholder='Todos anos disponíveis')
                selecao_mes = st.selectbox(label= 'Mês', options=list(range(1, 13)), index=None, placeholder='Todos meses disponíveis')
                
                if selecao_ano:
                    df_de_uso = df_de_uso.query(f'ano == {selecao_ano}')
                if selecao_mes:
                    df_de_uso = df_de_uso.query(f'mes == {selecao_mes}')
                
                partido_options = df_de_uso['siglaPartido'].unique().tolist()
                descricao_options = df_de_uso['descricao'].unique().tolist()
                selecao_partido = st.selectbox(label='Partido', options=partido_options, index=None, placeholder='Todos partidos disponíveis')
                selecao_descricao = st.selectbox(label='Despesa', options=descricao_options, index=None, placeholder='Todas despesas disponíveis')
                
                if selecao_partido:
                    df_de_uso = df_de_uso.query('siglaPartido == @selecao_partido')
                if selecao_descricao:
                    df_de_uso = df_de_uso.query('descricao == @selecao_descricao')
                
            
            
        valor_total_formatado = format_currency(number=df_de_uso['valor'].sum(), currency='BRL', locale='pt_BR')
        st.text(f'Despesa total: {valor_total_formatado}')
        
        grafico_por = st.selectbox(label='Gráfico por:', options=['Partido', 'Deputado'], index=0)
        
        if grafico_por == 'Deputado':
            
            colunas_agrupamento = ['nome', 'link']
            
            if selecao_ano:
                colunas_agrupamento.append('ano')
            if selecao_mes:
                colunas_agrupamento.append('mes')
            if selecao_partido:
                colunas_agrupamento.append('siglaPartido')
            if selecao_descricao:
                colunas_agrupamento.append('descricao')
            
            df_de_uso = df_de_uso.groupby(colunas_agrupamento)['valor'].sum().reset_index().sort_values(by='valor', ascending=True)
            df_de_uso['valor_formatado'] = df_de_uso['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
            
            fig = px.bar(
                data_frame=df_de_uso,
                x='valor',
                y='nome',
                # color='siglaPartido',
                orientation='h',
                text='valor_formatado',
                custom_data=['nome', 'valor_formatado'],
                labels={'nome': 'Deputado', 'valor': 'Despesa (R$)'}
            )
            
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>Despesa (R$): R$ %{customdata[1]}",
                # customdata= df_custo_por_estado_periodo['periodo'].dt.strftime('%B/%Y'),
                hoverlabel=dict(
                    # bgcolor='white',
                    font=dict(size=14),
                ),
                textfont_size=14,
                textfont_weight='bold'
            )
            
            fig.update_layout(
                width=1500,
                height= max(300, min(40 * df_de_uso.shape[0], 1000))
            )
        else:
            
            colunas_agrupamento = ['siglaPartido']
            
            if selecao_ano:
                colunas_agrupamento.append('ano')
            if selecao_mes:
                colunas_agrupamento.append('mes')
            if selecao_partido:
                colunas_agrupamento.append('siglaPartido')
            if selecao_descricao:
                colunas_agrupamento.append('descricao')
            
            df_de_uso = df_de_uso.groupby(colunas_agrupamento)['valor'].sum().reset_index().sort_values(by='valor', ascending=True)
            df_de_uso['valor_formatado'] = df_de_uso['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
            
            fig = px.bar(
                data_frame=df_de_uso,
                x='valor',
                y='siglaPartido',
                # color='siglaPartido',
                orientation='h',
                text='valor_formatado',
                custom_data=['siglaPartido', 'valor_formatado'],
                labels={'siglaPartido': 'Partido', 'valor': 'Despesa (R$)'}
            )
            
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>Valor: R$ %{customdata[1]}",
                # customdata= df_custo_por_estado_periodo['periodo'].dt.strftime('%B/%Y'),
                hoverlabel=dict(
                    # bgcolor='white',
                    font=dict(size=14),
                ),
                textfont_size=14,
                textfont_weight='bold'
            )
            
            fig.update_layout(
                width=1500,
                height= max(300, min(40 * df_de_uso.shape[0], 1000)),
                plot_bgcolor='rgba(240,240,240,1)',
                paper_bgcolor='rgba(250,250,250,1)',
                title=dict(
                    text=f'Despesa por {grafico_por}',
                    font=dict(size=26, color='black', family='Arial'),
                    x=.5,
                    xanchor='center',
                )
            )
        
        st.plotly_chart(fig)
        
        # st.write(df)
        # st.write(df_por_deputado_ano_mes_descricao)
        # st.write(df_por_deputado_ano_mes)
        # st.write(df_por_deputado_ano)
        # st.write(df_por_deputado)
        # st.write(top_10_maior_custo_partido_nome)
        # st.write(df_deputado_agrupado_partido_nome_categoria)
        
        # print(df_deputado_agrupado_nome.shape)

    def despesa_geral(self):
        df = self.processar.retornar_df_resumo_por_partido()
        df['valor'] = df['valor'].abs()
        
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
        
        selecao_categoria_despesa = col1.selectbox(label='Seleção da Categoria da Despesa', options=[str(cat).capitalize() for cat in df['categoria'].unique()], index=None, placeholder='Todas categorias selecionadas')
        
        if selecao_categoria_despesa:
            df = df[df['categoria']==selecao_categoria_despesa.upper()]
        else:
            df = df
        
        selecao_estado = col2.selectbox(label='Estado', options=sorted(df['estado'].map(ESTADOS_BRASIL).unique()), index=None, placeholder='Todos estados selecionados')
        
        if selecao_estado:
            sigla_estado = next((sigla for sigla, nome in ESTADOS_BRASIL.items() if nome == selecao_estado), None)
            df = df[df['estado']==sigla_estado]
        else:
            df = df
        
        selecao_partido = col3.selectbox(label='Partido', options=df['partido'].unique(), index=None, placeholder='Todos partidos selecionados')
        
        if selecao_partido:
            df = df[df['partido']==selecao_partido]
        else:
            df = df
        
        # df = df.sort_values(by='periodo')
        
        grafico_por = st.selectbox(label='Gráfico por:', options=['Estado', 'Partido'], index=0)
        
        if grafico_por == 'Estado':
            df_despesa_geral = df.groupby(['estado', 'periodo'])['valor'].sum().reset_index()
            df_despesa_geral['estado_nome'] = df_despesa_geral['estado'].map(ESTADOS_BRASIL)
            df_despesa_geral['periodo_formatado'] = df_despesa_geral['periodo'].dt.strftime('%m/%Y')
            df_despesa_geral['valor_formatado'] = df_despesa_geral['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
            
            
            fig = px.line(
                df_despesa_geral,
                x='periodo',
                y='valor',
                color='estado',
                markers=True,
                line_group='estado',
                labels={'valor': 'Despesa (R$)', 'estado': 'Estado (sigla)', 'periodo': 'Período'},
                custom_data=['estado_nome', 'periodo_formatado', 'valor_formatado']
            )
            
            fig.update_traces(
                hovertemplate="<b>%{customdata[1]}</b><br>Valor: R$ %{customdata[2]}<br>Estado: %{customdata[0]}<extra></extra>",
                # customdata= df_despesa_geral['periodo'].dt.strftime('%B/%Y'),
                hoverlabel=dict(
                    # bgcolor='white',
                    font=dict(size=14),
                )
            )
            
            fig.update_layout(
                title=dict(
                    text='Custo mensal por estado (2023-2024)',
                    font=dict(size=26, color='black', family='Arial'),
                    x=.5,
                    xanchor='center'
                ),
                # xaxis=dict(
                #     tickmode='array',
                #     tickvals=df_despesa_geral['periodo'].unique(),
                #     ticktext=df_despesa_geral['periodo_formatado'].unique(),
                #     tickangle=45
                # ),
                height = 750
            )
        else:
            
            df_despesa_geral = df.groupby(['partido', 'periodo'])['valor'].sum().reset_index()
            df_despesa_geral['periodo_formatado'] = df_despesa_geral['periodo'].dt.strftime('%m/%Y')
            df_despesa_geral['valor_formatado'] = df_despesa_geral['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
            
            
            fig = px.line(
                df_despesa_geral,
                x='periodo',
                y='valor',
                color='partido',
                markers=True,
                line_group='partido',
                labels={'valor': 'Despesa (R$)', 'partido': 'Partido', 'periodo': 'Período'},
                custom_data=['partido', 'periodo_formatado', 'valor_formatado']
            )
            
            fig.update_traces(
                hovertemplate="<b>%{customdata[1]}</b><br>Valor: %{customdata[2]}<br>Partido: %{customdata[0]}<extra></extra>",
                # customdata= df_despesa_geral['periodo'].dt.strftime('%B/%Y'),
                hoverlabel=dict(
                    # bgcolor='white',
                    font=dict(size=14),
                )
            )
            
            fig.update_layout(
                title=dict(
                    text='Custo mensal por partido (2023-2024)',
                    font=dict(size=26, color='black', family='Arial'),
                    x=0.5,
                    xanchor='center'
                ),
                # xaxis=dict(
                #     tickmode='array',
                #     tickvals=df_despesa_geral['periodo'].unique(),
                #     ticktext=df_despesa_geral['periodo_formatado'].unique(),
                #     tickangle=45
                # ),
                height = 750
            )
            
        
        valor_total_formatado = format_currency(number=df_despesa_geral['valor'].sum(), currency='BRL', locale='pt_BR')
        st.write(valor_total_formatado)
        
        fig.update_layout(
            # plot_bgcolor='rgba(240,240,240,1)',
            paper_bgcolor='rgba(250,250,250,1)'
        )
        
        st.plotly_chart(fig)
        # st.write(df)
        # st.write(df_despesa_geral) ##
        
        df_gastos_categoria = df.groupby('categoria')[['valor']].sum().reset_index()
        df_gastos_categoria['valor_formatado'] = df_gastos_categoria['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
        # df_gastos_categoria = df_gastos_categoria.sort_values('categoria')
        # st.write(df_gastos_categoria) ##
        
        fig_gastos_categoria = px.bar(
            data_frame=df_gastos_categoria,
            x='valor',
            y='categoria',
            labels={'valor': 'Despesa (R$)', 'categoria': 'Categoria'},
            category_orders={'categoria': df_gastos_categoria['categoria'].tolist()},
            custom_data=['categoria', 'valor_formatado'],
            height=800,
            # title='Gastos por categoria (acumulado)'
            # text_auto=True
        )
        
        fig_gastos_categoria.update_layout(
            title=dict(
                text='Gastos por despesa (descrição)',
                font=dict(size=26, family='Arial', color='black'),
                x=.5,
                xanchor='center'
            )
        )
        
        fig_gastos_categoria.update_traces(
            hovertemplate= '<b>%{customdata[0]}</b><br>Valor: %{customdata[1]}',
            texttemplate='%{customdata[1]}',
            # textposition='outside'
        )
        
        fig_gastos_categoria.update_layout(
            plot_bgcolor='rgba(240,240,240,1)',
            paper_bgcolor='rgba(250,250,250,1)'
        )
        
        st.plotly_chart(fig_gastos_categoria, use_container_width=True)
        
        df['valor_formatado'] = df['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
        
        fig_heatmap = px.density_heatmap(
            data_frame=df,
            x='estado',
            y='categoria',
            z='valor',
            color_continuous_scale='Blues',
            category_orders={'categoria': df_gastos_categoria['categoria'].tolist()},
            # custom_data=['categoria', 'valor_formatado']
            hover_data='valor_formatado'
        )
        
        fig_heatmap.update_traces(
            customdata=df['valor_formatado'],
            hovertemplate = '<b>Estado:</b> %{x}<br><b>Categoria:</b> %{y}<br><b>Valor:</b> %{z}'
        )
        
        # st.plotly_chart(fig_heatmap)
        st.text('Os reembolsos são tratados como valores negativos pelo site da câmara.\nEntende-se que estamos mostrando tudo aquilo que seria uma despesa para o estado, por isso estes valores negativos foram convertidos para valores positivos.')

    def despesa_deputado_individual(self):
        df = self.processar.retornar_df_deputados_base()
        
        busca_dep = st.text_input('Buscar', key='busca_Dep', placeholder='Ex: Silva')
        
        if busca_dep:
            deputados = df[df['nome'].str.contains(busca_dep, case=False, na=False)]
        else:
            deputados = df.copy()
        
        lista_deputados = deputados['nome']
        
        df_pos = deputados.copy()
        
        col1, col2 = st.columns([2,2])
        
        for i, dep in enumerate(lista_deputados):
            nome = deputados.query('nome == @dep')['nome'].iloc[0]
            link = deputados.query('nome == @dep')['link'].iloc[0]
            id = deputados.query('nome == @dep')['id'].iloc[0]
            link_imagem = f'https://www.camara.leg.br/internet/deputado/bandep/{id}.jpgmaior.jpg'
            link_route = f'/?id_deputado={id}'

            
            html_code = f"""
                <a href={link_route} style="text-decoration: none;">
                    <div style="display: flex; align-items: center; padding: 20px; border: 1px solid #ccc; border-radius: 5px; cursor: pointer; background-color: #f1f1f1; width: 100%; max-width: 800px; margin: 10px auto;">
                        <img src="{link_imagem}" alt="Foto do Deputado" style="width: 140px; height: 190px; border-radius: 50%; margin-right: 10px;">
                        <span style="font-size: 18px; color: black;">{nome}</span>
                    </div>
                </a>
            """
            
            if i % 2 == 0:
                with st.container():
                    col1.html(
                        html_code
                    )
            else:
                with st.container():
                    col2.html(
                        html_code
                    )
                
        
        # st.write(deputados)
    
    def despesa_deputado_individual_detalhado(self, id_deputado):
        col_titulo, col_botao = st.columns([6,1])
        col_titulo.subheader('Despesas por deputado individual')
        
        # st.write(id_deputado)
        
        if col_botao.button(label='Voltar', key='voltar'):
            self.limpar_parametros()
            st.rerun()
        
        with st.spinner('Aguarde um momento...'):
            dep = self.processar.detalhe_deputado(int(id_deputado))
        # st.write(dep)
        buscar_conjunto_uf = self.processar.processar_dados_deputados(dep['siglaUF'])
        df_dep = buscar_conjunto_uf.query('id == @id_deputado').copy()
        df_dep['periodo'] = df_dep['ano'].astype(str) + '-' + df_dep['mes'].astype(str)
        # st.write(df_dep)
        
        nome = df_dep['nome'].iloc[0]
        link = df_dep['link'].iloc[0]
        link_imagem = f'https://www.camara.leg.br/internet/deputado/bandep/{id_deputado}.jpgmaior.jpg'
        partido = df_dep['siglaPartido'].iloc[0]
        estado = df_dep['siglaUF'].iloc[0]
        
        with st.container():
            col1, col2 = st.columns([1,2])
            col1.html(f'''
                <img src={link_imagem} width=140 height=190 style="cursor: pointer">
                ''')
            col2.html(
                f'<br><br><h2>{nome}<br>'
            )
        
        col1, col2 = st.columns(2)
        
        resumo_por_periodo = df_dep.groupby('periodo')[['valor']].sum().reset_index()
        resumo_por_periodo['valor_formatado'] = resumo_por_periodo['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
        
        fig_periodo = px.bar(
            data_frame=resumo_por_periodo,
            x='periodo',
            y='valor',
            custom_data=['valor_formatado'],
        )
        
        fig_periodo.update_traces(
            hovertemplate='<b>Período:</b>%{x}<br><b>Valor:</b>%{customdata[0]}',
            hoverlabel=dict(
                # bgcolor='white',
                font=dict(size=14),
            ),
        )
        
        fig_periodo.update_layout(
            xaxis_tickformat='%b, %Y',
            title='Despesas por período',
            title_font=dict(size=26, color='black', family='Arial'),
            title_x=.40
        )
        
        col1.plotly_chart(fig_periodo, use_container_width=True)
        
        resumo_por_descricao = df_dep.groupby('descricao')[['valor']].sum().reset_index()
        resumo_por_descricao['valor_formatado'] = resumo_por_descricao['valor'].apply(lambda x: format_currency(number=x, currency='BRL', locale='pt_BR'))
        
        fig_descricao = px.bar(
            data_frame=resumo_por_descricao,
            y='descricao',
            x='valor',
            custom_data=['valor_formatado'],
            orientation='h'
        )
        
        fig_descricao.update_traces(
            hovertemplate='<b>Despesa:</b>%{x}<br><b>Valor:</b>%{customdata[0]}',
            hoverlabel=dict(
                # bgcolor='white',
                font=dict(size=14),
            ),
        )
        
        fig_descricao.update_layout(
            xaxis_tickformat='%b, %Y',
            title='Despesas por despesa',
            title_font=dict(size=26, color='black', family='Arial'),
            title_x=.40
        )
        
        col2.plotly_chart(fig_descricao, use_container_width=True)
    
    def run(self):
        st.set_page_config(layout='wide')
        id_deputado = self.parametros_id_deputados()
        st.title('Despesas Parlamentares')
        
        if not id_deputado:
            tab1, tab2, tab3 = st.tabs(['Despesa geral', 'Despesa por estado detalhado', 'Despesa deputado detalhado'])
            with tab1:
                self.despesa_geral() # este aparentemente está completo com o que foi idealizado a ele retornar
            with tab2:
                self.despesa_estado_detalhado()
            with tab3:
                self.despesa_deputado_individual()
        else:
            self.despesa_deputado_individual_detalhado(id_deputado)

app = UI()
app.run()
