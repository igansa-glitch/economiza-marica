import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 2. DESIGN E BANNER FIXO
st.markdown("""
    <style>
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #FFD700;
        z-index: 9999;
        border-bottom: 3px solid #000;
        padding: 10px;
        text-align: center;
        color: black;
    }
    .main-content {
        margin-top: 150px;
    }
    .card-produto {
        border-left: 5px solid #FFD700;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .nome-prod {font-size: 14px !important; font-weight: bold; text-transform: uppercase; color: #333;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.25em;}
    </style>
    <div class="fixed-header">
        <h2 style='margin:0; font-size: 20px;'>ANUNCIE AQUI! 📢</h2>
        <p style='margin:5px 0 0 0; font-size: 16px;'>WhatsApp: <b>(21) 98288-1425</b></p>
    </div>
""", unsafe_allow_html=True)

# 3. FILTRO DE QUALIDADE
def validar_dados(row):
    n = str(row.get('produto', '')).upper().strip()
    m = str(row.get('mercado', '')).upper().strip()
    if any(x in m for x in ['LOCAL', 'COMÉRCIO', 'DESCONHECIDO']): return None
    if any(x in n for x in [';', '%', '!', 'ICOA', 'PACV', 'FC1']) or len(n) < 4: return None
    return n

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            df_temp['produto_valido'] = df_temp.apply(validar_dados, axis=1)
            df_temp = df_temp.dropna(subset=['produto_valido'])
            df_temp['produto'] = df_temp['produto_valido']
            
            def categorizar(p):
                p = p.lower()
                if any(x in p for x in ['arroz', 'feijão', 'óleo', 'açúcar', 'macarrão', 'café']): return "Mercearia"
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'filé', 'linguiça']): return "Açougue"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga']): return "Laticínios"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'água', 'coca']): return "Bebidas"
                if any(x in p for x in ['fralda', 'sabão', 'detergente', 'omo', 'papel']): return "Limpeza"
                return "Outros"
            df_temp['setor'] = df_temp['produto'].apply(categorizar)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# 4. CONTEÚDO PRINCIPAL
st.markdown('<div class="main-content">', unsafe_allow_html=True)

with st.sidebar:
    st.header("🛒 Sua Lista de Compras")
    if st.session_state.carrinho:
        total = sum(item['preco'] * item['qtd'] for item in st.session_state.carrinho)
        texto_wa = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"**{item['qtd']}x** {item['nome']}")
            texto_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']})\n"
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
        link_zap = f"https://wa.me/?text={urllib.parse.quote(texto_wa + f'Total: R$ {total:.2f}')}"
        st.link_button("📲 Enviar Lista p/ WhatsApp", link_zap, use_container_width=True, type="primary")
    else:
        st.info("Lista vazia.")

st.title("📍 Comparativo Maricá")

c_busca, c_local = st.columns([2, 1])
with c_busca:
    busca = st.text_input("🔍 O que você procura?", placeholder="Buscar...")
with c_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Região", bairros)

if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    
    # AQUI ESTAVA O SEU ERRO DE INDENTAÇÃO:
    if bairro_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_sel]

    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, aba in enumerate(abas):
        with aba:
            nome_s = setores[i]
            df_s = df_f if nome_s == "Todos" else df_f[df_f['setor'] == nome_s]
            
            for p in df_s['produto'].unique():
                ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                with st.container():
                    st.markdown(f'<div class="card-produto"><span class="nome-prod">{p}</span>', unsafe_allow_html=True)
                    for _, row in ofertas.iterrows():
                        col1, col2, col3 = st.columns([2.5, 1.5, 0.5])
                        with col1:
                            st.write(f"🏪 **{row['mercado']}**")
                            st.caption(f"📍 {row['bairro']}")
                        with col2:
                            st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                        with col3:
                            if st.button("🛒", key=f"b_{nome_s}_{row['id']}"):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                                st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
