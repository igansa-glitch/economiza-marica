import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO COM O BANCO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

# Inicializa Carrinho
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
                # LATICÍNIOS
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'mortadela', 'salame', 'danone', 'coalhada', 'creme de leite', 'leite condensado', 'margarina']):
                    return "Laticínios"
                # BEBIDAS
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'guaraná', 'coca', 'fanta', 'skol', 'brahma', 'heineken', 'antarctica', 'tônica', 'energético']):
                    return "Bebidas"
                # LIMPEZA
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'shampoo', 'sabonete', 'pasta', 'creme dental', 'fralda', 'omo', 'brilhante']):
                    return "Limpeza"
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            termos_lixo = ['cada', 'unidade', 'un', 'kg', 'g', 'gramas', 'unid']
            df_temp = df_temp[~df_temp['produto'].str.lower().isin(termos_lixo)]
            df_temp = df_temp[df_temp['produto'].str.len() > 2]
            return df_temp
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL ---
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
            texto_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {sub:,.2f}\n"
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_wa + f'\n💰 *Total: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar p/ WhatsApp", link_wa)

    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz...")
    
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            # Filtro de Setor e Busca
            df_s = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            if busca:
                df_s = df_s[df_s['produto'].str.contains(busca, case=False)]
            
            if not df_s.empty:
                # Agrupamento para Comparação
                for prod_nome in df_s['produto'].unique():
                    variacoes = df_s[df_s['produto'] == prod_nome].sort_values(by='preco')
                    
                    with st.container(border=True):
                        st.markdown(f"### {prod_nome}")
                        for _, row in variacoes.iterrows():
                            c1, c2, c3 = st.columns([2.5, 1.5, 1.2])
                            with c1:
                                st.write(f"🏪 **{row['mercado']}**")
                                st.caption(f"📍 {row['bairro']}")
                            with c2:
                                st.subheader(f"R$ {row['preco']:,.2f}")
                            with c3:
                                k_qtd = f"q_{nome_setor}_{row['id']}"
                                k_btn = f"b_{nome_setor}_{row['id']}"
                                qtd = st.number_input("Qtd", 1, 50, 1, key=k_qtd)
                                if st.button("🛒 Adicionar", key=k_btn):
                                    st.session_state.carrinho.append({
                                        "nome": row['produto'], "preco": row['preco'], 
                                        "qtd": qtd, "mercado": row['mercado']
                                    })
                                    st.rerun()
            else:
                st.write("Nenhum item nesta categoria.")
else:
    st.warning("🤖 Aguardando novos dados do robô...")
