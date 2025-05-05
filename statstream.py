import pandas as pd
import streamlit as st
import requests
import re
import io
import gspread
from google.oauth2.service_account import Credentials
from graphs import plot_graph

st.set_page_config(page_title='Statstream', page_icon='📊', layout='wide')

def main():
    nav_bar = st.sidebar
    nav_bar.image('logo_cesupa.png')
    nav_bar.divider()
    nav_bar.title('StatStream 📚')
    options = ['Início', 'Dinâmica', 'Questões', 'Links externos']
    choice = nav_bar.radio('Barra de navegação', options=options)

    if choice == 'Início':
        with st.columns([1,3,1])[1]:
            welcome_page()
    elif choice == 'Dinâmica':
        with st.columns([1,3,1])[1]:
            run_dynamic()
    elif choice == 'Questões':
        with st.columns([1,3,1])[1]:    
            questions()
    elif choice == 'Links externos':
        with st.columns([1,3,1])[1]:
            external_links()

def welcome_page():
    st.title('Bem vindo ao StatStream!')

    st.write(''' 
        O StatStream é um aplicativo desenvolvido por meio da biblioteca Streamlit para auxiliar os alunos do terceiro 
        semestre do curso de ciência da computação do CESUPA (Centro Universitário do Estado do Pará) na aplicação e compreensão 
        de conceitos estatísticos.
    ''')

    st.divider()

    st.write('''
        ### Objetivo: 
        O objetivo principal é oferecer uma plataforma interativa onde, a partir da dinâmica sugerida, os usuários poderão:
        - Compreender os conceitos estatísticos
        - Realizar exercícios
        - Entender a aplicação do conteúdo utilizando Python
        - Gerar insights estatísticos
        - Desenvolver habilidades práticas
    ''')

    st.divider()

    url = 'https://raw.githubusercontent.com/yagoschnorr/Statstream/refs/heads/main/area_do_professor/ementa.md'

    response = requests.get(url)
    if response.status_code == 200:
        markdown_content = response.text

    try:
        st.markdown(markdown_content, unsafe_allow_html=True)
    except:
        st.error('Algo deu errado na leitura do markdown da ementa!')

    st.divider()

    st.write('''
        ### Autores:
        - Yago Patrick Schnorr Pinto 
        - Bruno Kalel Ribeiro da Silva
        - Adib Said Cavaleiro de Macedo Aboul Hosn
        - Marco Antônio Mora Estrada Filho
        - Pedro Henrique Sales Girotto
    ''')

