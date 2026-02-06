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

# --- ESTILO ---
st.markdown("""<style>.stButton>button {border-radius: 8px;}</style>""", unsafe_allow_html=True)

# --- CABEÇALHO E PROPAGANDA ---
st.info("📢 **Anuncie aqui:** Alcance milhares de moradores de Maricá! Contato: (21) 9XXXX-XXXX")
st.title("📍 Economiza Maricá")
st.markdown("### Onde sua lista sai mais barata hoje?")

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        response = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO) ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_atual = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total_atual += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {sub:,.2f}")
            texto_whats += f"• {item['qtd']}x {item['nome']} (R$ {sub:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total", f"R$ {total_atual:,.2f}")
        link_whats = f"https://wa.me/?text={urllib.parse.quote(texto_whats + f'\n💰 *Total: R$ {total_atual:,.2f}*')}"
        st.link_button("📲 Enviar p/ WhatsApp", link_whats, use_container_width=True)
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()
    
    st.markdown("---")
    st.warning("🛍️ **Daniparfun**\nOs melhores perfumes árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
if not df.empty:
    # 1. Comparador de Economia (Só aparece se tiver itens no carrinho)
    if st.session_state.carrinho:
        with st.container(border=True):
            st.markdown("#### 📊 Comparativo de Preços")
            mercados = df['mercado'].unique()
            res_comp = []
            for m in mercados:
                soma, conta = 0, 0
                for item in st.session_state.carrinho:
                    match = df[(df['mercado'] == m) & (df['produto'] == item['nome'])]
                    if not match.empty:
                        soma += match['preco'].values[0] * item['qtd']
                        conta += 1
                if conta > 0:
                    res_comp.append({"Mercado": m, "Total": soma})
            
            if res_comp:
                res_df = pd.DataFrame(res_comp).sort_values(by="Total")
                st.success(f"Sua compra é mais barata no **{res_df.iloc[0]['Mercado']}** (R$ {res_df.iloc[0]['Total']:,.2f})")

    # 2. Busca e Filtros
    busca = st.text_input("🔍 Procure por um produto (ex: Alcatra, Arroz...)", placeholder="Digite aqui...")
    if busca:
        df = df[df['produto'].str.lower().str.contains(busca.lower())]

    # 3. Vitrine por Setores
    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            df_s = df[df['setor'] == setor]
            if not df_s.empty:
                for _, row in df_s.iterrows():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 1.5, 1.2])
                        with c1:
                            st.markdown(f"**{row['produto']}**")
                            st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}, Maricá")
                        with c2:
                            st.subheader(f"R$ {row['preco']:,.2f}".replace('.', ','))
                        with c3:
                            q = st.number_input("Qtd", 1, 50, 1, key=f"q_{row['id']}")
                            if st.button("Adicionar", key=f"b_{row['id']}", use_container_width=True):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": q})
                                st.toast("Adicionado!")
                                st.rerun()
            else:
                st.write("Nenhuma oferta encontrada neste setor.")
else:
    st.warning("⚠️ O banco de dados está vazio! Por favor, rode o **coletor.py** no seu computador para enviar os preços.")

st.markdown("---")
st.caption("📍 Economiza Maricá - 2026")
