#!/bin/bash
# Dabra - Consultar CPF
# Uso: DABRA_API_KEY=dabra_live_... ./cpf.sh 123.456.789-09
# Com a chave de teste (dabra_test_...) a resposta e o exemplo do endpoint, a custo zero.
API_KEY="${DABRA_API_KEY:-dabra_test_SUA_CHAVE}"
BASE="https://app.dabradata.com/api/v1/consulta"
CPF=$(echo "${1:-12345678909}" | tr -d '.-')

echo "=== Consulta basica CPF - R\$ 0,24 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/dados-cadastrais-basicos?cpf=$CPF" | python3 -m json.tool

echo "=== Receita Federal PF (tempo real) - R\$ 0,54 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/receita-federal-pf?cpf=$CPF" | python3 -m json.tool
