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
    st.header("🛒 Sua Lista")
    if st.session_state.carrinho:
        total = 0
        texto_wa = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total += subtotal
            st.write(f"**{item['nome']}**")
            st.caption(f"R$ {item['preco']:.2f} no {item['mercado']}")
            texto_wa += f"• {item['nome']} ({item['mercado']}) - R$ {item['preco']:.2f}\n"
            
            # BOTÃO DE REMOVER INDIVIDUAL (MANTIDO)
            if st.button(f"Remover item", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
        
        # BOTÃO ENVIAR WHATSAPP
        link_zap = f"https://wa.me/?text={urllib.parse.quote(texto_wa + f'\n💰 *Total: R$ {total:.2f}*')}"
        st.link_button("📲 Enviar Lista p/ WhatsApp", link_zap, use_container_width=True, type="primary")
        
        # NOVO BOTÃO: LIMPAR TUDO
        if st.button("🗑️ Limpar Lista Toda", use_container_width=
