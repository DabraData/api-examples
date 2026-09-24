// Dabra - KYC Pessoa Fisica em Node.js (18+, sem dependencias)
// Custo de referencia: R$ 6,00 por pessoa (7 consultas, precos de tabela em 24/09/2026)
// Docs: https://dabradata.com/docs

const API_KEY = process.env.DABRA_API_KEY || 'dabra_test_SUA_CHAVE';
const BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

const CHECKS = {
  identidade:         'receita-federal-pf',     // R$ 0,54
  pep:                'pep-exposicao',          // R$ 0,43
  listas_restritivas: 'listas-restritivas',     // R$ 1,49 (17 listas, inclui OFAC/ONU/UE)
  ceis:               'ceis-sancoes',           // R$ 0,43
  antecedentes:       'antecedentes-federais',  // R$ 0,60
  processos:          'processos-agrupada',     // R$ 1,65
  mandados:           'cnj-mandados-prisao',    // R$ 0,86
};

async function check(name, endpoint, cpf) {
  try {
    const url = new URL(`${BASE_URL}/${endpoint}`);
    url.searchParams.set('cpf', cpf);
    const res = await fetch(url, { headers: { 'X-API-Key': API_KEY } });
    const body = await res.json();
    const status = res.ok ? 'OK' : `HTTP ${res.status}`;
    console.log(`  [${status}] ${name}: custo=R$ ${res.headers.get('x-request-cost') || '0'}`);
    return { name, status: res.status, data: res.ok ? body : null, erro: res.ok ? null : body.error };
  } catch (e) {
    return { name, status: 'erro', erro: e.message };
  }
}

async function kycPF(cpf) {
  const results = await Promise.all(
    Object.entries(CHECKS).map(([name, ep]) => check(name, ep, cpf))
  );
  return Object.fromEntries(results.map(r => [r.name, r]));
}

const cpf = process.argv[2] || '12345678909';
console.log(`KYC PF para CPF ${cpf}:\n`);
kycPF(cpf).then(r => console.log(`\n${Object.keys(r).length} consultas concluidas.`));
