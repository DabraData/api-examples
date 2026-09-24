# Dabra - KYC Pessoa Fisica
# Custo de referencia: R$ 6,43 por pessoa (8 consultas, precos de tabela em 24/09/2026)
# pip install requests
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

CHECKS = {
    "identidade":         "receita-federal-pf",     # R$ 0,54
    "pep":                "pep-exposicao",          # R$ 0,43
    "listas_restritivas": "listas-restritivas",     # R$ 1,49 (17 listas, inclui OFAC/ONU/UE)
    "ceis":               "ceis-sancoes",           # R$ 0,43
    "antecedentes":       "antecedentes-federais",  # R$ 0,60
    "processos":          "processos-agrupada",     # R$ 1,65
    "mandados":           "cnj-mandados-prisao",    # R$ 0,86
    "tse":                "tse-situacao",           # R$ 0,43
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


def kyc_pf(cpf: str) -> dict:
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
    print(f"KYC PF para CPF {cpf}:\n")
    kyc_pf(cpf)
