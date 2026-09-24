# Como contribuir

Contribuicoes sao bem-vindas! Este repositorio aceita exemplos de integracao com a Dabra API em qualquer linguagem.

## Adicionar uma nova linguagem

1. Crie uma pasta com o nome da linguagem (ex: `php/`, `go/`, `ruby/`)
2. Siga o padrao dos exemplos existentes:
   - `cnpj.{ext}` — consulta basica de CNPJ
   - `cpf.{ext}` — consulta basica de CPF
   - `kyc_pf.{ext}` — KYC pessoa fisica
3. Use `dabra_live_SUA_CHAVE` como placeholder da API key
4. Inclua comentario no topo com custo estimado quando relevante
5. Abra um Pull Request com titulo `feat: exemplos em {linguagem}`

## Corrigir um exemplo existente

1. Abra uma issue descrevendo o problema
2. Faca um fork, corrija e abra um PR referenciando a issue

## Padrao de codigo

- Sem dependencias externas quando possivel (use stdlib)
- Tratamento basico de erro (nao silenciar excecoes)
- Mostrar headers `X-Request-Cost` e `X-Balance-Remaining` quando possivel
- Documentacao completa em https://dabradata.com/docs

## Duvidas

WhatsApp: https://wa.me/5511991220174
Email: contato@dabradata.com
