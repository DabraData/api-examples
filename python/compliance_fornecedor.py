# Dabra - Compliance continuo de fornecedores (batch)
# pip install requests
import requests, csv, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

API_KEY = "dabra_live_SUA_CHAVE"
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS  = {"X-API-Key": API_KEY}

CHECKS = {
    "ceis":             "ceis-sancoes",
    "cnep":             "cnep-sancoes",
    "trabalho_forcado": "trabalho-forcado",
    "pgfn":             "pgfn-devedores",
    "ofac":             "ofac-sancoes",
    "onu":              "onu-sancoes",
}


def _check(name, endpoint, doc):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}/{doc}", headers=HEADERS, timeout=30)
        return name, {"status": r.status_code, "ok": r.ok, "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"status": "error", "ok": False}


def compliance_fornecedor(cnpj: str) -> dict:
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(_check, n, ep, cnpj): n for n, ep in CHECKS.items()}
        for f in as_completed(futures):
            name, result = f.result()
            results[name] = result
    return results


def batch(cnpjs: list) -> list:
    report = []
    for cnpj in cnpjs:
        print(f"  Verificando {cnpj}...")
        checks = compliance_fornecedor(cnpj)
        falhas = [n for n, r in checks.items() if not r.get("ok")]
        report.append({"cnpj": cnpj, "timestamp": datetime.now().isoformat(),
                        "status": "REPROVADO" if falhas else "APROVADO", "falhas": falhas})
    return report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            cnpjs = [row["cnpj"] for row in csv.DictReader(f)]
    else:
        cnpjs = ["00000000000191", "33000167000101"]

    relatorio = batch(cnpjs)
    print("\n=== RELATORIO ===")
    for item in relatorio:
        status = "REPROVADO" if item["status"] == "REPROVADO" else "APROVADO"
        extra = f" -- falhas: {', '.join(item['falhas'])}" if item["falhas"] else ""
        print(f"  {item['cnpj']}: {status}{extra}")
