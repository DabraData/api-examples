# Dabra — API Examples

[![Sync](https://github.com/FonteData/fontedata-portal/actions/workflows/sync-api-examples.yml/badge.svg)](https://github.com/FonteData/fontedata-portal/actions/workflows/sync-api-examples.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![108+ endpoints](https://img.shields.io/badge/endpoints-108%2B-blue)](https://dabradata.com/docs)
[![Docs](https://img.shields.io/badge/docs-dabradata.com-teal)](https://dabradata.com/docs)

> Exemplos praticos de integracao com a [API da Dabra](https://dabradata.com) — a plataforma brasileira de inteligencia de dados com 108+ endpoints de CNPJ, CPF, KYC, compliance, processos judiciais e sancoes internacionais.

## Quick Start

1. **Crie sua conta** em [app.dabradata.com/signup](https://app.dabradata.com/signup) — gratuito, R$50 em creditos, sem cartao
2. **Copie sua API key** no painel
3. **Substitua** `fd_live_SUA_CHAVE` nos exemplos pela sua chave

```bash
curl -H "X-API-Key: fd_live_SUA_CHAVE" \
  https://app.dabradata.com/api/v1/consulta/consulta-cnpj-receita/00000000000191
```

## Exemplos por linguagem

| Linguagem | Pasta | Dependencias |
|---|---|---|
| cURL (bash) | [`/curl`](./curl) | nenhuma |
| Python | [`/python`](./python) | `pip install -r python/requirements.txt` |
| Node.js | [`/nodejs`](./nodejs) | Node 18+, sem deps |
| PHP | [`/php`](./php) | PHP 7.4+, ext-curl |
| Go | [`/go`](./go) | Go 1.21+, stdlib only |

## Casos de Uso

| Caso | Python | Node.js | PHP | Go | cURL |
|---|---|---|---|---|---|
| Consultar CNPJ | `cnpj.py` | `cnpj.js` | `cnpj.php` | `cnpj.go` | `cnpj.sh` |
| Consultar CPF | `cpf.py` | — | — | — | `cpf.sh` |
| KYC Pessoa Fisica | `kyc_pf.py` | `kyc_pf.js` | `kyc_pf.php` | `kyc_pf.go` | — |
| KYC Pessoa Juridica | `kyc_pj.py` | — | — | — | — |
| Due Diligence completa | `due_diligence.py` | — | — | — | — |
| Background Check | `background_check.py` | — | — | — | — |
| Compliance fornecedores | `compliance_fornecedor.py` | — | — | — | — |
| Sancoes internacionais | — | — | — | — | `sancoes.sh` |

## Postman

[![Run in Postman](https://run.pstmn.io/button.svg)](https://dabradata.com/docs)

Importe `Dabra.postman_collection.json` diretamente no Postman. Configure a variavel de ambiente `API_KEY` com sua chave.

## Autenticacao

```
X-API-Key: fd_live_SUA_CHAVE
```

## Headers de resposta uteis

| Header | Descricao |
|---|---|
| `X-Request-Cost` | Custo debitado em BRL |
| `X-Balance-Remaining` | Saldo restante |
| `X-Request-Id` | ID unico para debug |
| `X-RateLimit-Remaining-RPM` | Requisicoes restantes/minuto |

## Links

- Documentacao completa: https://dabradata.com/docs
- Precos: https://dabradata.com/pricing
- Suporte via WhatsApp: https://wa.me/5511991220174
- Criar conta gratis: https://app.dabradata.com/signup

## Contribuindo

Veja [CONTRIBUTING.md](./CONTRIBUTING.md). PRs com exemplos em novas linguagens sao bem-vindos.

---

> Este repositorio e atualizado automaticamente quando a documentacao da Dabra e atualizada.
