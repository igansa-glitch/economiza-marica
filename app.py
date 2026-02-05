import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURAÇÕES DE CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="🛒", layout="wide")

# --- INICIALIZAÇÃO DO CARRINHO (MEMÓRIA) ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILIZAÇÃO CSS PARA O CARRINHO FLUTUANTE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; }
    .carrinho-total { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("📍 Economiza Maricá")
st.markdown("### O robô IA pesquisa, você economiza!")
st.divider()

# --- BARRA LATERAL (CARRINHO DE COMPRAS) ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Seu carrinho está vazio.")
    else:
        total_geral = 0
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_geral += subtotal
            col_item, col_btn = st.columns([4, 1])
            with col_item:
                st.write(f"**{item['qtd']}x** {item['nome']}")
                st.caption(f"Subtotal: R$ {subtotal:,.2f}")
            with col_btn:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.carrinho.pop(i)
                    st.rerun()
        
        st.divider()
        st.markdown(f"### Total: R$ {total_geral:,.2f}")
        if st.button("Limpar Lista"):
            st.session_state.carrinho = []
            st.rerun()

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=600)
def buscar_dados():
    try:
        response = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

df = buscar_dados()

if not df.empty:
    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            df_setor = df[df['setor'] == setor]
            if not df_setor.empty:
                for _, row in df_setor.iterrows():
                    preco_formatado = f"R$ {row['preco']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                    
                    with st.container():
                        col_prod, col_info, col_acao = st.columns([3, 2, 1.5])
                        
                        with col_prod:
                            st.markdown(f"#### {row['produto']}")
                            st.caption(f"🏪 **{row['mercado']}** | 📍 {row['bairro']}, Maricá - RJ")
                        
                        with col_info:
                            st.markdown(f"## {preco_formatado}")
                        
                        with col_acao:
                            qtd = st.number_input("Qtd/Kg", min_value=1, max_value=50, value=1, key=f"q_{row['id']}")
                            if st.button("Adicionar", key=f"add_{row['id']}"):
                                st.session_state.carrinho.append({
                                    "nome": row['produto'],
                                    "preco": row['preco'],
                                    "qtd": qtd
                                })
                                st.toast(f"{row['produto']} adicionado!")
                                st.rerun()
                        st.divider()
            else:
                st.info(f"Sem ofertas de {setor} agora.")
else:
    st.warning("Aguardando o robô coletar os preços...")

            


