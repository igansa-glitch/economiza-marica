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

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp {background-color: #f4f7f6;}
    .prop-box {background-color: #ffffff; padding: 12px; text-align: center; border: 2px dashed #007bff; border-radius: 8px; margin-bottom: 15px; color: #333;}
    .whats-link {color: #25d366; font-weight: bold; text-decoration: none; font-size: 1.1em;}
    .card-produto {border-left: 5px solid #007bff; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    .nome-prod {font-size: 0.95em !important; font-weight: bold; color: #333; text-transform: uppercase; margin-bottom: 8px; display: block;}
    .preco-valor {color: #27ae60; font-weight: 800; font-size: 1.2em;}
    .nome-mercado {font-weight: 600; color: #555; font-size: 0.9em;}
    </style>
    """, unsafe_allow_html=True)

# --- FILTRO DE QUALIDADE ---
def validar_dados(row):
    n = str(row.get('produto', '')).upper().strip()
    m = str(row.get('mercado', '')).upper().strip()
    if any(x in m for x in ['LOCAL', 'COMÉRCIO', 'DESCONHECIDO']): return None
    if any(x in n for x in [';', '%', '!', 'ICOA', 'PACV']) or len(n) < 4: return None
    return n

# --- CARREGAMENTO ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        df_temp = pd.DataFrame(res.data)
        if not df_temp.empty:
            df_temp['produto_valido'] = df_temp.apply(validar_dados, axis=1)
            df_temp = df_temp.dropna(subset=['produto_valido'])
            df_temp['produto'] = df_temp['produto_valido']
            df_temp = df_temp.drop_duplicates(subset=['produto', 'mercado', 'preco'], keep='first')
            
            def categorizar(p):
                p = p.lower()
                if any(x in p for x in ['arroz', 'feijão', 'óleo', 'açúcar', 'macarrão', 'café', 'dona elza']): return "Mercearia"
                if any(x in p for x in ['carne', 'frango', 'bife', 'picanha', 'filé', 'linguiça']): return "Açougue"
                if any(x in p for x in ['leite', 'queijo', 'iogurte', 'manteiga', 'requeijão']): return "Laticínios"
                if any(x in p for x in ['refrigerante', 'cerveja', 'suco', 'água', 'coca', 'original']): return "Bebidas"
                if any(x in p for x in ['fralda', 'sabão', 'detergente', 'omo', 'papel']): return "Limpeza"
                return "Outros"
            
            df_temp['setor'] = df_temp['produto'].apply(categorizar)
            return df_temp
        return pd.DataFrame()
    except: return pd.DataFrame()

df = carregar_dados()

# --- BARRA LATERAL (CARRINHO DETALHADO + WHATSAPP) ---
with st.sidebar:
    st.header("🛒 Sua Lista")
    if not st.session_state.carrinho:
        st.info("Lista vazia.")
    else:
        total_geral = 0
        texto_whatsapp = "🛒 *Minha Lista de Compras - Economiza Maricá*\n\n"
        
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_geral += subtotal
            
            # Mostra os valores individuais
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {item['preco']:.2f} cada no {item['mercado']} | Sub: R$ {subtotal:.2f}")
            
            # Monta o texto para o WhatsApp
            texto_whatsapp += f"• {item['qtd']}x {item['nome']} ({item['mercado']}) - R$ {subtotal:.2f}\n"
            
            if st.button("Remover", key=f"side_del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_geral:,.2f}")
        
        # Botão do WhatsApp para enviar a lista
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whatsapp + f'\n💰 *Total: R$ {total_geral:.2f}*')}"
        st.link_button("📲 Enviar Lista p/ WhatsApp", link_wa, type="primary")

    st.markdown("---")
    st.markdown(f'<div class="prop-box"><b>ANUNCIE AQUI</b><br>(21) 98288-1425<br>WhatsApp</div>', unsafe_allow_html=True)

# --- CONTEÚDO PRINCIPAL ---
st.markdown(f'<div class="prop-box">📢 <b>FAÇA SUA PROPAGANDA AQUI</b><br>Contato: (21) 98288-1425<br><a href="https://wa.me/5521982881425" class="whats-link">WhatsApp Comercial</a></div>', unsafe_allow_html=True)

st.title("📍 Economiza Maricá")

c1, c2 = st.columns([2, 1])
with c1:
    busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Arroz...")
with c2:
    bairros = ["Todos os Bairros", "Centro", "Itaipuaçu", "Inoã", "São José", "Ponta Negra"]
    bairro_sel = st.selectbox("📍 Filtrar Bairro", bairros)

if not df.empty:
    df_f = df.copy()
    if busca:
        df_f = df_f[df_f['produto'].str.contains(busca, case=False)]
    if bairro_sel != "Todos os Bairros":
        df_f = df_f[df_f['bairro'] == bairro_sel]

    setores = ["Todos", "Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza", "Outros"]
    abas = st.tabs(setores)

    for i, aba in enumerate(abas):
        with aba:
            nome_s = setores[i]
            df_s = df_f if nome_s == "Todos" else df_f[df_f['setor'] == nome_s]
            
            if not df_s.empty:
                for p in df_s['produto'].unique():
                    ofertas = df_s[df_s['produto'] == p].sort_values(by='preco')
                    with st.container():
                        st.markdown(f'<div class="card-produto"><span class="nome-prod">{p}</span>', unsafe_allow_html=True)
                        for _, row in ofertas.iterrows():
                            col1, col2, col3, col4 = st.columns([2.5, 1.2, 0.8, 0.5])
                            with col1:
                                st.write(f"🏪 **{row['mercado']}** ({row['bairro']})")
                            with col2:
                                st.markdown(f'<span class="preco-valor">R$ {row["preco"]:,.2f}</span>', unsafe_allow_html=True)
                            with col3:
                                qtd = st.number_input("Qtd", 1, 99, 1, key=f"q_{nome_s}_{row['id']}", label_visibility="collapsed")
                            with col4:
                                if st.button("🛒", key=f"b_{nome_s}_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": qtd, "mercado": row['mercado']})
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"Nenhuma oferta em {nome_s}.")
else:
    st.warning("🤖 Aguardando novos dados...")
