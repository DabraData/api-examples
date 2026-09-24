#!/bin/bash
# Dabra - Enviar SMS e codigo OTP
# Uso: DABRA_API_KEY=dabra_live_... ./sms.sh 5511999999999
# Os endpoints de mensageria sao POST com corpo JSON. Numero com DDI e DDD, so digitos.
API_KEY="${DABRA_API_KEY:-dabra_test_SUA_CHAVE}"
BASE="https://app.dabradata.com/api/v1/consulta"
NUMERO="${1:-5511999999999}"

echo "=== Enviar SMS - R\$ 0,29 por credito de 160 caracteres ==="
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d "{\"numero\": \"$NUMERO\", \"mensagem\": \"Seu pedido foi aprovado.\", \"reference\": \"pedido-123\"}" \
  "$BASE/sms-enviar" | python3 -m json.tool

echo "=== Enviar codigo OTP - R\$ 0,29 ==="
curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d "{\"numero\": \"$NUMERO\"}" \
  "$BASE/otp-send" | python3 -m json.tool

# Depois que a pessoa digitar o codigo (gratis):
# curl -s -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
#   -d '{"request_id": "otp_...", "codigo": "123456"}' "$BASE/otp-verify"
