# Dabra - KYC completo Pessoa Juridica
# Custo estimado: ~R$ 15,09 por empresa (sem socios)
# pip install requests
import requests, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS  = {"X-API-Key": API_KEY}

CHECKS = {
    "cnpj_qsa":         "receita-federal-pj-qsa",
    "beneficiario":     "beneficiario-final",
    "ceis":             "ceis-sancoes",
    "cnep":             "cnep-sancoes",
    "trabalho_forcado": "trabalho-forcado",
    "pgfn":             "pgfn-devedores",
    "cnd":              "cnd-debitos",
    "cndt":             "tst-cndt",
    "fgts":             "fgts-regularidade",
    "processos":        "processos-completa",
    "ofac":             "ofac-sancoes",
}


def _check(name, endpoint, doc):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}/{doc}", headers=HEADERS, timeout=60)
        return name, {"status": r.status_code, "data": r.json() if r.ok else None, "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "error", "error": str(e)}


def kyc_pj(cnpj: str) -> dict:
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(_check, n, ep, cnpj): n for n, ep in CHECKS.items()}
        for f in as_completed(futures):
            name, result = f.result()
            results[name] = result
            icon = "OK" if result["status"] == 200 else "FALHOU"
            print(f"  [{icon}] {name}: custo=R${result.get('cost','N/A')}")
    return results


if __name__ == "__main__":
    cnpj = sys.argv[1] if len(sys.argv) > 1 else "00000000000191"
    print(f"KYC PJ para CNPJ {cnpj}:\n")
    kyc_pj(cnpj)
