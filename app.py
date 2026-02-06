import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

# Inicializa Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- INTERFACE ---
st.title("📍 Economiza Maricá")
st.markdown("---")

# Barra Lateral com Carrinho e Propaganda
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_lista = 0
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} ({item['mercado']})")
        st.divider()
        st.metric("Total", f"R$ {total_lista:,.2f}")
    
    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nOs melhores perfumes árabes de Maricá!")

# Exibição dos Produtos
if not df.empty:
    busca = st.text_input("🔍 O que você procura em Maricá?", placeholder="Ex: Arroz, Feijão, Alcatra...")
    df_f = df[df['produto'].str.contains(busca, case=False)] if busca else df
    
    for _, row in df_f.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.5, 1.2])
            c1.markdown(f"**{row['produto']}**\n\n🏪 {row['mercado']} | 📍 {row['bairro']}")
            c2.subheader(f"R$ {row['preco']:,.2f}")
            if c3.button("🛒", key=f"b_{row['id']}"):
                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                st.rerun()
else:
    st.warning("⚠️ O robô está enviando os preços... Atualize a página em 1 minuto!")
