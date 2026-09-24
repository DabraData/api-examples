<?php
// Dabra - KYC Pessoa Fisica em PHP (7.4+, ext-curl)
// Custo de referencia: R$ 6,00 por pessoa (7 consultas, precos de tabela em 24/09/2026)
// Docs: https://dabradata.com/docs

$API_KEY  = getenv('DABRA_API_KEY') ?: 'dabra_test_SUA_CHAVE';
$BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

$CHECKS = [
    'identidade'         => 'receita-federal-pf',     // R$ 0,54
    'pep'                => 'pep-exposicao',          // R$ 0,43
    'listas_restritivas' => 'listas-restritivas',     // R$ 1,49 (17 listas, inclui OFAC/ONU/UE)
    'ceis'               => 'ceis-sancoes',           // R$ 0,43
    'antecedentes'       => 'antecedentes-federais',  // R$ 0,60
    'processos'          => 'processos-agrupada',     // R$ 1,65
    'mandados'           => 'cnj-mandados-prisao',    // R$ 0,86
];

function fetchCheck(string $name, string $endpoint, string $cpf, string $apiKey, string $baseUrl): array {
    $url = "{$baseUrl}/{$endpoint}?" . http_build_query(['cpf' => $cpf]);
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ["X-API-Key: {$apiKey}"],
        CURLOPT_TIMEOUT        => 120,
        CURLOPT_HEADER         => true,
    ]);
    $response   = curl_exec($ch);
    $httpCode   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);

    $headers = substr($response, 0, $headerSize);
    $body    = json_decode(substr($response, $headerSize), true);
    preg_match('/^X-Request-Cost:\s*([\d.]+)/mi', $headers, $cost);

    $icon = $httpCode === 200 ? 'OK' : "HTTP {$httpCode}";
    echo "  [{$icon}] {$name}: custo=R$ " . ($cost[1] ?? '0') . "\n";

    return [
        'status' => $httpCode,
        'data'   => $httpCode === 200 ? $body : null,
        'erro'   => $httpCode === 200 ? null : ($body['error'] ?? null),
        'cost'   => $cost[1] ?? null,
    ];
}

$cpf = $argv[1] ?? '12345678909';
echo "KYC PF para CPF {$cpf}:\n\n";

$results = [];
foreach ($CHECKS as $name => $endpoint) {
    $results[$name] = fetchCheck($name, $endpoint, $cpf, $API_KEY, $BASE_URL);
}

echo "\n" . count($results) . " consultas concluidas.\n";
