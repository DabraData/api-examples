#!/bin/bash
# Dabra - Sancoes internacionais (OFAC, ONU, UE, UK)
API_KEY="dabra_live_SUA_CHAVE"
BASE="https://app.dabradata.com/api/v1/consulta"
DOC="${1:-12345678900}"

for lista in "ofac-sancoes:OFAC" "onu-sancoes:ONU" "eu-sancoes:UE" "uk-sancoes:UK"; do
  endpoint="${lista%%:*}"; nome="${lista##*:}"
  echo "=== $nome ==="
  curl -s -H "X-API-Key: $API_KEY" "$BASE/$endpoint/$DOC" | python3 -m json.tool
done
