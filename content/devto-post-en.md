---
title: "How to Query CNPJ, CPF, and Run Automated KYC in Brazil via API"
published: true
tags: [api, brazil, kyc, compliance]
cover_image: https://dabradata.com/og-image.png
canonical_url: https://dabradata.com/guias/como-consultar-cnpj-api
---

Automating Brazilian public data queries should be simple. In practice, anyone who has tried knows each government agency uses a different format, different authentication, different availability. Receita Federal goes down occasionally. PGFN has obscure rate limits. Sanctions lists each have their own search rules.

This post shows how to do it cleanly in Python, Node.js, and cURL, with working examples you can run at zero cost using a test key.

## What you can query via API

**Companies (CNPJ):**
- Receita Federal data (company name, CNAE, status, address, shareholders/QSA)
- Beneficial ownership (UBO) and corporate links
- Certificates (federal tax CND, labor CNDT, FGTS)
- Federal tax debt (PGFN)
- CGU sanctions (CEIS, CNEP) and improbity convictions (CNIA)
- Lawsuits, TCU records, environmental compliance (IBAMA)

**Individuals (CPF):**
- Receita Federal data
- Politically Exposed Persons (PEP)
- Restrictive lists: 17 national and international lists resolved by CPF
- Federal Police criminal record certificate
- Lawsuits and arrest warrants (CNJ)

**International sanctions (by name):**
- OFAC (USA), UN, EU, UK, Canada, Switzerland, Australia, Interpol, FBI, FinCEN

133 queries in total, plus SMS and OTP sending, all under one API key.

## Test key first, live key later

Every account gets two keys. The test key (`dabra_test_...`) validates parameters exactly like production and returns each endpoint's example response at zero cost, flagged with the `X-Example: true` header. Build the integration with it, then swap in the live key (`dabra_live_...`).

(Keys issued before 2026-09-24 start with `fd_live_`/`fd_test_` and keep working. No need to rotate.)

## Basic CNPJ query

Parameters go in the query string. CNPJ and CPF are accepted with or without punctuation:

```bash
curl -H "X-API-Key: dabra_test_YOUR_KEY" \
  "https://app.dabradata.com/api/v1/consulta/receita-federal-pj?cnpj=00000000000191"
```

Returns JSON with company name, tax status, CNAE, address, share capital, opening date and the shareholder list (QSA). Cost with a live key: R$ 0.43.

In Python:

```python
import os
import requests

API_KEY = os.environ["DABRA_API_KEY"]

def query_cnpj(cnpj: str) -> dict:
    r = requests.get(
        "https://app.dabradata.com/api/v1/consulta/receita-federal-pj",
        params={"cnpj": cnpj},
        headers={"X-API-Key": API_KEY},
        timeout=60,
    )
    if not r.ok:
        err = r.json()["error"]
        raise RuntimeError(f"HTTP {r.status_code} {err['code']}: {err['message']}")
    print(f"Cost: R$ {r.headers.get('X-Request-Cost')}")
    return r.json()

data = query_cnpj("00.000.000/0001-91")
print(data["razao_social"])
print(data["descricao_situacao_cadastral"])
```

In Node.js (18+, no dependencies):

```javascript
async function queryCNPJ(cnpj) {
  const url = new URL('https://app.dabradata.com/api/v1/consulta/receita-federal-pj');
  url.searchParams.set('cnpj', cnpj);
  const res = await fetch(url, { headers: { 'X-API-Key': process.env.DABRA_API_KEY } });
  const body = await res.json();
  if (!res.ok) throw new Error(`HTTP ${res.status} ${body.error.code}`);
  return body;
}
```

## Parallel KYC in Python

For due diligence or regulatory onboarding, you typically need to fire multiple checks at once. `ThreadPoolExecutor` makes this clean:

```python
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE    = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": os.environ["DABRA_API_KEY"]}

KYC_CHECKS = {
    "identity":          "receita-federal-pf",
    "pep":               "pep-exposicao",
    "restrictive_lists": "listas-restritivas",
    "ceis":              "ceis-sancoes",
    "criminal":          "antecedentes-federais",
    "lawsuits":          "processos-agrupada",
    "warrants":          "cnj-mandados-prisao",
}

def check(name, endpoint, cpf):
    r = requests.get(f"{BASE}/{endpoint}", params={"cpf": cpf}, headers=HEADERS, timeout=120)
    return name, r.status_code, r.headers.get("X-Request-Cost")

def kyc(cpf: str):
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(check, n, ep, cpf) for n, ep in KYC_CHECKS.items()]
        for f in as_completed(futures):
            name, status, cost = f.result()
            print(f"  {name}: HTTP {status} | R$ {cost}")

kyc("123.456.789-09")
```

Total list price for this individual KYC: R$ 6.00 (seven queries). The same pattern works for companies: swap in CNPJ endpoints, and query international sanctions lists by the company name returned by Receita Federal.

One rule worth hard-coding: a failed query (timeout, source offline) is never a clean result. Treat it as inconclusive, not as "nothing found".

## Why one API instead of integrating each agency directly

The alternative is integrating each agency individually: Receita Federal, CGU, PGFN, TST, TSE, Banco Central, OFAC, and so on. Each one has its own format, authentication, rate limits, and availability. Maintaining those integrations is the actual work, not the business logic.

[Dabra](https://dabradata.com) consolidates them into a single REST API with one API key and prepaid, per-query pricing.

## Useful response headers

Every successful call returns:

```
X-Request-Cost: 0.43              # amount deducted
X-Balance-Remaining: 47.23        # remaining balance
X-RateLimit-Remaining-RPM: 58     # requests left this minute
X-Response-Time-Ms: 312           # processing time
```

You can build a per-query cost dashboard just by reading these headers.

## Also available over MCP

The same queries are exposed as a remote MCP server at `https://app.dabradata.com/mcp`, with OAuth login, for Claude, ChatGPT and Cursor. Same prices, same balance, and every paid call asks for cost confirmation first.

## Code examples

Full working examples in Python, Node.js, PHP, Go and cURL:

**[github.com/DabraData/api-examples](https://github.com/DabraData/api-examples)**

Includes complete flows for company due diligence, candidate background checks, batch supplier compliance, SMS/OTP and webhook signature verification.

## Getting started

Free account, no credit card, pay per query: **[app.dabradata.com/signup](https://app.dabradata.com/signup)**

Full API reference (133 queries, with prices): **[dabradata.com/docs](https://dabradata.com/docs)**

OpenAPI spec: **[app.dabradata.com/api/v1/openapi.json](https://app.dabradata.com/api/v1/openapi.json)**

---

Questions about a specific use case or integration? Drop a comment.
