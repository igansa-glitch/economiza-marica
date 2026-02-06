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

# --- CARREGAMENTO E CLASSIFICAÇÃO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        
        if not df_temp.empty:
            # Limpeza de lixo visual
            lixo = ['promoção', 'cada', 'unidade', 'unid', 'un', 'kg', 'g', ';', ':', 'promocão']
            df_temp = df_temp[~df_temp['produto'].str.lower().isin(lixo)]
            
            # Remove duplicados
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')

            def classificar_setor(row):
                prod = str(row.get('produto', '')).lower()
                
                # MERCEARIA (Prioridade para tirar o Óleo das Bebidas)
                if any(x in prod for x in ['óleo', 'soja', 'arroz', 'feijão', 'açúcar', 'macarrão', 'café', 'farinha', 'sal', 'biscoito', 'molho', 'extrato']):
                    return "Mercearia"
                
                # BEBIDAS (Refinado)
                if any(x in prod for x in ['refrigerante', 'cerveja', 'suco', 'vinho', 'água', 'coca', 'fanta', 'skol', 'brahma', 'heineken', 'guaraná', 'antarctica', 'original', 'sem açúcar', '1,5l', '2l', 'litro']):
                    return "Bebidas"
                
                # AÇOUGUE
                if any(x in prod for x in ['carne', 'frango', 'alcatra', 'picanha', 'linguiça', 'coxa', 'maminha', 'costela', 'fígado', 'asa', 'sobrecoxa', 'porco', 'bife']):
                    return "Açougue"
                
                # LATICÍNIOS
                if any(x in prod for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão', 'creme de leite', 'leite condensado', 'margarina', 'presunto', 'mussarela']):
                    return "Laticínios"
                
                # LIMPEZA
                if any(x in prod for x in ['sabão', 'detergente', 'amaciante', 'papel', 'desinfetante', 'veja', 'cloro', 'fralda', 'omo', 'brilhante', 'shampoo']):
                    return "Limpeza"
                
                return "Outros"

            df_temp['setor'] = df_temp.apply(classificar_setor, axis=1)
            
            # Ajuste de nomes incompletos (Trata o "original/sem açúcar")
            def ajustar_nome(nome):
                n = nome.lower()
                if "original" in n and "açúcar" in n and len(n) < 30:
                    return "Refrigerante Coca-Cola 1,5L (Variações)"
                return nome
            
            df_temp['produto'] = df_temp['produto'].apply(ajustar_nome)
            
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Vazia")
    else:
        total = 0
        txt_wa = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            txt_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {sub:,.2f}\n"
            if st.button("❌", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.divider()
        st.metric("Total", f"R$ {total:,.2f}")
        st.link_button("📲 Enviar WhatsApp", f"https://wa.me/?text={urllib.parse.quote(txt_wa + f'\n💰 *Total: R$ {total:,.2f}*')}")

    st.markdown("---")
    st.image("https://via.placeholder.com/300x150.png?text=DANIPARFUN+PERFUMES", use_container_width=True)
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.title("📍 Economiza Maricá")

if not df.empty:
    busca = st.text_input("🔍 Procure um produto...", placeholder="Ex: Alcatra, Cerveja, Arroz...")
    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            df_s = df if nome_setor == "Todos" else df[df['setor'] == nome_setor]
            if busca:
                df_s = df_s[df_s['produto'].str.contains(busca, case=False)]
            
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
                st.write("Nenhum item aqui.")
else:
    st.warning("🤖 Aguardando novos dados do robô...")
    
