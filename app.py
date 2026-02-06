import streamlit as st
import pandas as pd
from supabase import create_client

# Conexão
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="🛒")

st.title("📍 Economiza Maricá")
st.subheader("O robô IA pesquisa, você economiza!")

# Puxar dados do banco
try:
    response = supabase.table("ofertas").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Filtros básicos
        bairro = st.sidebar.selectbox("Escolha o Bairro", df['bairro'].unique())
        dados_filtrados = df[df['bairro'] == bairro]
        st.table(dados_filtrados[['produto', 'preco', 'mercado', 'setor']])
    else:
        st.info("O robô ainda não enviou ofertas hoje. Rode o coletor.py!")
except Exception as e:
    st.error(f"Erro ao conectar com o banco: {e}")