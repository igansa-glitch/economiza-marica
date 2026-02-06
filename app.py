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

   # ABA 1: SUPER OFERTAS (Lógica de Comparação Real)
    with tab_promo:
        st.markdown("#### 🔥 Onde você economiza de verdade")
        
        # Só calculamos economia se o produto existir em mais de um lugar
        contagem_produtos = df.groupby('produto')['mercado'].transform('count')
        df_comparavel = df[contagem_produtos > 1].copy()
        
        if not df_comparavel.empty:
            df_comparavel['preco_max'] = df_comparavel.groupby('produto')['preco'].transform('max')
            df_comparavel['economia_real'] = (df_comparavel['preco_max'] - df_comparavel['preco']) / df_comparavel['preco_max']
            
            # Filtra onde a diferença é maior que zero (o mais barato de todos)
            melhores_precos = df_comparavel[df_comparavel['economia_real'] > 0].sort_values(by='economia_real', ascending=False)

            if not melhores_precos.empty:
                cols = st.columns(3)
                for idx, row in melhores_precos.head(6).iterrows():
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.error(f"📉 {row['economia_real']*100:.0f}% MAIS BARATO")
                            st.write(f"**{row['produto']}**")
                            st.subheader(f"R$ {row['preco']:,.2f}")
                            st.caption(f"🏪 No {row['mercado']} vs outros")
                            if st.button("Adicionar", key=f"promo_{row['id']}"):
                                st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                                st.rerun()
            else:
                st.info("💡 Dica: Adicione mais encartes! Quando dois mercados tiverem o mesmo item, eu te aviso qual é o mais barato aqui.")
        else:
            st.info("🧐 O robô está analisando os outros mercados. Assim que eu encontrar o mesmo produto em dois lugares, calcularei a economia para você!")
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

