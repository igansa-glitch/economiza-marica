import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .prop-box {background-color: #f8f9fa; padding: 12px; text-align: center; border: 2px dashed #007bff; border-radius: 8px; margin-bottom: 15px; color: #333;}
    .whats-link {color: #25d366; font-weight: bold; text-decoration: none;}
    .card-produto {border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: white;}
    .nome-prod {font-size: 1.05em !important; font-weight: bold; color: #2c3e50; margin-bottom: 8px; border-bottom: 2px solid #007bff; display: inline-block;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.1em;}
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO E CLASSIFICAÇÃO AUTOMÁTICA ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            
            # Inteligência para separar os produtos nas abas certas
            def definir_setor(p):
                p = str(p).lower()
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'porco', 'moída']): return "Açougue"
                if any(x in p for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'sal', 'biscoito', 'molho', 'extrato', 'milho']): return "Mercearia"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'creme de leite', 'leite condensado']): return "Laticínios"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'coca', 'fanta', 'skol', 'brahma', 'heineken']): return "Bebidas"
                if any(x in p for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'fralda', 'omo', 'shampoo']): return "Limpeza"
                return "Outros"
            
            df_temp['setor'] = df_temp['produto'].apply(definir_setor)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- PROPAGANDA SUPERIOR ---
st.markdown(f'<div class="prop-box">📢 <b>FAÇA SUA PROPAGANDA AQUI</b><br>Contato: (21) 98288-1425<br><a href="https://wa.me/5521982881425" class="whats-link">WhatsApp</a></div>', unsafe_allow_html=True)

# --- FILTROS ---
c_busca, c_local = st.columns([2, 1])
with c_busca:
    busca = st.text_input("🔍 O que você procura?", placeholder="Buscar...")
with c_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Região", bairros)

# --- EXIBIÇÃO POR ABAS CORRIGIDA ---
if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_sel]

    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            # --- O FILTRO QUE FALTAVA ---
            if nome_setor == "Todos":
                df_s = df_f
            else:
                df_s = df_f[df_f['setor'] == nome_setor]
            
            if not df_s.empty:
                for p in df_s['produto'].unique():
                    ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                    with st.container():
                        st.markdown(f'<div class="card-produto"><div class="nome-prod">{p}</div>', unsafe_allow_html=True)
                        for _, row in ofertas.iterrows():
                            c1, c2, c3, c4 = st.columns([2.5, 1.2, 0.8, 0.5])
                            with c1:
                                st.write(f"🏪 **{row['mercado']}** ({row['bairro']})")
                            with c2:
                                st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                            with c3:
                                qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{nome_setor}_{row['id']}", label_visibility="collapsed")
                            with c4:
                                if st.button("🛒", key=f"b_{nome_setor}_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.toast("Adicionado!")
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"Sem ofertas para {nome_setor} no momento.")
else:
    st.warning("Aguardando dados...")
