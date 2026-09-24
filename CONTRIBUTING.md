# Como contribuir

Este repositorio aceita exemplos de integracao com a API da Dabra em qualquer linguagem.

## Adicionar uma nova linguagem

1. Crie uma pasta com o nome da linguagem (ex: `ruby/`, `java/`, `csharp/`)
2. Siga o padrao dos exemplos existentes:
   - `cnpj.{ext}` - consulta de CNPJ (`receita-federal-pj`)
   - `cpf.{ext}` - consulta de CPF (`receita-federal-pf`)
   - `kyc_pf.{ext}` - KYC pessoa fisica
3. Leia a chave da variavel de ambiente `DABRA_API_KEY`, com `dabra_test_SUA_CHAVE` como
   valor padrao. Nunca inclua uma chave real no codigo.
4. Parametros vao na querystring: `/api/v1/consulta/<slug>?cnpj=...`
5. Inclua no topo o custo de referencia e a data da tabela de precos usada
6. Abra um Pull Request com titulo `feat: exemplos em {linguagem}`

## Testar sem gastar saldo

Use a chave de teste (`dabra_test_...`, na pagina de chaves do painel). Ela valida os parametros
como em producao e devolve o exemplo de resposta de cada endpoint, a custo zero, com o header
`X-Example: true`.

## Corrigir um exemplo existente

1. Abra uma issue descrevendo o problema
2. Faca um fork, corrija e abra um PR referenciando a issue

## Padrao de codigo

- Sem dependencias externas quando possivel (use a stdlib)
- Tratamento basico de erro: leia o envelope `{"error": {"code", "message"}}` e nao silencie
  excecoes. Uma consulta que falhou nunca deve ser tratada como "nada consta"
- Mostre os headers `X-Request-Cost` e `X-Balance-Remaining` quando possivel
- Nomes de consulta (slugs) e parametros conforme o catalogo vivo:
  https://app.dabradata.com/api/v1/docs

## OpenAPI e Postman

`openapi.yaml` e `Dabra.postman_collection.json` sao gerados. Nao edite a mao; rode:

```bash
pip install requests pyyaml
python scripts/atualizar_referencia.py
```

## Duvidas

Email: contato@dabradata.com
WhatsApp: https://wa.me/5511991220174
