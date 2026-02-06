import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO CSS (Focado em Compactação e Comparação) ---
st.markdown("""
    <style>
    .prop-box {background-color: #f8f9fa; padding: 10px; text-align: center; border: 1.5px dashed #bbb; border-radius: 8px; margin-bottom: 15px; color: #555; font-size: 0.9em; font-weight: bold;}
    .card-produto {border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: white;}
    .nome-prod {font-size: 1.05em !important; font-weight: bold; color: #2c3e50; margin-bottom: 8px; border-bottom: 2px solid #3498db; display: inline-block;}
    .item-mercado {padding: 6px 0; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.1em; min-width: 90px; display: inline-block;}
    .nome-mercado {font-weight: 600; font-size: 0.95em; color: #444;}
    .bairro-info {font-size: 0.8em; color: #888;}
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            # Remove duplicados exatos para não poluir
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- PROPAGANDA SUPERIOR ---
st.markdown('<div class="prop-box">📢 FAÇA SUA PROPAGANDA AQUI - CONTATO: (21) 9XXXX-XXXX</div>', unsafe_allow_html=True)

# --- FILTROS ---
c_busca, c_local = st.columns([2, 1])
with c_busca:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz, Leite...")
with c_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Região", bairros)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.info("Lista vazia")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            total += item['preco'] * item['qtd']
            st.write(f"**{item['qtd']}x** {item['nome']}")
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
    
    st.markdown("---")
    st.markdown('<div class="prop-box">FAÇA SUA PROPAGANDA AQUI</div>', unsafe_allow_html=True)
    st.markdown('<div class="prop-box">FAÇA SUA PROPAGANDA AQUI</div>', unsafe_allow_html=True)

# --- EXIBIÇÃO TIPO ESCADA ---
if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_sel]

    # Agrupa por produto para criar a "Escada"
    produtos = df_f['produto'].unique()
    
    for p in produtos:
        # Pega todas as redes que têm esse produto e ordena pelo menor preço
        ofertas = df_f[df_f['produto'] == p].sort_values(by='preco')
        
        with st.container():
            st.markdown(f'<div class="card-produto"><div class="nome-prod">{p}</div>', unsafe_allow_html=True)
            
            for _, row in ofertas.iterrows():
                # Layout de linha compacta para comparação rápida
                col1, col2, col3, col4 = st.columns([2.5, 1.2, 0.8, 0.5])
                with col1:
                    st.markdown(f'<span class="nome-mercado">🏪 {row["mercado"]}</span> <br> <span class="bairro-info">📍 {row["bairro"]}</span>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                with col3:
                    qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{row['id']}", label_visibility="collapsed")
                with col4:
                    if st.button("🛒", key=f"b_{row['id']}"):
                        st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Aguardando dados dos encartes...")
