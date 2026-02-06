import st_javascript as st_js # Biblioteca para o GPS
import streamlit as st
import pandas as pd
from supabase import create_client
import urllib.parse
from math import radians, cos, sin, asin, sqrt

# --- CONEXÃO ---
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

st.set_page_config(page_title="Economiza Maricá", layout="wide", page_icon="📍")

# --- FUNÇÃO GPS (COORDENADAS DE MARICÁ) ---
coordenadas_bairros = {
    "Centro": (-22.9194, -42.8186),
    "Inoã": (-22.9271, -42.9161),
    "Itaipuaçu": (-22.9519, -42.9242),
    "Ponta Negra": (-22.9536, -42.6842),
    "São José": (-22.9344, -42.8447)
}

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine para distância entre dois pontos
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6371 * c
    return km

# --- CAPTURA LOCALIZAÇÃO ---
st.sidebar.markdown("### 📍 Sua Localização")
loc = st_js.st_javascript("navigator.geolocation.getCurrentPosition(success => { return {lat: success.coords.latitude, lon: success.coords.longitude} });")

user_lat, user_lon = None, None
if loc and isinstance(loc, dict) and 'lat' in loc:
    user_lat, user_lon = loc['lat'], loc['lon']
    st.sidebar.success("GPS Ativado!")
else:
    st.sidebar.warning("Ative o GPS para ver os mercados mais próximos.")

# --- CARREGAR DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        res = supabase.table("ofertas").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = carregar_dados()

# --- INTERFACE ---
st.title("📍 Economiza Maricá")
st.caption(f"Atualizado em: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

# --- LISTAGEM COM DISTÂNCIA ---
if not df.empty:
    tab_promo, tab_setores = st.tabs(["🔥 SUPER OFERTAS", "📦 TODOS OS PRODUTOS"])

    with tab_setores:
        busca = st.text_input("🔍 O que você procura?", placeholder="Ex: Alcatra, Feijão...")
        df_f = df[df['produto'].str.contains(busca, case=False)] if busca else df
        
        for _, row in df_f.iterrows():
            dist_texto = ""
            if user_lat and row['bairro'] in coordenadas_bairros:
                b_lat, b_lon = coordenadas_bairros[row['bairro']]
                dist = calcular_distancia(user_lat, user_lon, b_lat, b_lon)
                dist_texto = f" 📏 a {dist:.1f} km de você"

            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.5, 1.2])
                with c1:
                    st.markdown(f"**{row['produto']}**")
                    st.caption(f"🏪 {row['mercado']} | 📍 {row['bairro']}{dist_texto}")
                with c2:
                    st.subheader(f"R$ {row['preco']:,.2f}")
                with c3:
                    if st.button("🛒", key=f"b_{row['id']}"):
                        st.toast("Adicionado ao carrinho!")

# (Restante do código do carrinho e propagandas mantido...)
