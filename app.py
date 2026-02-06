import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse

# --- CONEXÃO COM O BANCO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="🛒")

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- ESTILO ---
st.markdown("""<style>.stButton>button {border-radius: 8px; font-weight: bold; height: 3em; background-color: #007bff; color: white;}</style>""", unsafe_allow_html=True)

# --- CARREGAMENTO E LIMPEZA DE DUPLICADOS ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            # 1. REMOVE DUPLICADOS: Mantém apenas uma linha por produto em cada mercado
            # Isso limpa o erro de aparecer o mesmo preço 3 vezes
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')

            def classificar_setor(row):
                prod = str(row.get('produto', '')).lower().strip()
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'sobrecoxa', 'porco', 'lombo', 'bife']):
                    return "Açougue"
                if any(x in prod for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'molho', 'biscoito', 'leite em pó', 'maionese', 'sal']):
                    return "Mercearia"
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela', 'creme de leite', 'leite condensado']):
                    return "Laticínios"
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'guaraná', 'coca', 'fanta', 'skol', 'brahma', 'heineken']):
                    return "Bebidas"
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'shampoo', 'sabonete', 'fralda', 'omo']):
                    return "Limpeza"
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            
            # Limpa lixo
            termos_lixo = ['cada', 'unidade', 'un', 'kg', 'g', 'unid']
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
        st.info("Vazia")
    else:
        total = 0
        txt_wa = "🛒 *Lista Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            txt_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']})\n"
            if st.button("Remover", key=f"s_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.metric("Total", f"R$ {total:,.2f}")
        st.link_button("📲 WhatsApp", f"https://wa.me/?text={urllib.parse.quote(txt_wa)}")

    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            df_s = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            
            if not df_s.empty:
                # Agrupa por produto para o comparativo
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
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.rerun()
            else:
                st.write("Nenhum item aqui.")
else:
    st.warning("🤖 Aguardando dados...")
