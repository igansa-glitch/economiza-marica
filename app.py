import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="💰")

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- TÍTULO ---
st.title("📍 Economiza Maricá")
st.subheader("O radar de preços oficial da nossa cidade")

if not df.empty:
    # --- ABA DE DESTAQUES (INTELIGÊNCIA) ---
    tab_promo, tab_setores = st.tabs(["🔥 SUPER OFERTAS DO DIA", "📦 TODOS OS PRODUTOS"])

    with tab_promo:
        st.write("Produtos com o melhor custo-benefício em Maricá hoje:")
        
        # Lógica: Se o produto aparece em mais de um mercado, comparamos.
        # Se for único, vemos se o preço está abaixo da média histórica (simplificado aqui)
        precos_medios = df.groupby('produto')['preco'].transform('mean')
        df['economia'] = (precos_medios - df['preco']) / precos_medios
        
        # Filtramos o que está 15% abaixo da média
        promos = df[df['economia'] > 0.15].sort_values(by='economia', ascending=False)

        if not promos.empty:
            cols = st.columns(3)
            for idx, row in promos.head(6).iterrows():
                with cols[idx % 3]:
                    st.success(f"**{row['produto']}**")
                    st.metric(label=row['mercado'], value=f"R$ {row['preco']:.2f}", delta=f"-{row['economia']*100:.0f}% mais barato")
                    st.caption(f"📍 {row['bairro']}")
        else:
            st.info("Buscando as melhores ofertas... O robô está analisando os encartes!")

    with tab_setores:
        setor_sel = st.selectbox("Escolha o setor:", ["Todos"] + list(df['setor'].unique()))
        
        filtro = df if setor_sel == "Todos" else df[df['setor'] == setor_sel]
        
        for _, row in filtro.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{row['produto']}**\n\n{row['mercado']}")
                c2.subheader(f"R$ {row['preco']:.2f}")
                if c3.button("Adicionar à Lista", key=f"btn_{row['id']}"):
                    st.toast(f"{row['produto']} adicionado!")

else:
    st.warning("Aguardando a IA terminar a leitura dos encartes... Os preços aparecerão aqui em instantes!")
