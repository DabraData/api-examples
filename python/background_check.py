# Dabra - Background check de candidato
# Custo de referencia: R$ 4,75 por candidato (6 consultas, precos de tabela em 24/09/2026)
# pip install requests
#
# Use apenas com base legal e finalidade compativeis com a LGPD e a legislacao trabalhista.
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

CHECKS = {
    "identidade":      "receita-federal-pf",      # R$ 0,54
    "antecedentes":    "antecedentes-federais",   # R$ 0,60
    "mandados_prisao": "cnj-mandados-prisao",     # R$ 0,86
    "processos":       "processos-agrupada",      # R$ 1,65
    "situacao_eleit":  "tse-situacao",            # R$ 0,43
    "historico_prof":  "historico-profissional",  # R$ 0,67
}


def _check(name, endpoint, cpf):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params={"cpf": cpf}, headers=HEADERS, timeout=120)
        corpo = r.json()
        return name, {"status": r.status_code, "data": corpo if r.ok else None,
                      "erro": None if r.ok else corpo.get("error"),
                      "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "erro", "erro": str(e)}


def background_check(cpf: str) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(_check, n, ep, cpf) for n, ep in CHECKS.items()]
        for f in as_completed(futures):
            name, result = f.result()
            results[name] = result
            icon = "OK" if result["status"] == 200 else f"HTTP {result['status']}"
            print(f"  [{icon}] {name}: custo=R$ {result.get('cost') or '0'}")
    return results


if __name__ == "__main__":
    cpf = sys.argv[1] if len(sys.argv) > 1 else "12345678909"
    print(f"Background check para CPF {cpf}:\n")
    background_check(cpf)
