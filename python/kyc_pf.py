# Dabra - KYC completo Pessoa Fisica
# Custo estimado: ~R$ 9,00 por pessoa
# pip install requests
import requests, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS  = {"X-API-Key": API_KEY}

CHECKS = {
    "identidade":     "receita-federal-pf",
    "pep":            "pep-exposicao",
    "pep_estendida":  "pep-estendida",
    "ceis":           "ceis-sancoes",
    "ofac":           "ofac-sancoes",
    "onu":            "onu-sancoes",
    "antecedentes":   "antecedentes-criminais",
    "processos":      "processos-agrupada",
    "mandados":       "cnj-mandados-prisao",
    "tse":            "tse-situacao",
}


def _check(name, endpoint, cpf):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}/{cpf}", headers=HEADERS, timeout=30)
        return name, {"status": r.status_code, "data": r.json() if r.ok else None, "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "error", "error": str(e)}


def kyc_pf(cpf: str) -> dict:
    cpf = cpf.replace(".", "").replace("-", "")
    results = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(_check, n, ep, cpf): n for n, ep in CHECKS.items()}
        for f in as_completed(futures):
            name, result = f.result()
            results[name] = result
            icon = "OK" if result["status"] == 200 else "FALHOU"
            print(f"  [{icon}] {name}: custo=R${result.get('cost','N/A')}")
    return results


if __name__ == "__main__":
    cpf = sys.argv[1] if len(sys.argv) > 1 else "12345678900"
    print(f"KYC PF para CPF {cpf}:\n")
    kyc_pf(cpf)
