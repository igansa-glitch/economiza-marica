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

# --- ESTILO ---
st.markdown("""<style>.stButton>button {border-radius: 8px; font-weight: bold; background-color: #28a745; color: white;}</style>""", unsafe_allow_html=True)

# --- CARREGAMENTO E LIMPEZA TURBO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            # 1. Filtro de Lixo: Remove linhas onde o produto ou mercado são apenas ruído
            lixo = ['promoção', 'cada', 'unidade', 'unid', 'un', 'kg', 'g', ';', ':', 'promocão']
            df_temp = df_temp[~df_temp['produto'].str.lower().isin(lixo)]
            df_temp = df_temp[~df_temp['mercado'].str.lower().isin(lixo)]
            
            # 2. Remove Duplicados (Mesmo preço no mesmo mercado)
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')

            def classificar_setor(row):
                prod = str(row.get('produto', '')).lower()
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'sobrecoxa', 'porco', 'bife']): return "Açougue"
                if any(x in prod for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'sal', 'biscoito']): return "Mercearia"
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'creme de leite', 'leite condensado']): return "Laticínios"
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'coca', 'fanta', 'skol', 'brahma']): return "Bebidas"
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'fralda', 'omo']): return "Limpeza"
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO E PROPAGANDAS) ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total = 0
        txt_wa = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {sub:,.2f} no {item['mercado']}")
            txt_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {sub:,.2f}\n"
            if st.button("❌", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total Estimado", f"R$ {total:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(txt_wa + f'\n💰 *Total: R$ {total:,.2f}*')}"
        st.link_button("📲 Enviar WhatsApp", link_wa)

    st.markdown("---")
    # ESPAÇO PARA PROPAGANDA
    st.image("https://via.placeholder.com/300x150.png?text=DANIPARFUN+PERFUMES", use_container_width=True)
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes em Maricá com preços imbatíveis!")
    st.info("📢 **Anuncie aqui!**\nSua marca no maior comparador de preços da cidade.")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            df_s = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            
            if not df_s.empty:
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
                                if st.button("🛒", key=k_btn):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.rerun()
            else:
                st.write("Nenhum item nesta categoria.")
else:
    st.warning("🤖 Aguardando dados do robô...")
