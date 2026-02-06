import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO (Mantendo seus dados) ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

# 2. JANELA SUPERIOR FIXA (Propaganda Destaque)
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
    }
    .main-content {
        margin-top: 110px; /* Abre espaço para o topo fixo */
    }
    .product-row {
        border-bottom: 1px solid #eee;
        padding: 8px 0;
        display: flex;
        align-items: center;
    }
    </style>
    <div class="fixed-header">
        <h2 style='margin:0;'>ANUNCIE AQUI! 📢</h2>
        <p style='margin:0; font-size: 18px;'>WhatsApp: <b>(21) 982881425</b></p>
    </div>
""", unsafe_allow_html=True)

# 3. JANELA LATERAL (Anúncios Secundários)
with st.sidebar:
    st.header("Parceiros")
    st.info("FAÇA SUA PROPAGANDA AQUI!\n\n(21) 982881425")
    st.divider()
    # Futuros anúncios podem entrar aqui

# 4. CONTEÚDO PRINCIPAL (Busca de Dados do Supabase)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("📍 Comparativo de Preços em Maricá")

# Exemplo de consulta ao seu banco (ajuste o nome da tabela conforme sua estrutura)
try:
    response = supabase.table("produtos").select("*").execute()
    dados = response.data
    
    if dados:
        for item in dados:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # Nome do produto com fonte menor como você pediu
                st.markdown(f"<span style='font-size:14px;'><b>{item['nome']}</b></span><br><small>{item.get('mercado', 'Mercado Local')}</small>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<b style='color:green;'>R$ {item['preco']}</b>", unsafe_allow_html=True)
                
            with col3:
                # Aqui você poderá puxar a distância calculada automaticamente
                st.write(f"📍 {item.get('distancia', 'Calculando...')}")
                
            with col4:
                # Botão de WhatsApp para o usuário compartilhar a lista
                msg = f"Olha esse preço no Economiza Maricá: {item['nome']} por R${item['preco']}"
                link_zap = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{link_zap}" target="_blank" style="text-decoration:none;"><button style="background-color:#25d366; color:white; border:none; padding:5px 10px; border-radius:5px; width:100%;">WhatsApp</button></a>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum produto encontrado no banco de dados.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

st.markdown('</div>', unsafe_allow_html=True)
