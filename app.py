

import streamlit as st
import pandas as pd
from supabase import create_client

# Configurações (Assegure que as aspas estão aqui!)
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"

# Inicializa o cliente Supabase
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", page_icon="📍")
st.markdown("<h1 style='text-align: center; color: #27ae60;'>📍 Economiza Maricá</h1>", unsafe_allow_html=True)

# Função para buscar dados
def buscar_dados():
    try:
        # Busca os dados da tabela 'ofertas'
        resposta = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(resposta.data)
    except Exception as e:
        st.error(f"Erro ao conectar com o banco: {e}")
        return pd.DataFrame()

df = buscar_dados()

if not df.empty:
    st.success("Preços atualizados hoje em Maricá!")
    
    # Criar filtros para facilitar a busca do usuário
    bairros = df['bairro'].unique()
    bairro_selecionado = st.selectbox("Escolha seu bairro:", bairros)
    
    setores = df['setor'].unique()
    setor_selecionado = st.radio("O que você procura?", setores, horizontal=True)
    
    # Filtrar os dados
    filtro = (df['bairro'] == bairro_selecionado) & (df['setor'] == setor_selecionado)
    df_exibir = df[filtro].sort_values(by='preco')
    
    if not df_exibir.empty:
        # Mostrar os dados de forma bonita
        for index, row in df_exibir.iterrows():
            with st.container():
                st.markdown(f"""
                <div style='border: 1px solid #ddd; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
                    <h3 style='margin: 0;'>{row['produto']}</h3>
                    <p style='color: #27ae60; font-size: 20px; font-weight: bold;'>R$ {row['preco']:.2f}</p>
                    <p style='margin: 0;'>🏪 <b>{row['mercado']}</b></p>
                    <p style='font-size: 12px; color: #666;'>📍 {row['bairro']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma oferta encontrada para este setor neste bairro.")
else:
    st.warning("Aguardando o Agente IA enviar os preços de hoje...")
    st.info("Dica: Rode o arquivo coletor.py no seu computador para enviar dados!")


