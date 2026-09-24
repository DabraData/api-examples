// Dabra - KYC Pessoa Fisica em Node.js
// Custo estimado: ~R$ 9,00 por pessoa
// Docs: https://dabradata.com/docs

const API_KEY = 'dabra_live_SUA_CHAVE';
const BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

const CHECKS = {
  identidade:   'receita-federal-pf',
  pep:          'pep-exposicao',
  ceis:         'ceis-sancoes',
  ofac:         'ofac-sancoes',
  antecedentes: 'antecedentes-criminais',
  processos:    'processos-agrupada',
  mandados:     'cnj-mandados-prisao',
};

async function kycPF(cpf) {
  const cpfLimpo = cpf.replace(/[\.\-]/g, '');
  const results = await Promise.all(
    Object.entries(CHECKS).map(async ([name, ep]) => {
      try {
        const res = await fetch(`${BASE_URL}/${ep}/${cpfLimpo}`, { headers: { 'X-API-Key': API_KEY } });
        const status = res.status === 200 ? 'OK' : 'FALHOU';
        console.log(`  [${status}] ${name}: custo=R$${res.headers.get('x-request-cost') || 'N/A'}`);
        return { name, status: res.status, data: res.ok ? await res.json() : null };
      } catch (e) {
        return { name, status: 'error', error: e.message };
      }
    })
  );
  return Object.fromEntries(results.map(r => [r.name, r]));
}

const cpf = process.argv[2] || '12345678900';
console.log(`KYC PF para CPF ${cpf}:\n`);
kycPF(cpf).then(r => console.log(`\n${Object.keys(r).length} checks concluidos.`));
