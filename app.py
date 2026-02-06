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

# --- ESTILO CSS (Compacto e Profissional) ---
st.markdown("""
    <style>
    .prop-box {background-color: #f8f9fa; padding: 12px; text-align: center; border: 2px dashed #007bff; border-radius: 8px; margin-bottom: 15px; color: #333; font-size: 0.95em;}
    .whats-link {color: #25d366; font-weight: bold; text-decoration: none; font-size: 1.1em;}
    .card-produto {border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.03);}
    .nome-prod {font-size: 1.05em !important; font-weight: bold; color: #2c3e50; margin-bottom: 8px; border-bottom: 2px solid #007bff; display: inline-block;}
    .item-mercado {padding: 6px 0; border-bottom: 1px solid #f0f0f0;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.15em;}
    .nome-mercado {font-weight: 600; font-size: 0.95em; color: #444;}
    .bairro-info {font-size: 0.8em; color: #888; margin-left: 5px;}
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

# --- 1. PROPAGANDA SUPERIOR COM SEU CONTATO ---
st.markdown(f"""
    <div class="prop-box">
        📢 <b>FAÇA SUA PROPAGANDA AQUI</b><br>
        Contato: (21) 98288-1425<br>
        <a href="https://wa.me/5521982881425" class="whats-link">WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# --- FILTROS ---
c_busca, c_local = st.columns([2, 1])
with c_busca:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz, Cerveja...")
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
    # Janelas de Propaganda Lateral com seu contato
    for _ in range(2):
        st.markdown(f"""
            <div class="prop-box">
                <b>FAÇA SUA PROPAGANDA AQUI</b><br>
                (21) 98288-1425<br>
                <span style="color:#25d366; font-size:0.8em;">WhatsApp</span>
            </div>
            """, unsafe_allow_html=True)

# --- EXIBIÇÃO EM ESCADA (MERCADOS UM ABAIXO DO OUTRO) ---
if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_sel]

    # Lista de Setores para as Abas
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            # Filtro simples de setor por palavra-chave se necessário
            prods = df_f['produto'].unique()
            for p in prods:
                # Pega as redes para este produto e ordena do menor para o maior preço
                ofertas = df_f[df_f['produto'] == p].sort_values(by='preco')
                
                with st.container():
                    st.markdown(f'<div class="card-produto"><div class="nome-prod">{p}</div>', unsafe_allow_html=True)
                    
                    for _, row in ofertas.iterrows():
                        # Layout de linha para comparação rápida
                        c1, c2, c3, c4 = st.columns([2.5, 1.2, 0.8, 0.5])
                        with c1:
                            st.markdown(f'<span class="nome-mercado">🏪 {row["mercado"]}</span><span class="bairro-info">({row["bairro"]})</span>', unsafe_allow_html=True)
                        with c2:
                            st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                        with c3:
                            qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{nome_setor}_{row['id']}", label_visibility="collapsed")
                        with c4:
                            if st.button("🛒", key=f"b_{nome_setor}_{row['id']}"):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("🤖 Aguardando novos dados do robô...")