def run_dynamic():
    if "df" not in st.session_state:
        file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
        
        if file is not None:
            df = pd.read_csv(file)
            st.session_state.df = df
            st.session_state.df_original = df.copy()
            st.rerun()
    else:
        col1, col2, col3, col4 = st.columns([3,2,2,3])

        with col2:
            if st.button('Trocar dataset'):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col3:        
            if st.button('resetar dataset'):
                st.session_state.df = st.session_state.df_original
                st.rerun()

        teste = st.session_state.df
        df = teste.copy()   

        st.write("### -> Visualização completa do DataFrame")
        st.dataframe(df, height=200, width=850)

        st.write('- #### Valores únicos:')

        unique_values = pd.DataFrame({'Colunas': df.columns,
                                      'Valores únicos': [", ".join(map(str, df[col].unique().tolist())) for col in df.columns]})
        
        st.dataframe(unique_values, width=850, height=200, hide_index=True)

        st.write('- #### Valores nulos e tipos de dado:')

        info = pd.DataFrame({'Colunas': df.columns,
                             'Valores nulos': df.isnull().sum(),
                             'Tipos de dados': df.dtypes.astype(str)})
        
        st.dataframe(info, width=850, height=200, hide_index=True)

        st.divider()

        st.write('### Tratamento da tabela')

        ### Modificando valores únicos errados
        st.write('- ##### Modificando valores únicos:')

        coluna_modificar_valores_unicos = st.multiselect('Em quais colunas você deseja substituir valores únicos?', options=df.columns)

        for i in range(len(coluna_modificar_valores_unicos)):
            tipo_coluna = df[coluna_modificar_valores_unicos[i]].dtype
            valor_antigo = st.text_input(f'Digite o valor antigo que você deseja modificar da coluna {coluna_modificar_valores_unicos[i]}:', placeholder='Exemplo de formatação: exemplo1, exemplo2').strip().split(', ')
            valor_novo = st.text_input(f'Digite o valor para qual você deseja modificar da coluna {coluna_modificar_valores_unicos[i]}:', placeholder='Exemplo de formatação: exemplo1, exemplo2').strip().split(', ')

            if valor_antigo[0] != '' and valor_novo[0] != '':
                if tipo_coluna != 'object':
                    if tipo_coluna == 'int64':
                        valor_antigo = list(map(int, valor_antigo))
                        valor_novo = list(map(int, valor_novo))
                    elif tipo_coluna == 'float64':
                        valor_antigo = list(map(float, valor_antigo))
                        valor_novo = list(map(float, valor_novo))
                    elif tipo_coluna == 'bool':
                        valor_antigo = list(map(bool, valor_antigo))
                        valor_novo = list(map(bool, valor_novo))

                try:
                    df[coluna_modificar_valores_unicos[i]] = df[coluna_modificar_valores_unicos[i]].replace(valor_antigo, valor_novo) 
                except:
                    st.error('Você inseriu um número diferente de palavras!')

        ### Mudando o nome das colunas
        st.write('- ##### Mudando o nome das colunas:')

        escolha_mudar_coluna = st.multiselect('Quais colunas você deseja trocar o nome?', options=df.columns)

        for i in range(len(escolha_mudar_coluna)):
            nova_coluna = st.text_input(f'Digite o novo nome para a coluna {escolha_mudar_coluna[i]}: ').strip()
            if nova_coluna != '':
                df.rename(columns={escolha_mudar_coluna[i]: nova_coluna}, inplace=True)

        ### Tratamento de valores nulos
        if df.isnull().sum().sum() > 0:
            st.write('- ##### Lidando com valores nulos:')

            colunas_com_nulos = [col for col in df.columns if df[col].isnull().sum() > 0]

            st.write(f'Você possui {len(colunas_com_nulos)} colunas com valores nulos no seu dataframe, o que deseja fazer com eles?')

            opcoes_tratamento_nulos = ['', 'Remover linhas com valores nulos', 'Preencher com algo os valores nulos', 'Preencher com a média da coluna', 'Preencher com a mediana da coluna', 'Preencher com a moda da coluna']
            for i in range(len(colunas_com_nulos)):
                escolha_tratar_nulo = st.selectbox(f'Escolha a opçõa que voce deseja para tratar a coluna {colunas_com_nulos[i]}', options=opcoes_tratamento_nulos)
                try:
                    if escolha_tratar_nulo == 'Remover linhas com valores nulos':
                        df.dropna(subset=[colunas_com_nulos[i]], inplace=True)
                    elif escolha_tratar_nulo == 'Preencher com algo os valores nulos':
                        preencher = st.text_input('Com o que você deseja preencher os valores nulos?')
                        df[colunas_com_nulos[i]] = df[colunas_com_nulos[i]].fillna(preencher)
                    elif escolha_tratar_nulo == 'Preencher com a média da coluna':
                        df[colunas_com_nulos[i]] = df[colunas_com_nulos[i]].fillna(df[colunas_com_nulos[i]].mean())
                    elif escolha_tratar_nulo == 'Preencher com a mediana da coluna':
                        df[colunas_com_nulos[i]] = df[colunas_com_nulos[i]].fillna(df[colunas_com_nulos[i]].median())
                    elif escolha_tratar_nulo == 'Preencher com a moda da coluna':
                        df[colunas_com_nulos[i]] = df[colunas_com_nulos[i]].fillna(df[colunas_com_nulos[i]].mode()[0])        
                except:
                    st.error(f'Você não pode {escolha_tratar_nulo} na coluna {colunas_com_nulos[i]}') # dar uma olhada no que posso escrever melhor aqui

        ### Alterando tipo de dados
        st.write('- ##### Alterando tipo de dados:')

        escolhas_alterar_tipo = st.multiselect('Insira a coluna que você deseja alterar:', options=df.columns)

        opcoes_alterar_tipo = ['', 'Inteiro', 'Float', 'String', 'Booleano', 'Datetime']
        for i in range(len(escolhas_alterar_tipo)):
            tipo = st.selectbox(f'Voce deseja alterar a coluna {escolhas_alterar_tipo[i]} do tipo {df[escolhas_alterar_tipo[i]].dtypes} para qual tipo? ', options=opcoes_alterar_tipo)
            try:
                if tipo == 'Inteiro':
                    df[escolhas_alterar_tipo[i]] = df[escolhas_alterar_tipo[i]].astype(int)
                elif tipo == 'Float':
                    df[escolhas_alterar_tipo[i]] = df[escolhas_alterar_tipo[i]].astype(float)
                elif tipo == 'String':
                    df[escolhas_alterar_tipo[i]] = df[escolhas_alterar_tipo[i]].astype(str)
                elif tipo == 'Booleano':
                    df[escolhas_alterar_tipo[i]] = df[escolhas_alterar_tipo[i]].astype(bool)
                elif tipo == 'Datetime':
                    df[escolhas_alterar_tipo[i]] = pd.to_datetime(df[escolhas_alterar_tipo[i]])
            except:
                st.error(f'A coluna {escolhas_alterar_tipo[i]} não pode ser alterada para o tipo {tipo}.')

        ### Excluir uma coluna da tabela
        st.write('- ##### Excluindo colunas:')

        excluir = st.multiselect('Escolha as colunas que deseja excluir caso queira excluir alguma:', options=df.columns)
        df.drop(columns=excluir, inplace=True)

        with st.columns([3,2,3])[1]:
            if st.button('finalizar tratamento'):
                st.session_state.df = df
                st.rerun()

        with st.sidebar:
            st.download_button(label='Baixe o dataframe aqui!', data=st.session_state.df.to_csv(index=False), file_name=f'dataframe_tratado.csv', mime='csv')

        st.divider()

        st.write('## Plotagem de gráficos')
        
        chart_type = st.selectbox("Escolha o tipo de gráfico", ["Scatterplot", "Barplot", "Boxplot", "Lineplot"])
        plot_graph(df, chart_type)

