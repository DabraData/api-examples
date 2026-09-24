#!/bin/bash
# Dabra - Sancoes internacionais
# Uso: DABRA_API_KEY=dabra_live_... ./sancoes.sh "Nome Completo" [CPF]
#
# As listas internacionais (OFAC, ONU, UE, Reino Unido) sao consultadas por NOME.
# Para pessoa fisica com CPF, listas-restritivas cruza 17 listas nacionais e
# internacionais de uma vez, resolvendo pelo documento.
API_KEY="${DABRA_API_KEY:-dabra_test_SUA_CHAVE}"
BASE="https://app.dabradata.com/api/v1/consulta"
NOME="${1:-Fulano de Tal}"
CPF=$(echo "${2:-}" | tr -d '.-')

for lista in "ofac-sancoes:OFAC (EUA) - R\$ 0,51" "onu-sancoes:ONU - R\$ 0,51" \
             "eu-sancoes:Uniao Europeia - R\$ 1,86" "uk-sancoes:Reino Unido - R\$ 0,43"; do
  endpoint="${lista%%:*}"; rotulo="${lista#*:}"
  echo "=== $rotulo ==="
  curl -s -G -H "X-API-Key: $API_KEY" --data-urlencode "nome=$NOME" "$BASE/$endpoint" | python3 -m json.tool
done

if [ -n "$CPF" ]; then
  echo "=== Listas restritivas por CPF (17 listas) - R\$ 1,49 ==="
  curl -s -H "X-API-Key: $API_KEY" "$BASE/listas-restritivas?cpf=$CPF" | python3 -m json.tool
fi
