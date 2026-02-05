import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# Conexão
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="🛒", layout="wide")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

st.title("📍 Economiza Maricá")
st.markdown("### O robô IA pesquisa, você economiza!")
st.divider()

# --- BARRA LATERAL COM WHATSAPP ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_geral = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá* \n\n"
        
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_geral += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"Subtotal: R$ {subtotal:,.2f}")
            texto_whats += f"✅ {item['qtd']}x {item['nome']} (R$ {subtotal:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        texto_whats += f"\n💰 *Total: R$ {total_geral:,.2f}*"
        st.divider()
        st.markdown(f"### Total: R$ {total_geral:,.2f}")
        
        # Botão do WhatsApp
        texto_codificado = urllib.parse.quote(texto_whats)
        link_whats = f"https://wa.me/?text={texto_codificado}"
        st.link_button("📲 Enviar p/ WhatsApp", link_whats)
        
        if st.button("Limpar Tudo"):
            st.session_state.carrinho = []
            st.rerun()

# --- EXIBIÇÃO DAS OFERTAS ---
df = pd.DataFrame(supabase.table("ofertas").select("*").execute().data)

if not df.empty:
    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            df_setor = df[df['setor'] == setor]
            if not df_setor.empty:
                for _, row in df_setor.iterrows():
                    preco_f = f"R$ {row['preco']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"#### {row['produto']}")
                        st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}, Maricá")
                    with col2:
                        st.markdown(f"## {preco_f}")
                    with col3:
                        qtd = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                        if st.button("Add", key=f"b_{row['id']}"):
                            st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd})
                            st.rerun()
                    st.divider()
else:
    st.warning("Aguardando o robô...")

     



