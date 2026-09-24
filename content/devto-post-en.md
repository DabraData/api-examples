---
title: "How to Query CNPJ, CPF, and Run Automated KYC in Brazil via API"
published: true
tags: [api, brazil, kyc, compliance]
cover_image: https://dabradata.com/og-image.png
canonical_url: https://dabradata.com/guias/como-consultar-cnpj-api
---

Automating Brazilian public data queries should be simple. In practice, anyone who has tried knows each government agency uses a different format, different authentication, different availability. Receita Federal goes down occasionally. PGFN has obscure rate limits. OFAC returns XML from 1999.

This post shows how to do it cleanly in Python, Node.js, and cURL — with real working examples.

## What you can query via API

**Companies (CNPJ):**
- Receita Federal data (company name, CNAE, status, address, shareholders/QSA)
- Certifications (CND, CNDT, FGTS)
- Federal tax debt (PGFN)
- CGU sanctions (CEIS, CNEP)
- Judicial records (TJ, TRF, TRT)
- Environmental compliance (IBAMA)

**Individuals (CPF):**
- Receita Federal data
- Politically Exposed Persons (PEP)
- Criminal records
- Judicial records
- Arrest warrants (CNJ)

**International sanctions:**
- OFAC (USA), UN, EU, UK, Interpol, FBI, FinCEN

## Basic CNPJ query

The most common endpoint — Receita Federal company data:

```bash
curl -H "X-API-Key: dabra_live_YOUR_KEY" \
  https://app.dabradata.com/api/v1/consulta/consulta-cnpj-receita/00000000000191
```

Returns JSON with company name, tax status, CNAE, address, capital, opening date. Cost: R$ 0.16.

(Keys issued before 2026-09-24 start with `fd_live_`/`fd_test_` instead and keep working — no need to rotate.)

In Python:

```python
import requests

def query_cnpj(cnpj: str) -> dict:
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    r = requests.get(
        f"https://app.dabradata.com/api/v1/consulta/consulta-cnpj-receita/{cnpj}",
        headers={"X-API-Key": "dabra_live_YOUR_KEY"},
        timeout=30,
    )
    r.raise_for_status()
    print(f"Cost: R$ {r.headers.get('X-Request-Cost')}")
    return r.json()

data = query_cnpj("00.000.000/0001-91")
print(data["razao_social"])       # BANCO DO BRASIL SA
print(data["situacao_cadastral"]) # ATIVA
```

In Node.js:

```javascript
async function queryCNPJ(cnpj) {
  const clean = cnpj.replace(/[\.\-\/]/g, '');
  const res = await fetch(
    `https://app.dabradata.com/api/v1/consulta/consulta-cnpj-receita/${clean}`,
    { headers: { 'X-API-Key': 'dabra_live_YOUR_KEY' } }
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

## Parallel KYC in Python

For due diligence or regulatory onboarding, you typically need to fire multiple checks simultaneously. `ThreadPoolExecutor` makes this clean:

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "dabra_live_YOUR_KEY"
BASE    = "https://app.dabradata.com/api/v1/consulta"
HEADERS = {"X-API-Key": API_KEY}

KYC_CHECKS = {
    "identity":    "receita-federal-pf",
    "pep":         "pep-exposicao",
    "ceis":        "ceis-sancoes",
    "ofac":        "ofac-sancoes",
    "criminal":    "antecedentes-criminais",
    "judicial":    "processos-agrupada",
}

def check(name, endpoint, cpf):
    r = requests.get(f"{BASE}/{endpoint}/{cpf}", headers=HEADERS, timeout=30)
    return name, r.status_code, r.headers.get("X-Request-Cost")

def kyc(cpf: str):
    cpf = cpf.replace(".", "").replace("-", "")
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(check, n, ep, cpf): n for n, ep in KYC_CHECKS.items()}
        for f in as_completed(futures):
            name, status, cost = f.result()
            print(f"  {name}: HTTP {status} | R$ {cost}")

kyc("123.456.789-00")
```

Total cost for a full individual KYC: ~R$ 9.00 (~$1.80 USD). The same pattern works for companies — just swap the endpoints.

## Why one API instead of integrating each agency directly

The alternative is integrating each government agency individually: Receita Federal, CGU, PGFN, TST, TSE, Banco Central, OFAC, and so on. Each one has its own format, authentication, rate limits, and availability. Maintaining those integrations is the actual work — not the business logic.

[Dabra](https://dabradata.com) consolidates 108+ sources into a single REST API with a unified JSON format and one API key.

## Useful response headers

Every call returns:

```
X-Request-Cost: 0.54          # amount deducted
X-Balance-Remaining: 47.23    # remaining balance
X-Request-Id: req_abc123      # for debugging
X-RateLimit-Remaining-RPM: 58 # requests left this minute
```

You can build a per-query-type cost dashboard just by reading these headers.

## Code examples

Full working examples in Python, Node.js, PHP, and Go:

**[github.com/DabraData/api-examples](https://github.com/DabraData/api-examples)**

Includes complete flows for due diligence, admissional background checks, and batch supplier compliance monitoring.

## Getting started

Free account with R$50 in credits (no credit card): **[app.dabradata.com/signup](https://app.dabradata.com/signup)**

Full API reference (108+ endpoints): **[dabradata.com/docs](https://dabradata.com/docs)**

OpenAPI spec: **[dabradata.com/openapi.yaml](https://dabradata.com/openapi.yaml)**

---

Questions about a specific use case or integration? Drop a comment.
