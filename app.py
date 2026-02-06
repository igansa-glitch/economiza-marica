import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# Conexão
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="🛒", layout="wide")

# Inicializa Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("📍 Economiza Maricá")
st.markdown("### O robô IA pesquisa, você economiza!")
st.divider()

# Sidebar - Carrinho e WhatsApp
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_geral = 0
        resumo_whats = "🛒 *Lista de Compras - Economiza Maricá*\n\n"
        
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_geral += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"Subtotal: R$ {subtotal:,.2f}")
            resumo_whats += f"• {item['qtd']}x {item['nome']} (R$ {subtotal:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        resumo_whats += f"\n💰 *Total Estimado: R$ {total_geral:,.2f}*"
        st.divider()
        st.markdown(f"### Total: R$ {total_geral:,.2f}")
        
        # Link WhatsApp
        link_final = f"https://wa.me/?text={urllib.parse.quote(resumo_whats)}"
        st.link_button("📲 Enviar p/ WhatsApp", link_final, use_container_width=True)
        
        if st.button("Limpar Tudo"):
            st.session_state.carrinho = []
            st.rerun()

# Busca Dados
try:
    response = supabase.table("ofertas").select("*").execute()
    df = pd.DataFrame(response.data)
except:
    df = pd.DataFrame()

if not df.empty:
    # Campo de busca para facilitar
    busca = st.text_input("🔍 O que você está procurando hoje?", "").lower()
    if busca:
        df = df[df['produto'].str.lower().str.contains(busca)]

    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            df_s = df[df['setor'] == setor]
            if not df_s.empty:
                for _, row in df_s.iterrows():
                    p_form = f"R$ {row['preco']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                    c1, c2, c3 = st.columns([3, 2, 1.2])
                    with c1:
                        st.markdown(f"#### {row['produto']}")
                        st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}, Maricá - RJ")
                    with c2:
                        st.markdown(f"## {p_form}")
                    with c3:
                        q = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                        if st.button("Adicionar", key=f"b_{row['id']}", use_container_width=True):
                            st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": q})
                            st.toast("Adicionado!")
                            st.rerun()
                    st.divider()
            else:
                st.info("Nenhuma oferta neste setor.")
else:
    st.warning("O robô está coletando os preços agora. Aguarde um instante!")
      
           
                    






