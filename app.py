import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO CSS ANALÍTICO (Foco em Dispositivos Móveis) ---
st.markdown("""
    <style>
    .stApp {background-color: #f8f9fa;}
    /* Propaganda mais compacta */
    .prop-box {background-color: #ffffff; padding: 8px; text-align: center; border: 2px dashed #007bff; border-radius: 8px; margin-bottom: 10px; font-size: 0.85em;}
    /* Cards de produto mais finos para caber mais na tela */
    .card-produto {border-left: 4px solid #007bff; border-radius: 6px; padding: 10px; margin-bottom: 8px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
    .nome-prod {font-size: 0.9em !important; font-weight: bold; color: #333; text-transform: uppercase; margin-bottom: 5px; display: block;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.1em;}
    .nome-mercado {font-size: 0.85em; font-weight: 600; color: #444;}
    /* Ajuste de abas para não quebrar no celular */
    .stTabs [data-baseweb="tab"] {padding: 10px 12px; font-size: 0.85em;}
    </style>
    """, unsafe_allow_html=True)

# --- FILTRO DE QUALIDADE DE DADOS ---
def validar_produto(nome):
    n = str(nome).upper().strip()
    # Bloqueia lixo comum do OCR
    bloqueados = [';', ':', '%', '!', '?', 'ICOA', 'PACV', 'FC1', '28,8', '7,99']
    if any(x in n for x in bloqueados) or len(n) < 4 or n.replace(',','').isdigit():
        return None
    return n

# --- FILTRO DE QUALIDADE DE DADOS (REFORÇADO) ---
def validar_entrada(row):
    # 1. Limpeza do Nome do Produto
    n = str(row.get('produto', '')).upper().strip()
    mercado = str(row.get('mercado', '')).upper().strip()
    
    # Bloqueia "Mercado Local" ou nomes genéricos que a IA inventa
    mercados_bloqueados = ['MERCADO LOCAL', 'LOCAL', 'COMÉRCIO', 'LOJA']
    if any(m in mercado for m in mercados_bloqueados):
        return None
    
    # Bloqueia lixo comum do OCR no nome do produto
    bloqueados_prod = [';', ':', '%', '!', '?', 'ICOA', 'PACV', 'FC1', '28,8', '7,99']
    if any(x in n for x in bloqueados_prod) or len(n) < 4 or n.replace(',','').isdigit():
        return None
        
    return n

# --- CARREGAMENTO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            # Aplica a validação cruzada (Produto + Mercado)
            df_temp['produto_limpo'] = df_temp.apply(validar_entrada, axis=1)
            
            # Remove o que foi invalidado
            df_temp = df_temp.dropna(subset=['produto_limpo'])
            df_temp['produto'] = df_temp['produto_limpo']
            
            # Remove duplicados
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            
            def categorizar(p):
                p = p.lower()
                # Mercearia Reforçada (Arroz, Feijão, etc)
                if any(x in p for x in ['arroz', 'feijão', 'óleo', 'açúcar', 'macarrão', 'café', 'dona elza', 'kicaldo', 'camil']): return "Mercearia"
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'filé', 'linguiça']): return "Açougue"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão']): return "Laticínios"
                if any(x in p for x in ['cerveja', 'suco', 'refrigerante', 'água', 'coca', 'original', 'açúcar']): return "Bebidas"
                if any(x in p for x in ['fralda', 'sabão', 'detergente', 'omo', 'papel']): return "Limpeza"
                return "Outros"
            
            df_temp['setor'] = df_temp['produto'].apply(categorizar)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- INTERFACE ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if st.session_state.carrinho:
        total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho)
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"**{item['qtd']}x** {item['nome']}")
            if st.button("Remover", key=f"s_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.metric("Total", f"R$ {total:,.2f}")
    
    st.markdown("---")
    st.markdown(f'<div class="prop-box"><b>ANUNCIE AQUI</b><br>(21) 98288-1425</div>', unsafe_allow_html=True)

# Banner Topo
st.markdown(f'<div class="prop-box">📢 <b>FAÇA SUA PROPAGANDA AQUI</b> - Contato: (21) 98288-1425 (WhatsApp)</div>', unsafe_allow_html=True)

st.title("📍 Economiza Maricá")

c1, c2 = st.columns([2, 1])
with c1:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Arroz...")
with c2:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    b_sel = st.selectbox("📍 Região", bairros)

if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if b_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == b_sel]

    abas = st.tabs(["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"])
    setores_lista = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]

    for i, aba in enumerate(abas):
        with aba:
            nome_setor = setores_lista[i]
            df_s = df_f if nome_setor == "Todos" else df_f[df_f['setor'] == nome_setor]
            
            if not df_s.empty:
                for p in df_s['produto'].unique():
                    ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                    with st.container():
                        st.markdown(f'<div class="card-produto"><span class="nome-prod">{p}</span>', unsafe_allow_html=True)
                        for _, row in ofertas.iterrows():
                            col1, col2, col3, col4 = st.columns([2.5, 1.2, 0.8, 0.5])
                            with col1:
                                st.markdown(f'<span class="nome-mercado">🏪 {row["mercado"]}</span><br><span style="font-size:0.75em;color:#999;">{row["bairro"]}</span>', unsafe_allow_html=True)
                            with col2:
                                st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                            with col3:
                                qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{nome_setor}_{row['id']}", label_visibility="collapsed")
                            with col4:
                                if st.button("🛒", key=f"b_{nome_setor}_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("🤖 Aguardando conexão com o coletor...")

