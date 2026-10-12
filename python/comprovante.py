# Dabra - Consulta com comprovante em Python
# pip install requests
# Docs: https://dabradata.com/docs/comprovante
#
# Consulta tst-cndt (R$ 0,54 + 25% so quando o link do comprovante vem, tabela de 24/09/2026)
# com comprovante=1 e baixa comprovante[0]. O link e aberto (sem chave) e vale 7 dias:
# 202 = ainda sendo preparado (tente de novo), 410 = vencido (refaca a consulta).
# Com a chave de teste (dabra_test_...) a resposta e o exemplo, sem custo, e o link e ficticio.
import os
import sys
import time

import requests

API_KEY = os.environ.get("DABRA_API_KEY", "dabra_test_SUA_CHAVE")
BASE_URL = "https://app.dabradata.com/api/v1/consulta"


def consultar_com_comprovante(cnpj: str) -> str:
    r = requests.get(f"{BASE_URL}/tst-cndt", params={"cnpj": cnpj, "comprovante": 1},
                     headers={"X-API-Key": API_KEY}, timeout=60)
    if not r.ok:
        erro = r.json().get("error", {})
        raise RuntimeError(f"HTTP {r.status_code} {erro.get('code')}: {erro.get('message')}")
    print(f"Custo: R$ {r.headers.get('X-Request-Cost')} | Saldo: R$ {r.headers.get('X-Balance-Remaining')}")
    links = r.json().get("comprovante") or []
    if not links:
        raise RuntimeError("A resposta nao trouxe comprovante (e nada foi cobrado por ele).")
    return links[0]


def baixar_comprovante(link: str, tentativas: int = 6) -> str:
    for i in range(1, tentativas + 1):
        r = requests.get(link, timeout=60)  # link aberto: sem X-API-Key
        if r.status_code == 200:
            tipo = r.headers.get("Content-Type", "")
            ext = "pdf" if "pdf" in tipo else "html" if "html" in tipo else "bin"
            arquivo = f"comprovante.{ext}"
            with open(arquivo, "wb") as f:
                f.write(r.content)
            return arquivo
        if r.status_code == 202:
            espera = int(r.headers.get("Retry-After", 5))
            print(f"Ainda sendo preparado, tentando de novo em {espera} s ({i}/{tentativas})...")
            time.sleep(espera)
            continue
        if r.status_code == 410:
            raise RuntimeError("Link vencido (7 dias) ou indisponivel: faca uma nova consulta.")
        raise RuntimeError(f"HTTP {r.status_code} ao baixar o comprovante")
    raise RuntimeError(f"Comprovante ainda nao ficou pronto; tente o link mais tarde: {link}")


if __name__ == "__main__":
    try:
        link = consultar_com_comprovante(sys.argv[1] if len(sys.argv) > 1 else "00000000000191")
        print("Comprovante salvo em", baixar_comprovante(link))
    except RuntimeError as e:
        sys.exit(str(e))
