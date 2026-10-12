#!/bin/bash
# Dabra - Consulta com comprovante (CNDT, tst-cndt)
# Uso: DABRA_API_KEY=dabra_live_... ./comprovante.sh 00.000.000/0001-91
# Custo de referencia: R$ 0,54 + 25% so quando o link do comprovante vem (tabela de 24/09/2026).
# O link e aberto (sem chave), vale 7 dias; 202 = ainda sendo preparado, 410 = vencido.
# Com a chave de teste (dabra_test_...) a resposta e o exemplo, sem custo: o link e ficticio.
# Precisa de curl e python3.
API_KEY="${DABRA_API_KEY:-dabra_test_SUA_CHAVE}"
BASE="https://app.dabradata.com/api/v1/consulta"
CNPJ=$(echo "${1:-00000000000191}" | tr -d './-')

RESP=$(curl -s -H "X-API-Key: $API_KEY" "$BASE/tst-cndt?cnpj=$CNPJ&comprovante=1")
LINK=$(echo "$RESP" | python3 -c 'import sys,json; print((json.load(sys.stdin).get("comprovante") or [""])[0])')
if [ -z "$LINK" ]; then
  echo "Sem link de comprovante na resposta (nada cobrado pelo comprovante):" >&2
  echo "$RESP" >&2
  exit 1
fi

for i in 1 2 3 4 5 6; do
  CODE=$(curl -s -L -o comprovante.bin -w '%{http_code}' "$LINK")
  case "$CODE" in
    200) echo "Comprovante salvo em comprovante.bin (tipo pelo Content-Type; geralmente PDF)"; exit 0 ;;
    202) echo "Ainda sendo preparado, tentando de novo em 5 s ($i/6)..."; sleep 5 ;;
    410) echo "Link vencido (7 dias) ou indisponivel: faca uma nova consulta." >&2; exit 1 ;;
    *)   echo "HTTP $CODE ao baixar o comprovante." >&2; exit 1 ;;
  esac
done
echo "Comprovante ainda nao ficou pronto; tente o link mais tarde: $LINK" >&2
exit 1
