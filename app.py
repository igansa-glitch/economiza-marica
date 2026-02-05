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
    # Formata a coluna de preço para exibir como dinheiro
    df['preco'] = df['preco'].apply(lambda x: f"R$ {x:,.2f}".replace('.', ','))
    
    st.dataframe(df[['produto', 'preco', 'mercado', 'bairro', 'setor']], use_container_width=True)
    else:
        st.info("O robô ainda não enviou ofertas hoje. Rode o coletor.py!")
except Exception as e:

    st.error(f"Erro ao conectar com o banco: {e}")
