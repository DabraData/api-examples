"""Regenera openapi.yaml e Dabra.postman_collection.json a partir da API viva.

A fonte da verdade e a propria API:
  - https://app.dabradata.com/api/v1/openapi.json  (especificacao OpenAPI)
  - https://app.dabradata.com/api/v1/docs          (catalogo: precos, exemplos)

Uso:
    pip install requests pyyaml
    python scripts/atualizar_referencia.py

Os dois arquivos gerados sao snapshots. Em caso de divergencia, vale a API viva.
"""
import datetime
import json
import pathlib

import requests
import yaml

BASE = "https://app.dabradata.com"
RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Valores das variaveis da colecao. A chave de teste (dabra_test_) aceita
# qualquer valor com formato valido e devolve o exemplo do endpoint a custo zero.
VARIAVEIS = {
    "baseUrl": BASE,
    "API_KEY": "dabra_test_SUA_CHAVE",
    "CPF": "12345678909",
    "CNPJ": "00000000000191",
    "NOME": "Fulano de Tal",
    "PLACA": "ABC1D23",
    "CEP": "01310100",
    "CELULAR": "5511999999999",
}
PARAM_VAR = {"cpf": "CPF", "cnpj": "CNPJ", "nome": "NOME", "placa": "PLACA", "cep": "CEP"}


def baixar(caminho: str) -> dict:
    r = requests.get(f"{BASE}{caminho}", timeout=60)
    r.raise_for_status()
    return r.json()


def gerar_openapi(spec: dict, hoje: str) -> None:
    cabecalho = (
        "# Snapshot da especificacao OpenAPI da Dabra.\n"
        f"# Fonte: {BASE}/api/v1/openapi.json (baixado em {hoje}).\n"
        "# Em caso de divergencia, vale a URL viva. Para atualizar:\n"
        "#   python scripts/atualizar_referencia.py\n"
    )
    corpo = yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, width=100)
    (RAIZ / "openapi.yaml").write_text(cabecalho + corpo, encoding="utf-8")


def _valor(param: dict, ep: dict) -> str:
    var = PARAM_VAR.get(param["nome"])
    if param["nome"] == "numero" and ep["categoria"] == "mensageria":
        var = "CELULAR"
    if param["nome"] == "mensagem":
        return "Mensagem de teste"
    if var:
        return "{{" + var + "}}"
    ex = str(param.get("example") or "")
    return "" if ex.startswith("SEU_") or ex.startswith("SUA_") else ex


def _parametros_ativos(ep: dict) -> set:
    """Obrigatorios + o primeiro de cada grupo 'informe um de'."""
    ativos = {p["nome"] for p in ep["parametros"] if p.get("obrigatorio")}
    for grupo in ep.get("grupos_obrigatorios") or []:
        if not ativos.intersection(grupo):
            # Em grupo cpf/cnpj, CNPJ primeiro: e o caso mais comum nas consultas mistas.
            ativos.add("cnpj" if "cnpj" in grupo else grupo[0])
    return ativos


def _request(ep: dict) -> dict:
    ativos = _parametros_ativos(ep)
    caminho = ep["url"].strip("/").split("/")
    descricao = (
        f"{ep['descricao']}\n\nPreco: {ep['preco'].replace('.', ',')} por {ep.get('unidade') or 'consulta'}."
        f"\nDocumentacao: https://dabradata.com{ep['doc_url']}"
    )
    req = {
        "method": ep["metodo"],
        "header": [{"key": "Accept", "value": "application/json"}],
        "description": descricao,
    }
    if ep["metodo"] == "POST":
        corpo = {p["nome"]: _valor(p, ep) for p in ep["parametros"] if p["nome"] in ativos}
        req["header"].append({"key": "Content-Type", "value": "application/json"})
        req["body"] = {"mode": "raw", "raw": json.dumps(corpo, ensure_ascii=False, indent=2),
                       "options": {"raw": {"language": "json"}}}
        query = []
    else:
        query = [{"key": p["nome"], "value": _valor(p, ep), "disabled": p["nome"] not in ativos,
                  "description": p.get("descricao", "")} for p in ep["parametros"]]
    raw = "{{baseUrl}}/" + "/".join(caminho)
    ativos_q = [q for q in query if not q["disabled"]]
    if ativos_q:
        raw += "?" + "&".join(f"{q['key']}={q['value']}" for q in ativos_q)
    req["url"] = {"raw": raw, "host": ["{{baseUrl}}"], "path": caminho, "query": query}
    item = {"name": f"{ep['nome']} ({ep['slug']})", "request": req}
    if ep.get("exemplo_resposta") is not None:
        item["response"] = [{
            "name": "Exemplo (chave de teste, X-Example: true)",
            "originalRequest": req,
            "status": "OK",
            "code": 200,
            "_postman_previewlanguage": "json",
            "header": [{"key": "Content-Type", "value": "application/json"},
                       {"key": "X-Example", "value": "true"}],
            "body": json.dumps(ep["exemplo_resposta"], ensure_ascii=False, indent=2),
        }]
    return item


def gerar_postman(catalogo: dict, hoje: str) -> None:
    rotulos = {c["chave"]: c["rotulo"] for c in catalogo["categorias_ordenadas"]}
    ordem = [c["chave"] for c in catalogo["categorias_ordenadas"]]
    pastas = {}
    for ep in sorted(catalogo["endpoints"], key=lambda e: e["nome"]):
        pastas.setdefault(ep["categoria"], []).append(_request(ep))
    chaves = ordem + sorted(k for k in pastas if k not in ordem)
    colecao = {
        "info": {
            "name": "Dabra API",
            "description": (
                f"{catalogo['total_endpoints']} consultas da API Dabra, geradas do catalogo vivo "
                f"({BASE}/api/v1/docs) em {hoje}.\n\n"
                "Configure a variavel API_KEY. Com uma chave de teste (dabra_test_...) cada "
                "chamada devolve o exemplo do endpoint a custo zero, com o header X-Example: true. "
                "Com a chave de producao (dabra_live_...) a consulta e real e cobrada.\n\n"
                "Documentacao: https://dabradata.com/docs"
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {"type": "apikey", "apikey": [
            {"key": "key", "value": "X-API-Key", "type": "string"},
            {"key": "value", "value": "{{API_KEY}}", "type": "string"},
            {"key": "in", "value": "header", "type": "string"},
        ]},
        "variable": [{"key": k, "value": v} for k, v in VARIAVEIS.items()],
        "item": [{"name": rotulos.get(k, k), "item": pastas[k]} for k in chaves if k in pastas],
    }
    (RAIZ / "Dabra.postman_collection.json").write_text(
        json.dumps(colecao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    hoje = datetime.date.today().isoformat()
    spec = baixar("/api/v1/openapi.json")
    catalogo = baixar("/api/v1/docs")
    gerar_openapi(spec, hoje)
    gerar_postman(catalogo, hoje)
    print(f"openapi.yaml: {len(spec['paths'])} rotas")
    print(f"Dabra.postman_collection.json: {len(catalogo['endpoints'])} consultas")


if __name__ == "__main__":
    main()
