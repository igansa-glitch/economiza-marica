import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações de Conexão
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="🛒", layout="wide")

st.title("📍 Economiza Maricá")
st.markdown("### O robô IA pesquisa, você economiza!")
st.divider()

# Função para puxar dados
def buscar_dados():
    try:
        response = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(response.data)
    except:
        return pd.DataFrame()

df = buscar_dados()

if not df.empty:
    # Definir os setores que queremos mostrar nas abas
    setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
    
    # Criar as abas no topo do site
    abas = st.tabs(setores)

    for i, setor in enumerate(setores):
        with abas[i]:
            # Filtrar dados apenas para aquele setor
            df_setor = df[df['setor'] == setor]
            
            if not df_setor.empty:
                # Mostrar em formato de cards ou lista limpa
                for _, row in df_setor.iterrows():
                    preco_formatado = f"R$ {row['preco']:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ',')
                    
                    with st.expander(f"💰 {preco_formatado} - {row['produto']}"):
                        st.write(f"🏠 Mercado: **{row['mercado']}**")
                        st.write(f"📍 Bairro: {row['bairro']}")
                        st.caption("Preço coletado automaticamente via Robô IA")
            else:
                st.info(f"Ainda não encontramos ofertas de {setor} hoje.")
else:
    st.warning("Aguardando o robô coletar os preços do encarte...")

# Botão lateral para atualizar
if st.sidebar.button("🔄 Atualizar Página"):
    st.rerun()
