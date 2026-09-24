# Dabra - Compliance de fornecedores em lote
# Custo de referencia: R$ 2,59 por CNPJ (5 consultas, precos de tabela em 24/09/2026)
# pip install requests
#
# Uso: python compliance_fornecedor.py fornecedores.csv   (coluna "cnpj")
#
# Cada CNPJ sai como APROVADO, REPROVADO ou INCONCLUSIVO. Uma consulta que falhou
# (timeout, fonte fora do ar) nunca conta como "nada consta": vira INCONCLUSIVO.
# Para volumes maiores sem codigo, o painel tem o enriquecimento em lote por CSV:
# https://dabradata.com/lote
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

# endpoint -> funcao que devolve True quando a resposta aponta um problema
CHECKS = {
    "receita-federal-pj": lambda d: d.get("descricao_situacao_cadastral") != "ATIVA",  # R$ 0,43
    "ceis-sancoes":       lambda d: bool(d.get("constamSancoes")),                     # R$ 0,43
    "cnep-sancoes":       lambda d: bool(d.get("constamSancoes")),                     # R$ 0,43
    "pgfn-devedores":     lambda d: bool(d.get("possuiDivida")),                       # R$ 0,43
    "ccd-pj":             lambda d: d.get("regularidadeFiscal") is False,              # R$ 0,87
}


def _check(endpoint, cnpj):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", params={"cnpj": cnpj}, headers=HEADERS, timeout=120)
    except requests.RequestException as e:
        return endpoint, "erro", str(e)
    if r.status_code == 200:
        return endpoint, ("problema" if CHECKS[endpoint](r.json()) else "ok"), None
    erro = r.json().get("error", {}) if r.headers.get("Content-Type", "").startswith("application/json") else {}
    if r.status_code == 404 and erro.get("code") == "not_found":
        # Documento sem registro na base consultada.
        return endpoint, "sem_registro", erro.get("message")
    return endpoint, "erro", f"HTTP {r.status_code} {erro.get('code')}: {erro.get('message')}"


def avaliar(cnpj: str) -> dict:
    resultados = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        for f in as_completed([ex.submit(_check, ep, cnpj) for ep in CHECKS]):
            endpoint, situacao, detalhe = f.result()
            resultados[endpoint] = {"situacao": situacao, "detalhe": detalhe}
    problemas = [ep for ep, r in resultados.items() if r["situacao"] == "problema"]
    falhas = [ep for ep, r in resultados.items() if r["situacao"] == "erro"]
    if problemas:
        status = "REPROVADO"
    elif falhas:
        status = "INCONCLUSIVO"
    else:
        status = "APROVADO"
    return {"cnpj": cnpj, "timestamp": datetime.now().isoformat(), "status": status,
            "problemas": problemas, "falhas": falhas, "resultados": resultados}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8-sig") as f:
            cnpjs = [row["cnpj"] for row in csv.DictReader(f)]
    else:
        cnpjs = ["00000000000191", "33000167000101"]

    print("=== RELATORIO ===")
    for cnpj in cnpjs:
        item = avaliar(cnpj)
        extra = ""
        if item["problemas"]:
            extra += f" | problemas: {', '.join(item['problemas'])}"
        if item["falhas"]:
            extra += f" | sem resposta: {', '.join(item['falhas'])}"
        print(f"  {cnpj}: {item['status']}{extra}")
