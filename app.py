import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

# Inicializa Carrinho na memória do navegador
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO ---
st.markdown("""<style>.stButton>button {border-radius: 8px; width: 100%; height: 3em; font-weight: bold;}</style>""", unsafe_allow_html=True)

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
        st.info("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"✅ **{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} no {item['mercado']}")
            texto_whats += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {subtotal:,.2f}\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        
        # WhatsApp Link com a lista pronta
        msg_final = texto_whats + f"\n💰 *Total: R$ {total_lista:,.2f}*"
        link_wa = f"https://wa.me/?text={urllib.parse.quote(msg_final)}"
        st.link_button("📲 Enviar Lista p/ WhatsApp", link_wa, type="primary")
        
        if st.button("Limpar Lista"):
            st.session_state.carrinho = []
            st.rerun()
    
    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes originais em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")
st.subheader("Onde sua economia acontece em tempo real")

if not df.empty:
    # 🔍 BUSCA E COMPARAÇÃO
    busca = st.text_input("🔍 Procure por um produto (ex: Arroz, Picanha, Feijão...)", "")
    
    # Se houver busca, filtramos. Se não, mostramos tudo.
    df_f = df[df['produto'].str.contains(busca, case=False)] if busca else df

    # --- LÓGICA DE COMPARAÇÃO DE PREÇOS ---
    # Agrupamos por produto para mostrar quem é o mais barato
    if not df_f.empty:
        st.markdown("### 🏷️ Ofertas Encontradas")
        
        for produto_nome in df_f['produto'].unique():
            itens = df_f[df_f['produto'] == produto_nome].sort_values(by='preco')
            
            with st.container(border=True):
                col_nome, col_precos = st.columns([2, 3])
                
                with col_nome:
                    st.markdown(f"#### {produto_nome}")
                    if len(itens) > 1:
                        st.write("🏆 *Comparação disponível*")
                
                with col_precos:
                    # Mostra cada mercado que tem esse produto
                    for _, row in itens.iterrows():
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"🏪 {row['mercado']}")
                        c2.subheader(f"R$ {row['preco']:,.2f}")
                        with c3:
                            qtd = st.number_input("Qtd", 1, 50, 1, key=f"qtd_{row['id']}")
                            if st.button("➕", key=f"add_{row['id']}"):
                                st.session_state.carrinho.append({
                                    "nome": row['produto'], 
                                    "preco": row['preco'], 
                                    "qtd": qtd, 
                                    "mercado": row['mercado']
                                })
                                st.toast(f"{row['produto']} adicionado!")
                                st.rerun()
else:
    st.warning("🤖 O robô está processando os encartes. Atualize a página em instantes!")
