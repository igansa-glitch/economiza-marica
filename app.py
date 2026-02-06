import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO COM O BANCO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

# Inicializa Carrinho na memória da sessão
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stButton>button {border-radius: 8px; font-weight: bold; height: 3em; background-color: #007bff; color: white;}
    .stButton>button:hover {background-color: #0056b3; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO E CLASSIFICAÇÃO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            def classificar_setor(row):
                prod = str(row.get('produto', '')).lower().strip()
                
                # AÇOUGUE
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'sobrecoxa', 'porco', 'lombo', 'bife', 'cupim', 'acém', 'paleta', 'peito', 'moída']):
                    return "Açougue"
                # MERCEARIA
                if any(x in prod for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'molho', 'biscoito', 'leite em pó', 'maionese', 'azeite', 'sal', 'extrato', 'espaguete', 'massa', 'tempero', 'milho', 'ervilha']):
                    return "Mercearia"
                # LATICÍNIOS / FRIOS
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'mortadela', 'salame', 'danone', 'coalhada', 'creme de leite', 'leite condensado', 'margarina']):
                    return "Laticínios"
                # BEBIDAS
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'guaraná', 'coca', 'fanta', 'skol', 'brahma', 'heineken', 'antarctica', 'tônica', 'energético', 'latão', 'long neck']):
                    return "Bebidas"
                # LIMPEZA / HIGIENE
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'shampoo', 'sabonete', 'pasta', 'creme dental', 'fralda', 'absorvente', 'lysoform', 'omo', 'brilhante', 'limpador']):
                    return "Limpeza"
                
                return "Outros"

            # Aplica a inteligência de setores
            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            
            # FILTRO CRUCIAL: Remove lixo (nomes que não ajudam o usuário)
            termos_lixo = ['cada', 'unidade', 'un', 'kg', 'g', 'gramas', 'unid', '.', '-', 'promoção']
            df_temp = df_temp[~df_temp['produto'].str.lower().isin(termos_lixo)]
            # Remove produtos com nomes muito curtos (menos de 3 letras) que costumam ser erro de leitura
            df_temp = df_temp[df_temp['produto'].str.len() > 2]
            
            return df_temp
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO E ANÚNCIO) ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.info("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_wa = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total_lista += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {sub:,.2f} no {item['mercado']}")
            texto_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {sub:,.2f}\n"
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa + f'\n💰 *Total: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar p/ WhatsApp", link_wa)
        if st.button("Limpar Tudo"):
            st.session_state.carrinho = []
            st.rerun()

    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nOs melhores perfumes árabes de Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Feijão, Omo...")
    
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
