# Dabra - Consultar CPF em Python
# pip install requests
import requests, sys

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"


def consultar_cpf(cpf: str) -> dict:
    cpf = cpf.replace(".", "").replace("-", "")
    r = requests.get(f"{BASE_URL}/receita-federal-pf/{cpf}", headers={"X-API-Key": API_KEY}, timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    cpf = sys.argv[1] if len(sys.argv) > 1 else "12345678900"
    dados = consultar_cpf(cpf)
    print(f"Nome:     {dados.get('nome')}")
    print(f"Situacao: {dados.get('situacao')}")
