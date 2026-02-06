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

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            # --- INTELIGÊNCIA DE SETORES (Caso o robô falhe) ---
            def classificar_setor(row):
                # Se o setor já estiver preenchido corretamente, mantém
                if row['setor'] in ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza"]:
                    return row['setor']
                
                # Caso contrário, tenta adivinhar pelo nome do produto
                prod = str(row['produto']).lower()
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha']):
                    return "Açougue"
                if any(x in prod for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha']):
                    return "Mercearia"
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão']):
                    return "Laticínios"
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água']):
                    return "Bebidas"
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante']):
                    return "Limpeza"
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
        return df_temp
    except:
        return pd.DataFrame()
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

