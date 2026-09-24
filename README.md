# Dabra - API Examples

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![133 consultas](https://img.shields.io/badge/consultas-133-blue)](https://dabradata.com/docs)
[![Docs](https://img.shields.io/badge/docs-dabradata.com-teal)](https://dabradata.com/docs)

Exemplos de integracao com a [API da Dabra](https://dabradata.com): 133 consultas de dados
brasileiros (CNPJ, CPF, KYC, compliance, processos judiciais, credito, sancoes internacionais)
e envio de SMS/OTP, por uma API REST pre-paga, com uma unica chave.

## Inicio rapido

1. Crie a conta em [app.dabradata.com/signup](https://app.dabradata.com/signup). Sem cartao de
   credito e sem mensalidade: voce paga por consulta, com saldo pre-pago.
2. Na pagina de chaves do painel ha duas chaves:
   - **teste** (`dabra_test_...`): aceita qualquer valor com formato valido e devolve o exemplo
     de resposta do endpoint, a custo zero, marcado com o header `X-Example: true`. A validacao
     de parametros e a mesma da producao. Use para montar a integracao.
   - **producao** (`dabra_live_...`): consulta real, debitada do saldo.
3. Rode um exemplo:

```bash
curl -H "X-API-Key: dabra_test_SUA_CHAVE" \
  "https://app.dabradata.com/api/v1/consulta/receita-federal-pj?cnpj=00000000000191"
```

Todos os exemplos leem a chave da variavel de ambiente `DABRA_API_KEY`:

```bash
export DABRA_API_KEY=dabra_test_SUA_CHAVE
python python/cnpj.py 00.000.000/0001-91
```

## Formato das chamadas

```
GET https://app.dabradata.com/api/v1/consulta/<slug>?<parametro>=<valor>
X-API-Key: <sua chave>
```

- Os parametros vao na **querystring** (`?cpf=...`, `?cnpj=...`, `?nome=...`). CPF e CNPJ
  aceitam com ou sem pontuacao.
- Algumas consultas pedem "um de" (por exemplo `cpf` **ou** `cnpj`); a pagina de cada consulta
  diz quais parametros sao obrigatorios.
- As listas internacionais (OFAC, ONU, UE, Reino Unido, FBI, Interpol) sao consultadas por
  `nome`. Para pessoa fisica com CPF, `listas-restritivas` cruza 17 listas nacionais e
  internacionais pelo documento.
- Mensageria (`sms-enviar`, `otp-send`, `otp-verify`, `otp-resend`, `sms-status`) e mais algumas
  consultas usam `POST` com corpo JSON.
- A resposta de sucesso e o JSON da consulta, sem envelope.
- Para repetir uma chamada com seguranca, envie `X-Idempotency-Key`: a mesma chave devolve a
  resposta original sem cobrar de novo.

Referencia completa, com preco, parametros e exemplo de resposta de cada consulta:
[dabradata.com/docs](https://dabradata.com/docs). Toda pagina da referencia tambem existe em
markdown, no mesmo endereco com `.md` no fim.

## Exemplos por linguagem

| Linguagem | Pasta | Dependencias | Rodar |
|---|---|---|---|
| cURL (bash) | [`/curl`](./curl) | nenhuma | `./curl/cnpj.sh 00000000000191` |
| Python | [`/python`](./python) | `pip install -r python/requirements.txt` | `python python/cnpj.py` |
| Node.js | [`/nodejs`](./nodejs) | Node 18+, sem deps | `node nodejs/cnpj.js` |
| PHP | [`/php`](./php) | PHP 7.4+, ext-curl | `php php/cnpj.php` |
| Go | [`/go`](./go) | Go 1.21+, stdlib | `go run go/cnpj.go` |

## Casos de uso

Custos de referencia pela tabela publica em 24/09/2026. O custo real de cada chamada vem no
header `X-Request-Cost`; os precos atuais estao em [dabradata.com/pricing](https://dabradata.com/pricing).

| Caso | Custo | Python | Node.js | PHP | Go | cURL |
|---|---|---|---|---|---|---|
| Consultar CNPJ (Receita Federal + QSA) | R$ 0,43 | `cnpj.py` | `cnpj.js` | `cnpj.php` | `cnpj.go` | `cnpj.sh` |
| Consultar CPF (Receita Federal) | R$ 0,54 | `cpf.py` | - | - | - | `cpf.sh` |
| KYC pessoa fisica | R$ 6,43 (Python) / R$ 6,00 | `kyc_pf.py` | `kyc_pf.js` | `kyc_pf.php` | `kyc_pf.go` | - |
| KYC pessoa juridica | R$ 11,27 | `kyc_pj.py` | - | - | - | - |
| Due diligence de empresa | R$ 15,52 | `due_diligence.py` | - | - | - | - |
| Background check de candidato | R$ 4,75 | `background_check.py` | - | - | - | - |
| Compliance de fornecedores (CSV) | R$ 2,59 por CNPJ | `compliance_fornecedor.py` | - | - | - | - |
| Sancoes internacionais | R$ 3,31 por nome | - | - | - | - | `sancoes.sh` |
| Enviar SMS e OTP | R$ 0,29 por credito | - | - | - | - | `sms.sh` |
| Receber webhook (verificar assinatura) | gratis | `webhook_assinatura.py` | - | - | - | - |

## Headers de resposta

| Header | Descricao |
|---|---|
| `X-Request-Cost` | Custo debitado nesta chamada, em BRL |
| `X-Balance-Remaining` | Saldo restante apos a chamada |
| `X-RateLimit-Limit-RPM` / `X-RateLimit-Remaining-RPM` | Limite e restante por minuto |
| `X-RateLimit-Limit-RPD` / `X-RateLimit-Remaining-RPD` | Limite e restante por dia |
| `X-Response-Time-Ms` | Tempo de processamento |
| `X-Example` | `true` quando a resposta e o exemplo da chave de teste |
| `X-Idempotent-Replay` | `true` quando a resposta veio de uma `X-Idempotency-Key` repetida |

## Erros

Todo erro tem o mesmo envelope:

```json
{"error": {"code": "insufficient_balance", "message": "...", "hint": "...", "details": {}}}
```

| HTTP | `code` | Quando |
|---|---|---|
| 400 | `invalid_parameters` | Parametro ausente ou em formato invalido |
| 401 | `unauthorized` | Chave ausente ou invalida |
| 402 | `insufficient_balance` | Saldo insuficiente; `details` traz `required_brl` e `available_brl` |
| 403 | `email_not_verified`, `kyc_required` | Conta ainda nao liberada para consultar (e-mail ou verificacao pendente) |
| 404 | `not_found` | Slug inexistente, ou documento sem registro na base consultada |
| 429 | `rate_limit_exceeded` | Limite de requisicoes; respeite o header `Retry-After` |
| 5xx | varia | A fonte nao respondeu. Uma falha nunca significa "nada consta" |

Em regra, erro nao e cobrado. Algumas fontes cobram mesmo quando nao ha registro para o documento;
nesses casos o custo vem em `X-Request-Cost`, como numa resposta de sucesso.

## Saldo

```bash
curl -H "X-API-Key: $DABRA_API_KEY" https://app.dabradata.com/api/v1/administrative/balance
```

Resposta com cache de 60 segundos; as respostas das consultas ja trazem o saldo no header
`X-Balance-Remaining`. Ver [dabradata.com/docs/administrativo/saldo](https://dabradata.com/docs/administrativo/saldo).

## Webhooks

Eventos disponiveis: `sms.mo.received`, `sms.optout` e `topup.credited`. Cada entrega e assinada
com HMAC-SHA256 do corpo bruto no header `X-Dabra-Signature: sha256=<hex>`. Por compatibilidade, o
mesmo valor tambem e enviado em `X-FonteData-Signature` durante 12 meses (a partir de 24/09/2026):
valide o header novo e use o legado so como fallback. Retentativas por 24 horas; deduplique por
`event_id`. Exemplo em [`python/webhook_assinatura.py`](./python/webhook_assinatura.py) e
documentacao em [dabradata.com/docs/webhooks](https://dabradata.com/docs/webhooks).

## MCP

As mesmas consultas estao disponiveis para Claude, ChatGPT, Cursor e outros clientes MCP, pelo
servidor remoto:

```
https://app.dabradata.com/mcp
```

Login por OAuth 2.1 no navegador, sem colar chave. O preco e o saldo sao os mesmos da API REST, e
toda execucao pede confirmacao do custo antes de debitar. Ver
[dabradata.com/docs/mcp](https://dabradata.com/docs/mcp).

## Outros produtos

- **Lote**: enriquecimento de uma planilha CSV inteira pelo painel, sem codigo. Formato dos
  arquivos: [dabradata.com/docs/lote](https://dabradata.com/docs/lote).
- **Dossie**: relatorio de uma pessoa ou empresa por finalidade (credito, contratacao, due
  diligence), com parecer e fontes citadas: [dabradata.com/dossie](https://dabradata.com/dossie).
- **SMS e OTP**: remetente white-label, OTP gerenciado e respostas do destinatario por webhook:
  [dabradata.com/sms](https://dabradata.com/sms).

## OpenAPI e Postman

- Especificacao viva: [app.dabradata.com/api/v1/openapi.json](https://app.dabradata.com/api/v1/openapi.json)
- Catalogo vivo, com precos e exemplos: [app.dabradata.com/api/v1/docs](https://app.dabradata.com/api/v1/docs)
- [`openapi.yaml`](./openapi.yaml) e [`Dabra.postman_collection.json`](./Dabra.postman_collection.json)
  sao snapshots gerados dessas URLs por [`scripts/atualizar_referencia.py`](./scripts/atualizar_referencia.py).
  Em caso de divergencia, vale a URL viva.

No Postman, importe a colecao e preencha a variavel `API_KEY`. Com a chave de teste, cada
requisicao devolve o exemplo do endpoint sem custo.

## Continuidade

Dabra e a marca da FONTEDATA TECNOLOGIA LTDA (CNPJ 67.011.070/0001-16), antes apresentada como
FonteData. A empresa, a conta, o saldo e a API sao os mesmos; so mudaram o nome e os enderecos.

- Chaves novas comecam com `dabra_live_` ou `dabra_test_`. Chaves emitidas antes de 24/09/2026
  comecam com `fd_live_` ou `fd_test_` e continuam validas; nao e preciso trocar.
- Este repositorio era `FonteData/api-examples` e agora e `DabraData/api-examples`. O GitHub
  redireciona o endereco antigo, mas atualize o remote:
  `git remote set-url origin https://github.com/DabraData/api-examples.git`.

## Links

- Documentacao: https://dabradata.com/docs
- Precos: https://dabradata.com/pricing
- Criar conta: https://app.dabradata.com/signup
- Suporte: contato@dabradata.com ou WhatsApp https://wa.me/5511991220174

## Contribuindo

Veja [CONTRIBUTING.md](./CONTRIBUTING.md). Exemplos em novas linguagens sao bem-vindos.
