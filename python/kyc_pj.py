# Dabra - KYC Pessoa Juridica
# Custo de referencia: R$ 11,27 por empresa (12 consultas, precos de tabela em 24/09/2026)
# pip install requests
#
# Duas etapas: primeiro o cadastro na Receita (para obter a razao social), depois as
# consultas por CNPJ em paralelo e as listas internacionais, que sao consultadas por nome.
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

POR_CNPJ = {
    "socios_ubo":   "vinculos-ubo",        # R$ 1,49 - QSA com documento completo + 1 nivel indireto
    "ceis":         "ceis-sancoes",        # R$ 0,43
    "cnep":         "cnep-sancoes",        # R$ 0,43
    "pgfn":         "pgfn-devedores",      # R$ 0,43
    "cnd_federal":  "ccd-pj",              # R$ 0,87 - Certidao Conjunta de Debitos
    "cndt":         "tst-cndt",            # R$ 0,54
    "fgts":         "fgts-regularidade",   # R$ 0,43
    "improbidade":  "cnia-improbidade",    # R$ 0,51
    "processos":    "processos-completa",  # R$ 4,69
}
POR_NOME = {
    "ofac": "ofac-sancoes",  # R$ 0,51
    "onu":  "onu-sancoes",   # R$ 0,51
}


def _get(name, endpoint, params):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=HEADERS, timeout=120)
        corpo = r.json()
        return name, {"status": r.status_code, "data": corpo if r.ok else None,
                      "erro": None if r.ok else corpo.get("error"),
                      "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "erro", "erro": str(e)}


def kyc_pj(cnpj: str) -> dict:
    _, cadastro = _get("cadastro", "receita-federal-pj", {"cnpj": cnpj})  # R$ 0,43
    results = {"cadastro": cadastro}
    razao = (cadastro.get("data") or {}).get("razao_social")

    tarefas = [(n, ep, {"cnpj": cnpj}) for n, ep in POR_CNPJ.items()]
    if razao:
        tarefas += [(n, ep, {"nome": razao}) for n, ep in POR_NOME.items()]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(_get, *t) for t in tarefas]):
            name, result = f.result()
            results[name] = result
    for name, result in results.items():
        icon = "OK" if result["status"] == 200 else f"HTTP {result['status']}"
        print(f"  [{icon}] {name}: custo=R$ {result.get('cost') or '0'}")
    return results


if __name__ == "__main__":
    cnpj = sys.argv[1] if len(sys.argv) > 1 else "00000000000191"
    print(f"KYC PJ para CNPJ {cnpj}:\n")
    kyc_pj(cnpj)
