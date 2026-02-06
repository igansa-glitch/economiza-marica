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

# --- ESPAÇO PARA PROPAGANDA NO TOPO ---
st.info("📢 **Espaço para Anunciante:** Anuncie sua loja aqui! Contato: (21) 9XXXX-XXXX")

st.title("📍 Economiza Maricá")
st.markdown("---")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081840.png", width=100)
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
            resumo_whats += f"• {item['qtd']}x {item['nome']} (R$ {subtotal:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total da Compra", f"R$ {total_geral:,.2f}")
        
        link_final = f"https://wa.me/?text={urllib.parse.quote(resumo_whats + f'\n💰 *Total: R$ {total_geral:,.2f}*')}"
        st.link_button("📲 Enviar Lista p/ WhatsApp", link_final, use_container_width=True)
        
        if st.button("Limpar Carrinho", use_container_width=True):
            st.session_state.carrinho = []
            st.rerun()

    # --- ESPAÇO PARA PROPAGANDA NA LATERAL ---
    st.markdown("---")
    st.markdown("### ✨ Patrocínio")
    st.warning("🛍️ **Daniparfun**\nPerfumes Árabes com os melhores preços de Maricá! Clique para saber mais.")

# --- BUSCA E CONTEÚDO PRINCIPAL ---
try:
    response = supabase.table("ofertas").select("*").execute()
    df = pd.DataFrame(response.data)
except:
    df = pd.DataFrame()

if not df.empty:
    col_busca, col_filtro = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 O que você quer economizar hoje?", placeholder="Ex: Alcatra, Leite, Feijão...")
    with col_filtro:
        ordem = st.selectbox("Ordenar por:", ["Menor Preço", "Produto (A-Z)"])

    if busca:
        df = df[df['produto'].str.lower().str.contains(busca.lower())]
    
    if ordem == "Menor Preço":
        df = df.sort_values(by="preco")
    else:
        df = df.sort_values(by="produto")

    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            df_s = df[df['setor'] == setor]
            if not df_s.empty:
                for _, row in df_s.iterrows():
                    with st.container(border=True): # Bordas para parecer um "Card"
                        c1, c2, c3 = st.columns([3, 1.5, 1.2])
                        with c1:
                            st.subheader(row['produto'])
                            st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}, Maricá")
                        with c2:
                            st.write("Valor Unitário:")
                            st.title(f"R$ {row['preco']:,.2f}".replace('.', ','))
                        with c3:
                            q = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                            if st.button("Adicionar", key=f"b_{row['id']}", use_container_width=True):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": q})
                                st.toast("Item adicionado!")
                                st.rerun()
            else:
                st.info(f"Nenhuma oferta de {setor} encontrada.")
else:
    st.warning("O robô está atualizando os preços. Volte em instantes!")

# --- ESPAÇO PARA PROPAGANDA NO RODAPÉ ---
st.markdown("---")
st.caption("📍 Economiza Maricá - 2026 | Desenvolvido para ajudar o povo maricaense.")







