// Dabra - Consultar CNPJ em Node.js (18+, sem dependencias)
// Docs: https://dabradata.com/docs/receita-federal/receita-federal-pj
//
// Chave: variavel de ambiente DABRA_API_KEY. Com a chave de teste (dabra_test_...)
// a resposta e o exemplo do endpoint, a custo zero, com o header X-Example: true.

const API_KEY = process.env.DABRA_API_KEY || 'dabra_test_SUA_CHAVE';
const BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

// Receita Federal PJ (R$ 0,43): cadastro, CNAE, endereco e QSA.
async function consultarCNPJ(cnpj) {
  const url = new URL(`${BASE_URL}/receita-federal-pj`);
  url.searchParams.set('cnpj', cnpj); // aceita com ou sem pontuacao
  const res = await fetch(url, { headers: { 'X-API-Key': API_KEY } });
  if (res.headers.get('x-example') === 'true') {
    console.log('(chave de teste: resposta de exemplo, sem custo)');
  }
  const body = await res.json();
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} ${body.error?.code}: ${body.error?.message}`);
  }
  console.log(`Custo: R$ ${res.headers.get('x-request-cost')} | Saldo: R$ ${res.headers.get('x-balance-remaining')}`);
  return body;
}

const cnpj = process.argv[2] || '00000000000191';
consultarCNPJ(cnpj).then(d => {
  console.log('Razao social:', d.razao_social);
  console.log('Situacao:    ', d.descricao_situacao_cadastral);
  console.log('CNAE:        ', d.cnae_fiscal_descricao);
}).catch(err => {
  console.error(err.message);
  process.exitCode = 1;
});
