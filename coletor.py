import httpx
from supabase import create_client

URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"
supabase = create_client(URL_DB, KEY_DB)

def enviar(produto, preco, mercado, bairro, setor):
    dados = {"produto": produto, "preco": preco, "mercado": mercado, "bairro": bairro, "setor": setor}
    supabase.table("ofertas").insert(dados).execute()
    print(f"✅ Enviado: {produto} em {mercado}")

print("🤖 Iniciando Robô de Maricá...")

# Teste manual para ver se o banco recebe
enviar("Leite Longa Vida", 5.49, "Supermarket", "Centro", "Laticínios")
enviar("Arroz 5kg", 24.90, "Grand Marché", "Itaipuaçu", "Mercearia")

print("🚀 Tudo pronto!")