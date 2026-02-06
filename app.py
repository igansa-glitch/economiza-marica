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
st.markdown("""<style>.stButton>button {border-radius: 8px; font-weight: bold; height: 3em;}</style>""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
@st.cache_data(ttl=30)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.info("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} no {item['mercado']}")
            texto_whats += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {subtotal:,.2f}\n"
            if st.button("Remover", key=f"sidebar_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whats + f'\n💰 *Total: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar WhatsApp", link_wa, type="primary")

    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Arroz, Picanha...")
    
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            # Filtro inteligente
            df_setor = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            if busca:
                df_setor = df_setor[df_setor['produto'].str.contains(busca, case=False)]
            
            if not df_setor.empty:
                # Agrupamento para Comparativo
                for produto in df_setor['produto'].unique():
                    variacoes = df_setor[df_setor['produto'] == produto].sort_values(by='preco')
                    
                    with st.container(border=True):
                        st.markdown(f"### {produto}")
                        
                        for _, row in variacoes.iterrows():
                            c1, c2, c3 = st.columns([2.5, 1.5, 1])
                            with c1:
                                st.write(f"🏪 **{row['mercado']}**")
                                st.caption(f"📍 {row['bairro']} | Maricá")
                            with c2:
                                st.subheader(f"R$ {row['preco']:,.2f}")
                            with c3:
                                # A CHAVE (KEY) AGORA É ÚNICA POR ABA E POR ID
                                key_qtd = f"qtd_{nome_setor}_{row['id']}"
                                key_btn = f"btn_{nome_setor}_{row['id']}"
                                
                                qtd = st.number_input("Qtd", 1, 50, 1, key=key_qtd)
                                if st.button("🛒 Adicionar", key=key_btn):
                                    st.session_state.carrinho.append({
                                        "nome": row['produto'], 
                                        "preco": row['preco'], 
                                        "qtd": qtd, 
                                        "mercado": row['mercado']
                                    })
                                    st.toast(f"{row['produto']} adicionado!")
                                    st.rerun()
            else:
                st.write("Nenhum item por aqui.")
else:
    st.warning("🤖 Aguardando dados do robô...")
