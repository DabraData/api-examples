# Dabra - Consultar CNPJ em Python
# pip install requests
import requests

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"


def consultar_cnpj(cnpj: str) -> dict:
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    r = requests.get(
        f"{BASE_URL}/consulta-cnpj-receita/{cnpj}",
        headers={"X-API-Key": API_KEY},
        timeout=30,
    )
    r.raise_for_status()
    print(f"Custo: R$ {r.headers.get('X-Request-Cost')} | Saldo: R$ {r.headers.get('X-Balance-Remaining')}")
    return r.json()


def consultar_cnpj_com_qsa(cnpj: str) -> dict:
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    r = requests.get(f"{BASE_URL}/receita-federal-pj-qsa/{cnpj}", headers={"X-API-Key": API_KEY}, timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    dados = consultar_cnpj("00.000.000/0001-91")
    print(f"Razao social: {dados.get('razao_social')}")
    print(f"Situacao:     {dados.get('situacao_cadastral')}")
