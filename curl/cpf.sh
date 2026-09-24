#!/bin/bash
# Dabra - Consultar CPF
API_KEY="dabra_live_SUA_CHAVE"
BASE="https://app.dabradata.com/api/v1/consulta"
CPF=$(echo "${1:-12345678900}" | tr -d '.-')

echo "=== CPF basico - R$ 0,24 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/cadastro-pf-basica/$CPF" | python3 -m json.tool

echo "=== CPF Receita Federal - R$ 0,63 ==="
curl -s -H "X-API-Key: $API_KEY" "$BASE/receita-federal-pf/$CPF" | python3 -m json.tool
