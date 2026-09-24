# Dabra - Due Diligence completa de empresa
# Custo estimado: ~R$ 17,58 por empresa
# pip install requests
import requests, json, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS  = {"X-API-Key": API_KEY}

CHECKS = {
    "cadastral_qsa":    "receita-federal-pj-qsa",
    "beneficiario":     "beneficiario-final",
    "pgfn":             "pgfn-devedores",
    "cnd":              "cnd-debitos",
    "cndt":             "tst-cndt",
    "fgts":             "fgts-regularidade",
    "cadin":            "cadin-federal",
    "ceis":             "ceis-sancoes",
    "cnep":             "cnep-sancoes",
    "trabalho_forcado": "trabalho-forcado",
    "improbidade":      "cnia-improbidade",
    "processos":        "processos-completa",
    "tcu":              "tcu-consolidada",
    "ibama_reg":        "ibama-regularidade",
    "ibama_embargo":    "ibama-embargo",
    "ibama_debitos":    "ibama-debitos",
    "ofac":             "ofac-sancoes",
    "onu":              "onu-sancoes",
    "ue":               "eu-sancoes",
}


def _fetch(endpoint, doc):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}/{doc}", headers=HEADERS, timeout=60)
        return endpoint, {"status": r.status_code, "data": r.json() if r.ok else None, "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return endpoint, {"status": "error", "error": str(e)}


def due_diligence(cnpj: str, output_file: str = None) -> dict:
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")
    results = {"cnpj": cnpj, "timestamp": datetime.now().isoformat(), "checks": {}}
    custo_total = 0.0

    print(f"Due diligence: {cnpj}")
    print("-" * 40)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(_fetch, ep, cnpj_limpo): name for name, ep in CHECKS.items()}
        for f in as_completed(futures):
            name, result = f.result()
            results["checks"][name] = result
            custo = float(result.get("cost") or 0)
            custo_total += custo
            icon = "OK" if result["status"] == 200 else "FALHOU"
            print(f"  [{icon}] {name:<22} R$ {custo:.2f}")

    results["custo_total"] = round(custo_total, 2)
    print(f"\nCusto total: R$ {custo_total:.2f}")
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Salvo em: {output_file}")
    return results


if __name__ == "__main__":
    cnpj = sys.argv[1] if len(sys.argv) > 1 else "00000000000191"
    output = sys.argv[2] if len(sys.argv) > 2 else f"dossie_{cnpj.replace('.','').replace('/','').replace('-','')}.json"
    due_diligence(cnpj, output_file=output)
