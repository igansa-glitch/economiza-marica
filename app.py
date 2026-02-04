import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração visual
st.set_page_config(page_title="Economiza Maricá", page_icon="📍")

st.markdown("<h1 style='text-align: center; color: #27ae60;'>📍 Economiza Maricá</h1>", unsafe_allow_html=True)

# Dados de Exemplo para o Teste
data = {
    'Produto': ['Alcatra kg', 'Alcatra kg', 'Arroz 5kg', 'Arroz 5kg'],
    'Mercado': ['Grand Marché', 'Rede Economia', 'Grand Marché', 'Princesa'],
    'Preço': [37.90, 41.50, 28.50, 26.90],
    'Bairro': ['Centro', 'Inoã', 'Centro', 'Itaipuaçu'],
    'Setor': ['Açougue', 'Açougue', 'Mercearia', 'Mercearia']
}
df = pd.DataFrame(data)

# Interface
bairro = st.selectbox("Sua região em Maricá:", ["Centro", "Itaipuaçu", "Inoã"])
st.write(f"### Melhores ofertas em {bairro}")
st.dataframe(df[df['Bairro'] == bairro])

st.success("App em modo de teste. O Agente de IA está simulando os dados.")