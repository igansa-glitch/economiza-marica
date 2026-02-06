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

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .main-header {text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 20px;}
    .prop-banner {background: linear-gradient(90deg, #FFD700, #FFA500); padding: 15px; text-align: center; border-radius: 10px; font-weight: bold; margin-bottom: 20px; color: black;}
    .card-produto {border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px; background-color: white;}
    .linha-mercado {display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee;}
    .preco-destaque {color: #28a745; font-weight: bold; font-size: 1.2em;}
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
            # Classificação interna de setores
            def classificar(p):
                p = p.lower()
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha']): return "Açougue"
                if any(x in p for x in ['arroz', 'feijão', 'óleo', 'café']): return "Mercearia"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'água']): return "Bebidas"
                return "Outros"
            df_temp['setor'] = df_temp['produto'].apply(classificar)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- 1. PROPAGANDA SUPERIOR ---
st.markdown("""
    <div class="prop-banner">
        🛍️ DANIPARFUN.COM.BR - Os Melhores Perfumes Árabes em Maricá! <br>
        <span style="font-size: 0.8em;">Use o cupom: MARICA5 e ganhe desconto</span>
    </div>
    """, unsafe_allow_html=True)

# --- 2. FILTROS DE TOPO (ACESSIBILIDADE) ---
col_busca, col_local = st.columns([2, 1])
with col_busca:
    busca = st.text_input("🔍 O que você quer comprar hoje?", placeholder="Ex: Arroz, Picanha...")
with col_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "Ponta Negra", "São José"]
    bairro_selecionado = st.selectbox("📍 Filtrar por Região", bairros)

# --- BARRA LATERAL (CARRINHO) ---
with st.sidebar:
    st.header("🛒 Sua Lista")
    if not st.session_state.carrinho:
        st.info("Sua lista está vazia.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {sub:,.2f} no {item['mercado']}")
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total", f"R$ {total:,.2f}")
        if st.button("Enviar para WhatsApp"):
            st.success("Lista enviada!")

# --- 3. EXIBIÇÃO EM CARDS DE COMPARAÇÃO ---
if not df.empty:
    # Filtros
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_selecionado != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_selecionado]

    # Agrupamento para Comparação Rápida
    produtos_unicos = df_f['produto'].unique()
    
    for prod in produtos_unicos:
        ofertas = df_f[df_f['produto'] == prod].sort_values(by='preco')
        
        with st.container():
            st.markdown(f"""<div class="card-produto"><h3>{prod}</h3>""", unsafe_allow_html=True)
            
            # Mostra cada mercado lado a lado ou em lista compacta
            for _, row in ofertas.iterrows():
                col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
                with col1:
                    st.write(f"🏪 **{row['mercado']}**")
                    st.caption(f"📍 {row['bairro']}")
                with col2:
                    st.markdown(f"""<span class="preco-destaque">R$ {row['preco']:,.2f}</span>""", unsafe_allow_html=True)
                with col3:
                    qtd = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                with col4:
                    if st.button("🛒", key=f"b_{row['id']}"):
                        st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                        st.toast("Adicionado!")
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("Aguardando dados do coletor...")
