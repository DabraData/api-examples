# Dabra - Background Check admissional
# Custo estimado: ~R$ 5,97 por candidato
# pip install requests
import requests, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS  = {"X-API-Key": API_KEY}

CHECKS = {
    "identidade":       "receita-federal-pf",
    "antecedentes":     "antecedentes-criminais",
    "mandados_prisao":  "cnj-mandados-prisao",
    "processos":        "processos-agrupada",
    "situacao_eleit":   "tse-situacao",
    "vinculo_emprego":  "vinculo-empregaticio",
    "trabalho_forcado": "trabalho-forcado",
}


def _check(name, endpoint, cpf):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}/{cpf}", headers=HEADERS, timeout=30)
        return name, {"status": r.status_code, "data": r.json() if r.ok else None, "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "error", "error": str(e)}


def background_check(cpf: str) -> dict:
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
    print(f"Background check para CPF {cpf}:\n")
    background_check(cpf)
