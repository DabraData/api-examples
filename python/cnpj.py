# Dabra - Consultar CNPJ em Python
# pip install requests
#
# Chave: variavel de ambiente DABRA_API_KEY. Com a chave de teste (dabra_test_...)
# a resposta e o exemplo do endpoint, a custo zero, com o header X-Example: true.
import os
import sys

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"


def consultar(slug: str, **params) -> dict:
    r = requests.get(f"{BASE_URL}/{slug}", params=params,
                     headers={"X-API-Key": API_KEY}, timeout=60)
    if r.headers.get("X-Example") == "true":
        print("(chave de teste: resposta de exemplo, sem custo)")
    if not r.ok:
        erro = r.json().get("error", {})
        raise RuntimeError(f"HTTP {r.status_code} {erro.get('code')}: {erro.get('message')}")
    print(f"Custo: R$ {r.headers.get('X-Request-Cost')} | Saldo: R$ {r.headers.get('X-Balance-Remaining')}")
    return r.json()


def consultar_cnpj(cnpj: str) -> dict:
    """Receita Federal PJ (R$ 0,43): cadastro, CNAE, endereco e QSA."""
    return consultar("receita-federal-pj", cnpj=cnpj)  # aceita com ou sem pontuacao


if __name__ == "__main__":
    dados = consultar_cnpj(sys.argv[1] if len(sys.argv) > 1 else "00.000.000/0001-91")
    print(f"Razao social: {dados.get('razao_social')}")
    print(f"Situacao:     {dados.get('descricao_situacao_cadastral')}")
    print(f"CNAE:         {dados.get('cnae_fiscal_descricao')}")
    for socio in dados.get("qsa") or []:
        print(f"  Socio: {socio.get('nome_socio')} ({socio.get('qualificacao_socio')})")
