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
        # --- AJUSTE DE FORMATO ---
        # Converte o preço para o formato R$ 0,00
        df['preco_formatado'] = df['preco'].apply(lambda x: f"R$ {x:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))
        
        # Criar colunas para organizar o visual
        for index, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['produto']}**")
                with col2:
                    st.write(f"**{row['preco_formatado']}**")
                with col3:
                    st.caption(f"{row['mercado']} ({row['bairro']})")
                st.divider()
    else:
        st.info("O robô ainda não enviou ofertas hoje. Rode o coletor.py!")
except Exception as e:
    st.error(f"Erro ao conectar com o banco: {e}")
