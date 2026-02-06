import streamlit as st
import pandas as pd
from supabase import create_client

# Conexão (Mantenha suas chaves)
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide")

# --- BUSCA DE DADOS ---
try:
    response = supabase.table("ofertas").select("*").execute()
    df = pd.DataFrame(response.data)
except:
    df = pd.DataFrame()

st.title("📍 Economiza Maricá")
st.subheader("Compare e escolha o menor preço da cidade!")

if not df.empty:
    # --- ABA DE COMPARATIVO ---
    tab_comp, tab_setores = st.tabs(["🔥 Comparar Preços", "📂 Ver por Setores"])

    with tab_comp:
        st.markdown("### 🏆 Onde está mais barato?")
        # Agrupa produtos iguais para comparar
        produtos_unicos = df['produto'].unique()
        
        for prod in produtos_unicos:
            variacoes = df[df['produto'] == prod].sort_values(by='preco')
            
            if len(variacoes) > 1: # Só mostra se tiver em mais de um mercado
                with st.container(border=True):
                    st.write(f"**PRODUTO:** {prod}")
                    cols = st.columns(len(variacoes))
                    
                    for idx, (index, row) in enumerate(variacoes.iterrows()):
                        with cols[idx]:
                            # O primeiro da lista é o mais barato (devido ao sort_values)
                            cor = "green" if idx == 0 else "gray"
                            st.markdown(f"""
                                <div style="border: 2px solid {cor}; padding: 10px; border-radius: 10px; text-align: center;">
                                    <p style="margin:0; font-size: 12px;">{row['mercado']}</p>
                                    <h2 style="margin:0; color: {cor};">R$ {row['preco']:.2f}</h2>
                                </div>
                            """, unsafe_allow_html=True)
                            if idx == 0: st.success("✅ Melhor Escolha")

    with tab_setores:
        st.write("Aqui ficam as abas normais por categoria que já criamos...")
        # (O código das abas de setores entra aqui)
else:
    st.info("O robô está trabalhando para comparar os preços...")
