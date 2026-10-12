// Dabra - Consulta com comprovante em Node.js (18+, sem dependencias)
// Docs: https://dabradata.com/docs/comprovante
//
// Consulta tst-cndt (R$ 0,54 + 25% so quando o link do comprovante vem, tabela de 24/09/2026)
// com comprovante=1 e baixa comprovante[0]. O link e aberto (sem chave) e vale 7 dias:
// 202 = ainda sendo preparado (tente de novo), 410 = vencido (refaca a consulta).
// Com a chave de teste (dabra_test_...) a resposta e o exemplo, sem custo, e o link e ficticio.

import { writeFile } from 'node:fs/promises';

const API_KEY = process.env.DABRA_API_KEY || 'dabra_test_SUA_CHAVE';
const BASE_URL = 'https://app.dabradata.com/api/v1/consulta';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function consultarComComprovante(cnpj) {
  const url = new URL(`${BASE_URL}/tst-cndt`);
  url.searchParams.set('cnpj', cnpj);
  url.searchParams.set('comprovante', '1');
  const res = await fetch(url, { headers: { 'X-API-Key': API_KEY } });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${body.error?.code}: ${body.error?.message}`);
  }
  console.log(`Custo: R$ ${res.headers.get('x-request-cost')} | Saldo: R$ ${res.headers.get('x-balance-remaining')}`);
  return body;
}

async function baixarComprovante(link, tentativas = 6) {
  for (let i = 1; i <= tentativas; i++) {
    const res = await fetch(link); // link aberto: sem X-API-Key
    if (res.status === 200) {
      const tipo = res.headers.get('content-type') || '';
      const arquivo = tipo.includes('pdf') ? 'comprovante.pdf' : tipo.includes('html') ? 'comprovante.html' : 'comprovante.bin';
      await writeFile(arquivo, Buffer.from(await res.arrayBuffer()));
      return arquivo;
    }
    if (res.status === 202) {
      const espera = Number(res.headers.get('retry-after')) || 5;
      console.log(`Ainda sendo preparado, tentando de novo em ${espera} s (${i}/${tentativas})...`);
      await sleep(espera * 1000);
      continue;
    }
    if (res.status === 410) {
      throw new Error('Link vencido (7 dias) ou indisponivel: faca uma nova consulta.');
    }
    throw new Error(`HTTP ${res.status} ao baixar o comprovante`);
  }
  throw new Error(`Comprovante ainda nao ficou pronto; tente o link mais tarde: ${link}`);
}

try {
  const dados = await consultarComComprovante(process.argv[2] || '00000000000191');
  const link = dados.comprovante?.[0];
  if (!link) throw new Error('A resposta nao trouxe comprovante (e nada foi cobrado por ele).');
  console.log('Comprovante salvo em', await baixarComprovante(link));
} catch (err) {
  console.error(err.message);
  process.exitCode = 1;
}
