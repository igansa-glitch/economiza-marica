import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

# Inicializa Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO E CABEÇALHO ---
st.markdown("""<style>.stButton>button {border-radius: 8px; width: 100%;}</style>""", unsafe_allow_html=True)

# Área de Propaganda Superior
st.info("📢 **Anuncie aqui:** Alcance milhares de moradores de Maricá! Contato: (21) 9XXXX-XXXX")

st.title("📍 Economiza Maricá")
st.markdown("### Onde sua lista sai mais barata hoje?")

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO E PROPAGANDA) ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} ({item['mercado']})")
            texto_whats += f"• {item['qtd']}x {item['nome']} - {item['mercado']} (R$ {subtotal:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total da Lista", f"R$ {total_lista:,.2f}")
        
        # WhatsApp Link
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whats + f'\n💰 *Total Estimado: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar p/ WhatsApp", link_wa, use_container_width=True)
        
        if st.button("Limpar Tudo"):
            st.session_state.carrinho = []
            st.rerun()
    
    st.markdown("---")
    # Propaganda Daniparfun
    st.warning("🛍️ **Daniparfun.com.br**\nOs melhores perfumes árabes de Maricá estão aqui! Visite nosso site.")

# --- CONTEÚDO PRINCIPAL ---
if not df.empty:
    tab_promo, tab_setores = st.tabs(["🔥 SUPER OFERTAS", "📦 TODOS OS PRODUTOS"])

    # ABA 1: SUPER OFERTAS (Lógica de Desconto)
    with tab_promo:
        st.markdown("#### Melhores oportunidades de hoje")
        # Calcula média para destacar o que está barato
        df['preco_medio'] = df.groupby('produto')['preco'].transform('mean')
        df['desconto'] = (df['preco_medio'] - df['preco']) / df['preco_medio']
        
        # Filtra ofertas reais (mais de 10% de economia comparado à média)
        promos = df[df['desconto'] > 0.10].sort_values(by='desconto', ascending=False)

        if not promos.empty:
            cols = st.columns(3)
            for idx, row in promos.head(6).iterrows():
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.error(f"Economia de {row['desconto']*100:.0f}%")
                        st.write(f"**{row['produto']}**")
                        st.subheader(f"R$ {row['preco']:,.2f}")
                        st.caption(f"🏪 {row['mercado']}")
                        if st.button("Adicionar", key=f"p_{row['id']}"):
                            st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                            st.rerun()
        else:
            st.info("O robô ainda está analisando as melhores ofertas...")

    # ABA 2: TODOS OS PRODUTOS (Layout Original)
    with tab_setores:
        busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Feijão...")
        df_filtrado = df[df['produto'].str.contains(busca, case=False)] if busca else df
        
        setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
        abas_s = st.tabs(setores)

        for i, s in enumerate(setores):
            with abas_s[i]:
                dados_s = df_filtrado[df_filtrado['setor'] == s]
                if not dados_s.empty:
                    for _, row in dados_s.iterrows():
                        with st.container(border=True):
                            c1, c2, c3 = st.columns([3, 1.5, 1.2])
                            with c1:
                                st.markdown(f"**{row['produto']}**")
                                st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}")
                            with c2:
                                st.subheader(f"R$ {row['preco']:,.2f}")
                            with c3:
                                q = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                                if st.button("🛒", key=f"b_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": q, "mercado": row['mercado']})
                                    st.toast("Adicionado!")
                                    st.rerun()
                else:
                    st.write("Sem produtos neste setor no momento.")
else:
    st.warning("⚠️ Aguardando dados do robô... Deixe o `coletor_ia_v2.py` rodando no seu computador!")

st.markdown("---")
st.caption("📍 Economiza Maricá - 2026 | Orgulhosamente servindo nossa cidade.")