def questions():
    url = 'https://raw.githubusercontent.com/yagoschnorr/Statstream/refs/heads/main/area_do_professor/questoes.md'
    response = requests.get(url)

    if response.status_code == 200:
        markdown_content = response.text

    try:
        interpolating_answer_box(markdown_content)
    except:
        st.error('Algo deu errado na leitura do markdown!')

def interpolating_answer_box(md):
    parts = re.split(r'(\[resposta\]|\[nome\])', md)

    answers = []
    question = 1
    number_of_questions = 1 

    for part in parts:
        if part == '[resposta]':
            number_of_questions += 1

    for part in parts:
        if part == '[nome]':
            key = 'nome'

            if 'nome' not in st.session_state:
                st.session_state.nome = ''

            st.session_state[key] = st.text_input(' ', value=st.session_state[key])
            answers.insert(0, st.session_state[key])

        elif part == '[resposta]':
            key = f'resposta_{question}'

            for i in range(1, number_of_questions):
                if f'resposta_{i}' not in st.session_state:
                    st.session_state[f'resposta_{i}'] = ''

            st.session_state[key] = st.text_input(f'Digite a resposta da questão {question} aqui:', value = st.session_state[key])
            answers.append(st.session_state[key])

            question += 1
        else:
            st.markdown(part)

    if answers:
        df_answers = pd.DataFrame([answers], columns=['Nome' if i == 0 else f'Resposta {i+1}' for i in range(len(answers))])

        csv_buffer = io.StringIO()
        df_answers.to_csv(csv_buffer, index=False)

        with st.sidebar:
            st.download_button(label='Baixe suas respostas aqui!', data=csv_buffer.getvalue(), file_name='respostas.csv', mime='text/csv')

        sent = False
        sending_error = False
        name_error = False
        with st.columns([3,2,3])[1]:
            if st.button('Enviar respostas!'):
                try:
                    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                    cred = Credentials.from_service_account_info(st.secrets['gcp_service_account'], scopes=scope)
                    client = gspread.authorize(cred)
                    sheet = client.open('statstream').sheet1

                    names = [line[0].replace(' ', '').strip().lower() for line in sheet.get_all_values() if line]

                    if answers[0].replace(' ', '').strip().lower() in names:
                        name_error = True
                    else:
                        sheet.append_row(answers)
                        sent = True
                except Exception as e:
                    st.write(e)
                    sending_error = True

        if sent == True:
            st.success('Respostas enviadas com sucesso!', icon='🚀')
        if sending_error == True:
            st.error('Ocorreu um erro ao enviar as respostas!', icon='🚨')
        if name_error == True:
            st.error('Você já enviou uma resposta anteriormente!', icon='🚨')

def external_links():
    url = 'https://raw.githubusercontent.com/yagoschnorr/Statstream/refs/heads/main/area_do_professor/linksExternos.md'

    response = requests.get(url)
    if response.status_code == 200:
        markdown_content = response.text

    try:
        st.markdown(markdown_content, unsafe_allow_html=True)
    except:
        st.error('Algo deu errado na leitura do markdown!')

if __name__ == '__main__':
    main()