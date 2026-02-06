import streamlit as st
from st_javascript import st_javascript
import pandas as pd
from supabase import create_client
import urllib.parse
from math import radians, cos, sin, asin, sqrt

# --- CONEXÃO COM O BANCO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button {border-radius: 8px; width: 100%;}
    .main {background-color: #f5f7f9;}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE GEOLOCALIZAÇÃO ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    return 6371 * c

coordenadas_bairros = {
    "Centro": (-22.9194, -42.8186),
    "Inoã": (-22.9271, -42.9161),
    "Itaipuaçu": (-22.9519, -42.9242),
    "Ponta Negra": (-22.9536, -42.6842),
    "São José": (-22.9344, -42.8447)
}

# Inicializa Carrinho
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- BARRA LATERAL (GPS, CARRINHO E PROPAGANDA) ---
with st.sidebar:
    st.header("📍 Sua Localização")
    # Captura GPS via JS
    loc = st_javascript("navigator.geolocation.getCurrentPosition(s => {window.parent.postMessage({type:'streamlit:setComponentValue', value:{lat:s.coords.latitude, lon:s.coords.longitude}}, '*')});")
    
    user_lat, user_lon = None, None
    if isinstance(loc, dict) and 'lat' in loc:
        user_lat, user_lon = loc['lat'], loc['lon']
        st.success("GPS Ativado!")
    else:
        st.info("Aguardando sinal do GPS...")

    st.divider()
    
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Sua lista está vazia.")
    else:
        total_lista = 0
        texto_whats = "🛒 *Minha Lista - Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            subtotal = item['preco'] * item['qtd']
            total_lista += subtotal
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {subtotal:,.2f} no {item['mercado']}")
            texto_whats += f"• {item['qtd']}x {item['nome']} - {item['mercado']} (R$ {subtotal:,.2f})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        
        st.divider()
        st.metric("Total Estimado", f"R$ {total_lista:,.2f}")
        link_wa = f"https://wa.me/?text={urllib.parse.quote(texto_whats + f'\n💰 *Total: R$ {total_lista:,.2f}*')}"
        st.link_button("📲 Enviar p/ WhatsApp", link_wa)
        
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()
    
    st.markdown("---")
    st.warning("🛍️ **Daniparfun.com.br**\nPerfumes Árabes em Maricá!")

# --- CONTEÚDO PRINCIPAL ---
st.info("📢 **Anuncie aqui:** Contato: (21) 9XXXX-XXXX")
st.title("📍 Economiza Maricá")

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

if not df.empty:
    tab_promo, tab_setores = st.tabs(["🔥 SUPER OFERTAS", "📦 TODOS OS PRODUTOS"])

    with tab_promo:
        st.markdown("#### Itens com maior economia hoje")
        # Lógica de economia
        df['media'] = df.groupby('produto')['preco'].transform('mean')
        df['diff'] = (df['media'] - df['preco']) / df['media']
        promos = df[df['diff'] > 0.05].sort_values(by='diff', ascending=False)

        if not promos.empty:
            cols = st.columns(3)
            for idx, row in promos.head(6).iterrows():
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.error(f"Economize {row['diff']*100:.0f}%")
                        st.write(f"**{row['produto']}**")
                        st.subheader(f"R$ {row['preco']:,.2f}")
                        st.caption(f"🏪 {row['mercado']}")
                        if st.button("Adicionar", key=f"p_{row['id']}"):
                            st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                            st.rerun()
        else:
            st.info("O robô está cruzando os preços para encontrar as melhores ofertas!")

    with tab_setores:
        busca = st.text_input("🔍 Buscar produto...", placeholder="Ex: Feijão, Arroz, Picanha...")
        df_f = df[df['produto'].str.contains(busca, case=False)] if busca else df
        
        setores = ["Açougue", "Mercearia", "Laticínios", "Bebidas", "Limpeza & Higiene", "Outros"]
        tabs_s = st.tabs(setores)

        for i, s in enumerate(setores):
            with tabs_s[i]:
                dados_s = df_f[df_f['setor'] == s]
                if not dados_s.empty:
                    for _, row in dados_s.iterrows():
                        dist_txt = ""
                        if user_lat and row['bairro'] in coordenadas_bairros:
                            b_lat, b_lon = coordenadas_bairros[row['bairro']]
                            d = calcular_distancia(user_lat, user_lon, b_lat, b_lon)
                            dist_txt = f" | 📏 {d:.1f} km"

                        with st.container(border=True):
                            c1, c2, c3 = st.columns([3, 1.5, 1.2])
                            with c1:
                                st.markdown(f"**{row['produto']}**")
                                st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}{dist_txt}")
                            with c2:
                                st.subheader(f"R$ {row['preco']:,.2f}")
                            with c3:
                                q = st.number_input("Qtd", 1, 20, 1, key=f"q_{row['id']}")
                                if st.button("🛒", key=f"b_{row['id']}"):
                                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": q, "mercado": row['mercado']})
                                    st.rerun()
                else:
                    st.write("Nenhum item encontrado neste setor.")
else:
    st.warning("⚠️ O banco de dados está sendo atualizado pelo robô IA. Volte em instantes!")

st.markdown("---")
st.caption(f"📍 Economiza Maricá - Atualizado em {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
