import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO COM O BANCO DE DADOS ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

# Inicializa o Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO CSS (Compacto, Fontes Menores e Profissional) ---
st.markdown("""
    <style>
    .stApp {background-color: #f4f7f6;}
    .prop-box {background-color: #ffffff; padding: 12px; text-align: center; border: 2px dashed #007bff; border-radius: 8px; margin-bottom: 15px; color: #333;}
    .whats-link {color: #25d366; font-weight: bold; text-decoration: none; font-size: 1.1em;}
    .card-produto {border-left: 5px solid #007bff; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    .nome-prod {font-size: 0.95em !important; font-weight: bold; color: #333; text-transform: uppercase; margin-bottom: 8px; display: block;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.15em;}
    .nome-mercado {font-weight: 600; color: #555; font-size: 0.9em;}
    .bairro-info {font-size: 0.8em; color: #888; margin-left: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE LIMPEZA PESADA (FILTRO ANTI-ERRO) ---
def limpeza_pesada(nome):
    n = str(nome).upper().strip()
    
    # 1. Remove caracteres estranhos do OCR
    for char in [';', ':', '%', '!', '?', '*', '(', ')', '[', ']', '_', '#', '@']:
        n = n.replace(char, '')
    
    # 2. Ignora nomes muito curtos ou que são apenas números (erros de leitura)
    if n.isdigit() or len(n) < 4:
        return None
        
    # 3. Lista de termos que indicam erro de captura (marcas sozinhas ou lixo)
    termos_bloqueados = ['PROMOCÃO', 'OFERTA', 'CADA', 'UNID', 'PREÇO', 'SADIA', 'PERDIGÃO', '500G', '1KG', 'COA2']
    if n in termos_bloqueados:
        return None

    # 4. Correções automáticas de palavras grudadas
    if 'FILÉEDFRPNGO' in n: return "FILÉ DE FRANGO"
    if 'BABYSEC' in n: return "FRALDA BABYSEC ULTRA HIPER"
    
    return n

# --- CARREGAMENTO E CLASSIFICAÇÃO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            # Aplica a limpeza nos nomes
            df_temp['produto'] = df_temp['produto'].apply(limpeza_pesada)
            
            # Remove o lixo (linhas que ficaram vazias após a limpeza)
            df_temp = df_temp.dropna(subset=['produto'])
            
            # Remove duplicados (mesmo produto, mercado e preço)
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            
            # Define o Setor para as abas funcionarem
            def definir_setor(p):
                p = p.lower()
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'filé', 'suíno', 'bovino', 'moída']): return "Açougue"
                if any(x in p for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'sal', 'biscoito', 'molho', 'extrato', 'milho']): return "Mercearia"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'creme de leite', 'leite condensado']): return "Laticínios"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'coca', 'fanta', 'skol', 'brahma', 'heineken']): return "Bebidas"
                if any(x in p for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'fralda', 'omo', 'shampoo', 'sabonete']): return "Limpeza"
                return "Outros"
            
            df_temp['setor'] = df_temp['produto'].apply(definir_setor)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO E PROPAGANDA) ---
with st.sidebar:
    st.header("🛒 Sua Lista")
    if not st.session_state.carrinho:
        st.info("Lista vazia.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            total += item['preco'] * item['qtd']
            st.write(f"**{item['qtd']}x** {item['nome']}")
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
    
    st.markdown("---")
    # Janelas de Propaganda Lateral
    st.markdown(f"""
        <div class="prop-box">
            <b>FAÇA SUA PROPAGANDA AQUI</b><br>
            (21) 98288-1425<br>
            <span style="color:#25d366; font-size:0.8em;">WhatsApp</span>
        </div>
        """, unsafe_allow_html=True)

# --- CONTEÚDO PRINCIPAL ---

# Propaganda Superior
st.markdown(f"""
    <div class="prop-box">
        📢 <b>FAÇA SUA PROPAGANDA AQUI</b><br>
        Contato: (21) 98288-1425<br>
        <a href="https://wa.me/5521982881425" class="whats-link">Clique e Fale no WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

st.title("📍 Economiza Maricá")

# Filtros
c_busca, c_local = st.columns([2, 1])
with c_busca:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz, Leite...")
with c_local:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Região", bairros)

# Abas e Exibição em Escada
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
            # Filtro real por aba
            df_s = df_f if nome_setor == "Todos" else df_f[df_f['setor'] == nome_setor]
            
            if not df_s.empty:
                # Agrupa por produto para a Escada de Preços
                for p in df_s['produto'].unique():
                    ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                    
                    with st.container():
                        st.markdown(f'<div class="card-produto"><span class="nome-prod">{p}</span>', unsafe_allow_html=True)
                        for _, row in ofertas.iterrows():
                            c1, c2
