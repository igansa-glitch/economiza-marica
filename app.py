import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO CSS AVANÇADO ---
st.markdown("""
    <style>
    .stApp {background-color: #f4f7f6;}
    .prop-box {background-color: #ffffff; padding: 15px; text-align: center; border: 2px dashed #e74c3c; border-radius: 10px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);}
    .whats-link {color: #25d366; font-weight: bold; font-size: 1.2em; text-decoration: none;}
    .card-produto {border-left: 5px solid #007bff; border-radius: 8px; padding: 15px; margin-bottom: 15px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .nome-prod {font-size: 1em !important; font-weight: 700; color: #333; text-transform: uppercase; margin-bottom: 10px; display: block;}
    .preco-valor {color: #27ae60; font-weight: 900; font-size: 1.3em;}
    .nome-mercado {font-weight: 600; color: #555; font-size: 0.9em;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA DE NOMES ---
def limpar_nome(nome):
    n = str(nome).upper()
    substituicoes = ['UNIDADE', 'UNID', ' CADA', ' KG', ' TIPO 1', ' TIPO 2']
    for s in substituicoes:
        n = n.replace(s, '')
    return n.strip()

# --- CARREGAMENTO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            df_temp['produto'] = df_temp['produto'].apply(limpar_nome)
            
            def definir_setor(p):
                p = p.lower()
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'porco', 'moída', 'bovino', 'suíno']): return "Açougue"
                if any(x in p for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'sal', 'biscoito', 'molho', 'extrato', 'milho', 'azeite']): return "Mercearia"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'creme de leite', 'leite condensado', 'frios']): return "Laticínios"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'coca', 'fanta', 'skol', 'brahma', 'heineken', 'guaraná']): return "Bebidas"
                if any(x in p for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'fralda', 'omo', 'shampoo', 'sabonete']): return "Limpeza"
                return "Outros"
            
            df_temp['setor'] = df_temp['produto'].apply(definir_setor)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.info("Adicione itens para comparar.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
    
    st.markdown("---")
    st.markdown(f'<div class="prop-box"><b>ANUNCIE AQUI</b><br>(21) 98288-1425<br><span style="color:#25d366;">WhatsApp</span></div>', unsafe_allow_html=True)

# --- CONTEÚDO PRINCIPAL ---
st.markdown(f'<div class="prop-box">📢 <b>ESPAÇO DISPONÍVEL PARA ANUNCIANTES</b><br>Destaque sua marca aqui! Contato: (21) 98288-1425<br><a href="https://wa.me/5521982881425" class="whats-link">Clique para conversar no WhatsApp</a></div>', unsafe_allow_html=True)

st.title("📍 Economiza Maricá")

c1, c2 = st.columns([2, 1])
with c1:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz, Cerveja...")
with c2:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Filtrar Região", bairros)

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
            df_s = df_f if nome_setor == "Todos" else df_f[df_f['setor'] == nome_setor]
            
            if not df_s.empty:
                for p in df_s['produto'].unique():
                    ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                    with st.container():
                        st.markdown(f'<div class="card-produto"><span class="nome-prod">{p}</span>', unsafe_allow_html=True)
                        for _, row in ofertas.iterrows():
                            col1, col2, col3, col4 = st.columns([2.5, 1.2, 0.8, 0.5])
                            with col1:
                                st.markdown(f'<span class="nome-mercado">🏪 {row["mercado"]}</span> <br> <span style="font-size:0.8em; color:#888;">📍 {row["bairro"]}</span>', unsafe_allow_html=True)
                            with col2:
                                st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                            with col3:
                                qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{nome_setor}_{row['id']}", label_visibility="collapsed")
                            with col4:
                                if st.button("🛒", key=f"b_{nome_setor}_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"Nenhum item em {nome_setor} nesta região.")
else:
    st.warning("🤖 Aguardando conexão com o coletor de preços...")
