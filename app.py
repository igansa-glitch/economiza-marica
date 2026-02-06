import streamlit as st
from st_javascript import st_javascript
import pandas as pd
from supabase import create_client
import urllib.parse
from math import radians, cos, sin, asin, sqrt

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

# --- LÓGICA DE DISTÂNCIA ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2)) 
    return 6371 * d

coordenadas_bairros = {
    "Centro": (-22.9194, -42.8186),
    "Inoã": (-22.9271, -42.9161),
    "Itaipuaçu": (-22.9519, -42.9242),
    "Ponta Negra": (-22.9536, -42.6842),
    "São José": (-22.9344, -42.8447)
}

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- SIDEBAR (GPS E CARRINHO) ---
with st.sidebar:
    st.header("📍 Localização")
    # Comando JS para pegar o GPS
    js_gps = "navigator.geolocation.getCurrentPosition(s => {window.parent.postMessage({type:'streamlit:setComponentValue', value:{lat:s.coords.latitude, lon:s.coords.longitude}}, '*')});"
    loc = st_javascript(js_gps)
    
    u_lat, u_lon = None, None
    if isinstance(loc, dict) and 'lat' in loc:
        u_lat, u_lon = loc['lat'], loc['lon']
        st.success("GPS Ativado!")
    else:
        st.info("Aguardando GPS...")

    st.divider()
    st.header("🛒 Minha Lista")
    if not st.session_state.carrinho:
        st.write("Vazia")
    else:
        total = 0
        txt_wa = "🛒 *Lista Economiza Maricá*\n\n"
        for i, item in enumerate(st.session_state.carrinho):
            sub = item['preco'] * item['qtd']
            total += sub
            st.write(f"**{item['qtd']}x** {item['nome']}")
            st.caption(f"R$ {sub:,.2f} no {item['mercado']}")
            txt_wa += f"• {item['qtd']}x {item['nome']} ({item['mercado']})\n"
            if st.button("Remover", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()
        st.metric("Total", f"R$ {total:,.2f}")
        st.link_button("📲 Enviar WhatsApp", f"https://wa.me/?text={urllib.parse.quote(txt_wa)}")

# --- CONTEÚDO ---
st.title("📍 Economiza Maricá")

@st.cache_data(ttl=60)
def carregar():
    try:
        r = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(r.data)
    except: return pd.DataFrame()

df = carregar()

if not df.empty:
    tab1, tab2 = st.tabs(["🔥 SUPER OFERTAS", "📦 PRODUTOS"])
    
    with tab2:
        busca = st.text_input("🔍 O que busca?")
        df_f = df[df['produto'].str.contains(busca, case=False)] if busca else df
        
        for _, row in df_f.iterrows():
            dist_txt = ""
            if u_lat and row['bairro'] in coordenadas_bairros:
                b_lat, b_lon = coordenadas_bairros[row['bairro']]
                d = calcular_distancia(u_lat, u_lon, b_lat, b_lon)
                dist_txt = f" | 📏 {d:.1f} km"

            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.5, 1.2])
                c1.markdown(f"**{row['produto']}**\n\n🏪 {row['mercado']}{dist_txt}")
                c2.subheader(f"R$ {row['preco']:,.2f}")
                if c3.button("🛒", key=f"b_{row['id']}"):
                    st.session_state.carrinho.append({"nome": row['produto'], "preco": row['preco'], "qtd": 1, "mercado": row['mercado']})
                    st.rerun()
else:
    st.warning("Aguardando dados do robô...")
