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

# --- FUNÇÃO DE CARREGAMENTO COM INTELIGÊNCIA DE SETORES ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            def classificar_setor(row):
                # Mantém se já estiver correto
                if row.get('setor') in ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza"]:
                    return row['setor']
                
                prod = str(row.get('produto', '')).lower()
                # Regras de Ouro para Maricá
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado']):
                    return "Açougue"
                if any(x in prod for x in ['arroz', 'feijão', 'açúcar', 'óleo', 'macarrão', 'café', 'farinha', 'molho', 'biscoito']):
                    return "Mercearia"
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'presunto', 'mussarela']):
                    return "Laticínios"
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'guaraná', 'coca']):
                    return "Bebidas"
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro']):
                    return "Limpeza"
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            return df_temp
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Tenta carregar os dados
df = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if len(st.session_state.carrinho) == 0:
        st.info("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} no {item['mercado']}")
            texto_whats += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {subtotal:,.2f}\n"
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whats + f'\n💰 *Total: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar WhatsApp", link_wa, type="primary")

    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if df is not None and not df.empty:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Arroz, Picanha...")
    
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            df_setor = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            if busca:
                df_setor = df_setor[df_setor['produto'].str.contains(busca, case=False)]
            
            if not df_setor.empty:
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
                st.write("Nenhum item encontrado nesta categoria.")
else:
    st.warning("🤖 Aguardando dados do robô... Deixe o coletor rodando no PC!")
