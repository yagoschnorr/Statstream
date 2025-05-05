import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def plot_graph(df, chart_type):
    fig, ax = plt.subplots()
    code = ""

    if chart_type == "Scatterplot":
        cols = st.multiselect("Escolha duas colunas numéricas", df.select_dtypes(include=['number']).columns, default=df.select_dtypes(include=['number']).columns[:2])
        if len(cols) == 2:
            sns.scatterplot(x=df[cols[0]], y=df[cols[1]], ax=ax)
            code = f"""
import seaborn as sns
import matplotlib.pyplot as plt
sns.scatterplot(x=df['{cols[0]}'], y=df['{cols[1]}'])
plt.show()
"""
    
    elif chart_type == "Barplot":
        col_x = st.selectbox("Escolha a coluna para o eixo X", df.columns)
        col_y = st.selectbox("Escolha a coluna para o eixo Y", df.select_dtypes(include=['number']).columns)
        if col_x and col_y:
            sns.barplot(x=df[col_x], y=df[col_y], ax=ax)
            plt.xticks(rotation=45)
            code = f"""
import seaborn as sns
import matplotlib.pyplot as plt
sns.barplot(x=df['{col_x}'], y=df['{col_y}'])
plt.xticks(rotation=45)
plt.show()
"""
    
    elif chart_type == "Boxplot":
        cols = st.multiselect("Escolha colunas numéricas para visualizar", df.select_dtypes(include=['number']).columns)
        if cols:
            sns.boxplot(data=df[cols], ax=ax)
            code = f"""
import seaborn as sns
import matplotlib.pyplot as plt
sns.boxplot(data=df[{cols}])
plt.show()
"""
            
    elif chart_type == "Lineplot":
        cols = st.multiselect("Escolha colunas numéricas para visualizar", df.select_dtypes(include=['number']).columns)
        if cols:
            sns.lineplot(data=df[cols], ax=ax)
            code = f"""
import seaborn as sns
import matplotlib.pyplot as plt
sns.lineplot(data=df[{cols}])
plt.show()
"""
    
    st.pyplot(fig)
    st.code(code, language='python')

def add_graph_section(df):
    st.write("## Seção de Gráficos")
    plot_graph(df)
