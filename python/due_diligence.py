# Dabra - Due Diligence de empresa
# Custo de referencia: R$ 15,52 por empresa (17 consultas, precos de tabela em 24/09/2026)
# pip install requests
#
# Gera um JSON com todas as respostas e o custo real, somado do header X-Request-Cost.
# Para um relatorio pronto, com parecer e fontes citadas, veja o Dossie: https://dabradata.com/dossie
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

POR_CNPJ = {
    "socios_ubo":     "vinculos-ubo",        # R$ 1,49
    "pgfn":           "pgfn-devedores",      # R$ 0,43
    "cnd_federal":    "ccd-pj",              # R$ 0,87
    "cndt":           "tst-cndt",            # R$ 0,54
    "fgts":           "fgts-regularidade",   # R$ 0,43
    "ceis":           "ceis-sancoes",        # R$ 0,43
    "cnep":           "cnep-sancoes",        # R$ 0,43
    "improbidade":    "cnia-improbidade",    # R$ 0,51
    "processos":      "processos-completa",  # R$ 4,69
    "tcu":            "tcu-consolidada",     # R$ 0,86
    "ibama_reg":      "ibama-regularidade",  # R$ 0,51
    "ibama_embargo":  "ibama-embargo",       # R$ 0,51
    "ibama_debitos":  "ibama-debitos",       # R$ 0,51
}
POR_NOME = {
    "ofac": "ofac-sancoes",  # R$ 0,51
    "onu":  "onu-sancoes",   # R$ 0,51
    "ue":   "eu-sancoes",    # R$ 1,86
}


def _get(name, endpoint, params):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=HEADERS, timeout=120)
        corpo = r.json()
        return name, {"endpoint": endpoint, "status": r.status_code,
                      "data": corpo if r.ok else None,
                      "erro": None if r.ok else corpo.get("error"),
                      "cost": r.headers.get("X-Request-Cost")}
    except Exception as e:
        return name, {"endpoint": endpoint, "status": "erro", "erro": str(e)}


def due_diligence(cnpj: str, output_file: str = None) -> dict:
    results = {"cnpj": cnpj, "timestamp": datetime.now().isoformat(), "checks": {}}
    print(f"Due diligence: {cnpj}")
    print("-" * 44)

    _, cadastro = _get("cadastro", "receita-federal-pj", {"cnpj": cnpj})  # R$ 0,43
    results["checks"]["cadastro"] = cadastro
    razao = (cadastro.get("data") or {}).get("razao_social")

    tarefas = [(n, ep, {"cnpj": cnpj}) for n, ep in POR_CNPJ.items()]
    if razao:
        tarefas += [(n, ep, {"nome": razao}) for n, ep in POR_NOME.items()]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(_get, *t) for t in tarefas]):
            name, result = f.result()
            results["checks"][name] = result

    custo_total = 0.0
    for name, result in results["checks"].items():
        custo = float(result.get("cost") or 0)
        custo_total += custo
        icon = "OK" if result["status"] == 200 else f"HTTP {result['status']}"
        print(f"  [{icon:>8}] {name:<16} R$ {custo:.2f}")
    results["custo_total"] = round(custo_total, 2)
    print(f"\nCusto total: R$ {custo_total:.2f}")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Salvo em: {output_file}")
    return results


if __name__ == "__main__":
    cnpj = sys.argv[1] if len(sys.argv) > 1 else "00000000000191"
    digitos = "".join(c for c in cnpj if c.isalnum())
    output = sys.argv[2] if len(sys.argv) > 2 else f"due_diligence_{digitos}.json"
    due_diligence(cnpj, output_file=output)
