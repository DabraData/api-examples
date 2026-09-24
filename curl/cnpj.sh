#!/bin/bash
# Dabra - Consultar CNPJ
# Uso: DABRA_API_KEY=dabra_live_... ./cnpj.sh 00.000.000/0001-91
# Com a chave de teste (dabra_test_...) a resposta e o exemplo do endpoint, a custo zero.
API_KEY="${DABRA_API_KEY:-dabra_test_SUA_CHAVE}"
BASE="https://app.dabradata.com/api/v1/consulta"
CNPJ=$(echo "${1:-00000000000191}" | tr -d './-')

echo "=== Receita Federal PJ (cadastro + QSA) - R\$ 0,43 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/receita-federal-pj?cnpj=$CNPJ" | python3 -m json.tool

echo "=== Receita Federal PJ em tempo real - R\$ 0,54 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/receita-federal-pj-live?cnpj=$CNPJ" | python3 -m json.tool
