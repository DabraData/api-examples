# Dabra - Receber webhook e verificar a assinatura (stdlib, sem dependencias)
#
# Toda entrega traz o header X-FonteData-Signature: sha256=<hex>, um HMAC-SHA256 do
# corpo BRUTO da requisicao com o segredo de assinatura gerado ao cadastrar o webhook.
# O nome do header ainda carrega a marca anterior; o valor e o calculo nao mudam.
# Documentacao: https://dabradata.com/docs/webhooks/assinatura
#
# Uso: DABRA_WEBHOOK_SECRET=... python webhook_assinatura.py   (escuta em :8080)
import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ.get("DABRA_WEBHOOK_SECRET", "seu_segredo_de_assinatura")
HEADER = "X-FonteData-Signature"


def assinatura_valida(corpo_bruto: bytes, header_assinatura: str, secret: str) -> bool:
    esperado = "sha256=" + hmac.new(secret.encode("utf-8"), corpo_bruto, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, header_assinatura or "")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if not assinatura_valida(corpo, self.headers.get(HEADER), SECRET):
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
