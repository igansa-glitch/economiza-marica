import time
from supabase import create_client

# 1. Configurações do seu banco de dados (Use as mesmas do app.py)
URL_DB = "https://isfnrwxpktsepyebnfiz.supabase.co"
KEY_DB = "sb_publishable_ij80OE6wXneFppa17HsoWw_Bi5kMPv1"

# Conecta com o Supabase
supabase = create_client(URL_DB, KEY_DB)

def enviar_dados_para_marica(produto, preco, mercado, bairro, setor):
    """Função para enviar uma oferta para o banco de dados"""
    dados = {
        "produto": produto,
        "preco": preco,
        "mercado": mercado,
        "bairro": bairro,
        "setor": setor
    }
    try:
        supabase.table("ofertas").insert(dados).execute()
        print(f"✅ Sucesso: {produto} a R$ {preco} no {mercado} ({bairro})")
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")

# --- SIMULAÇÃO DA RONDA DO AGENTE ---
print("🤖 Agente Economiza Maricá a iniciar ronda de preços...")

# Aqui você pode adicionar os preços manualmente para testar o seu app
enviar_dados_para_marica("Alcatra kg", 36.90, "Grand Marché", "Centro", "Açougue")
enviar_dados_para_marica("Feijão 1kg", 6.85, "Princesa", "Itaipuaçu", "Mercearia")
enviar_dados_para_marica("Arroz 5kg", 24.99, "Rede Economia", "Inoã", "Mercearia")

print("\n🚀 Ronda finalizada! Abra o seu link no telemóvel para ver os preços reais.")


