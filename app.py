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

# --- ESTILO CSS PERSONALIZADO (Fontes menores e Layout Compacto) ---
st.markdown("""
    <style>
    .prop-banner-top {background-color: #f1f1f1; padding: 10px; text-align: center; border: 2px dashed #ccc; border-radius: 8px; margin-bottom: 15px; color: #666; font-weight: bold;}
    .card-produto {border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 8px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);}
    .nome-produto {font-size: 1.1em !important; font-weight: bold; margin-bottom: 5px; color: #333;}
    .linha-mercado {font-size: 0.9em; padding: 5px 0; border-top: 1px solid #eee;}
    .preco-valor {color: #28a745; font-weight: bold; font-size: 1.1em;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {height: 40px; white-space: pre-wrap; font-size: 0.9em;}
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- 1. PROPAGANDA SUPERIOR (BANNER ÚNICO) ---
st.markdown('<div class="prop-banner-top">📢 ANUNCIE AQUI - (21) 9XXXX-XXXX</div>', unsafe_allow_html=True)

# --- 2. FILTROS DE TOPO ---
col_busca, col_local = st.columns([2, 1])
with col_busca:
    busca = st.text_input("🔍 Buscar item...", placeholder="Ex: Alcatra, Leite, Omo...")
with col_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "Maricá", "Ponta Negra"]
    bairro_selecionado = st.selectbox("📍 Região", bairros)

# --- BARRA LATERAL (CARRINHO E JANELA DE PROPAGANDA) ---
with st.sidebar:
    st.header("🛒 Sua Lista")
    if not st.session_state.carrinho:
        st.info("Vazia")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total", f"R$ {total:,.2f}")
        st.button("📲 Compartilhar Lista")
    
    st.markdown("---")
    # Janelas de Propaganda Lateral
    st.markdown('<div class="prop-banner-top">FAÇA SUA PROPAGANDA AQUI</div>', unsafe_allow_html=True)
    st.markdown('<div class="prop-banner-top">FAÇA SUA PROPAGANDA AQUI</div>', unsafe_allow_html=True)

# --- 3. EXIBIÇÃO ---
if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_selecionado != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_selecionado]

    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            # (Aqui você pode adicionar a lógica de filtro por setor se desejar)
            prods = df_f['produto'].unique()
            for p in prods:
                ofertas = df_f[df_f['produto'] == p].sort_values(by='preco')
                
                with st.container():
                    st.markdown(f'<div class="card-produto"><div class="nome-produto">{p}</div>', unsafe_allow_html=True)
                    for _, row in ofertas.iterrows():
                        c1, c2, c3, c4 = st.columns([2, 1, 0.8, 0.6])
                        with c1:
                            st.write(f"🏪 **{row['mercado']}**")
                            st.caption(f"📍 {row['bairro']}")
                        with c2:
                            st.markdown(f'<span class="preco-valor">R$ {row['preco']:,.2f}</span>', unsafe_allow_html=True)
                        with c3:
                            qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{row['id']}")
                        with c4:
                            if st.button("🛒", key=f"b_{row['id']}"):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Aguardando dados...")
