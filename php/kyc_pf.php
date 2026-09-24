<?php
// Dabra - KYC Pessoa Fisica em PHP
// Custo estimado: ~R$ 9,00 por pessoa
// Docs: https://dabradata.com/docs

$API_KEY = 'dabra_live_SUA_CHAVE';
$BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

$CHECKS = [
    'identidade'   => 'receita-federal-pf',
    'pep'          => 'pep-exposicao',
    'ceis'         => 'ceis-sancoes',
    'ofac'         => 'ofac-sancoes',
    'antecedentes' => 'antecedentes-criminais',
    'processos'    => 'processos-agrupada',
    'mandados'     => 'cnj-mandados-prisao',
];

function fetchCheck(string $name, string $endpoint, string $cpf, string $apiKey, string $baseUrl): array {
    $url = "{$baseUrl}/{$endpoint}/{$cpf}";
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ["X-API-Key: {$apiKey}"],
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_HEADER         => true,
    ]);
    $response   = curl_exec($ch);
    $httpCode   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);

    $headers = substr($response, 0, $headerSize);
    $body    = substr($response, $headerSize);
    preg_match('/X-Request-Cost:\s*([\d.]+)/i', $headers, $cost);

    $icon = $httpCode === 200 ? 'OK' : 'FALHOU';
    echo "  [{$icon}] {$name}: custo=R$" . ($cost[1] ?? 'N/A') . "\n";

    return ['status' => $httpCode, 'data' => json_decode($body, true), 'cost' => $cost[1] ?? null];
}

$cpf = preg_replace('/[.\-]/', '', $argv[1] ?? '12345678900');
echo "KYC PF para CPF {$cpf}:\n\n";

$results = [];
foreach ($CHECKS as $name => $endpoint) {
    $results[$name] = fetchCheck($name, $endpoint, $cpf, $API_KEY, $BASE_URL);
}

echo "\n" . count($results) . " checks concluidos.\n";
