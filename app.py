import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- BUSCA DE DADOS ---
response = supabase.table("ofertas").select("*").execute()
df = pd.DataFrame(response.data)

st.title("📍 Economiza Maricá")
st.markdown("### Onde sua lista sai mais barata hoje?")

# --- LÓGICA DE COMPARAÇÃO DE CARRINHO ---
if st.session_state.carrinho and not df.empty:
    with st.expander("📊 ANÁLISE DE ECONOMIA DA SUA LISTA", expanded=True):
        st.write("Simulamos sua lista nos mercados de Maricá:")
        
        mercados = df['mercado'].unique()
        resultados_comparacao = []

        for m in mercados:
            total_no_mercado = 0
            itens_encontrados = 0
            
            for item_carrinho in st.session_state.carrinho:
                # Tenta achar o mesmo produto nesse mercado
                match = df[(df['mercado'] == m) & (df['produto'] == item_carrinho['nome'])]
                if not match.empty:
                    total_no_mercado += match['preco'].values[0] * item_carrinho['qtd']
                    itens_encontrados += 1
            
            if itens_encontrados > 0:
                resultados_comparacao.append({"Mercado": m, "Total": total_no_mercado, "Itens": itens_encontrados})

        # Exibe o veredito
        if resultados_comparacao:
            res_df = pd.DataFrame(resultados_comparacao).sort_values(by="Total")
            melhor_opcao = res_df.iloc[0]
            
            st.success(f"✅ **Veredito:** Sua lista está mais barata no **{melhor_opcao['Mercado']}**!")
            st.info(f"💰 Valor Total estimado: **R$ {melhor_opcao['Total']:,.2f}**")
            
            if len(res_df) > 1:
                economia = res_df.iloc[1]['Total'] - melhor_opcao['Total']
                st.write(f"👉 Você economiza **R$ {economia:,.2f}** comparado ao segundo lugar.")

# --- BARRA LATERAL (CARRINHO) ---
with st.sidebar:
    st.header("🛒 Sua Lista")
    if not st.session_state.carrinho:
        st.write("Vazia")
    else:
        total_atual = 0
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total_atual += sub
            st.write(f"{item['qtd']}x {item['nome']}")
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.metric("Total Atual", f"R$ {total_atual:,.2f}")

# --- VITRINE DE PRODUTOS ---
# (Aqui entra o código das abas de setores que já temos...)
