# Dabra - Receber webhook e verificar a assinatura (stdlib, sem dependencias)
#
# Toda entrega traz o header X-Dabra-Signature: sha256=<hex>, um HMAC-SHA256 do
# corpo BRUTO da requisicao com o segredo de assinatura gerado ao cadastrar o webhook.
# Por compatibilidade, o mesmo valor tambem e enviado em X-FonteData-Signature durante
# 12 meses (a partir de 24/09/2026). Este exemplo le o header novo e so cai no legado
# quando o novo nao vier.
# Documentacao: https://dabradata.com/docs/webhooks/assinatura
#
# Uso: DABRA_WEBHOOK_SECRET=... python webhook_assinatura.py   (escuta em :8080)
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ.get("DABRA_WEBHOOK_SECRET", "seu_segredo_de_assinatura")
HEADER = "X-Dabra-Signature"
HEADER_LEGADO = "X-FonteData-Signature"  # compatibilidade por 12 meses


def header_de_assinatura(headers) -> str:
    """Header novo primeiro; o legado so como fallback (mesmo valor quando os dois vem)."""
    return headers.get(HEADER) or headers.get(HEADER_LEGADO) or ""


def assinatura_valida(corpo_bruto: bytes, header_assinatura: str, secret: str) -> bool:
    esperado = "sha256=" + hmac.new(secret.encode("utf-8"), corpo_bruto, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, header_assinatura or "")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if not assinatura_valida(corpo, header_de_assinatura(self.headers), SECRET):
            self.send_response(401)
            self.end_headers()
            return
        evento = json.loads(corpo)
        # Responda rapido (2xx) e processe depois. Deduplique por event_id: a mesma
        # entrega pode chegar mais de uma vez durante as retentativas.
        print(f"{evento['event_id']} {evento['event_type']}: {evento.get('data')}")
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
