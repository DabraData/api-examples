# Dabra - Consultar CPF em Python
# pip install requests
#
# Chave: variavel de ambiente DABRA_API_KEY. Com a chave de teste (dabra_test_...)
# a resposta e o exemplo do endpoint, a custo zero, com o header X-Example: true.
import os
import sys

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"


def consultar_cpf(cpf: str) -> dict:
    """Receita Federal PF (R$ 0,54): consulta ao vivo na fonte oficial."""
    r = requests.get(f"{BASE_URL}/receita-federal-pf", params={"cpf": cpf},
                     headers={"X-API-Key": API_KEY}, timeout=60)
    if not r.ok:
        erro = r.json().get("error", {})
        raise RuntimeError(f"HTTP {r.status_code} {erro.get('code')}: {erro.get('message')}")
    print(f"Custo: R$ {r.headers.get('X-Request-Cost')} | Saldo: R$ {r.headers.get('X-Balance-Remaining')}")
    return r.json()


if __name__ == "__main__":
    dados = consultar_cpf(sys.argv[1] if len(sys.argv) > 1 else "123.456.789-09")
    print(f"Nome:       {dados.get('nomePessoaFisica')}")
    print(f"Situacao:   {dados.get('situacaoCadastral')}")
    print(f"Nascimento: {dados.get('dataNascimento')}")
    print(f"Validacao:  {dados.get('link_validacao')}")
