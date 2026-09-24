// Dabra - Consultar CNPJ em Node.js
// Docs: https://dabradata.com/docs

const API_KEY = 'dabra_live_SUA_CHAVE';
const BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

async function consultarCNPJ(cnpj) {
  const cnpjLimpo = cnpj.replace(/[\.\-\/]/g, '');
  const res = await fetch(`${BASE_URL}/consulta-cnpj-receita/${cnpjLimpo}`, {
    headers: { 'X-API-Key': API_KEY }
  });
  console.log(`Custo: R$ ${res.headers.get('x-request-cost')} | Saldo: R$ ${res.headers.get('x-balance-remaining')}`);
  if (!res.ok) throw new Error(`Erro ${res.status}`);
  return res.json();
}

const cnpj = process.argv[2] || '00000000000191';
consultarCNPJ(cnpj).then(d => {
  console.log('Razao social:', d.razao_social);
  console.log('Situacao:    ', d.situacao_cadastral);
}).catch(console.error);
