<?php
// Dabra - Consultar CNPJ em PHP (7.4+, ext-curl)
// Docs: https://dabradata.com/docs/receita-federal/receita-federal-pj
//
// Chave: variavel de ambiente DABRA_API_KEY. Com a chave de teste (dabra_test_...)
// a resposta e o exemplo do endpoint, a custo zero, com o header X-Example: true.

$API_KEY  = getenv('DABRA_API_KEY') ?: 'dabra_test_SUA_CHAVE';
$BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

// Receita Federal PJ (R$ 0,43): cadastro, CNAE, endereco e QSA.
function consultarCNPJ(string $cnpj, string $apiKey, string $baseUrl): array {
    $url = $baseUrl . '/receita-federal-pj?' . http_build_query(['cnpj' => $cnpj]);

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ["X-API-Key: {$apiKey}"],
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_HEADER         => true,
    ]);

    $response   = curl_exec($ch);
    $httpCode   = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);

    $headers = substr($response, 0, $headerSize);
    $body    = json_decode(substr($response, $headerSize), true);

    if ($httpCode !== 200) {
        $erro = $body['error'] ?? [];
        throw new RuntimeException("HTTP {$httpCode} " . ($erro['code'] ?? '') . ': ' . ($erro['message'] ?? ''));
    }

    if (preg_match('/^X-Example:\s*true/mi', $headers)) {
        echo "(chave de teste: resposta de exemplo, sem custo)\n";
    }
    preg_match('/^X-Request-Cost:\s*([\d.]+)/mi', $headers, $cost);
    preg_match('/^X-Balance-Remaining:\s*([\d.-]+)/mi', $headers, $saldo);
    echo "Custo: R$ " . ($cost[1] ?? 'N/A') . " | Saldo: R$ " . ($saldo[1] ?? 'N/A') . "\n";

    return $body;
}

$dados = consultarCNPJ($argv[1] ?? '00.000.000/0001-91', $API_KEY, $BASE_URL);
echo "Razao social: " . $dados['razao_social'] . "\n";
echo "Situacao:     " . $dados['descricao_situacao_cadastral'] . "\n";
echo "CNAE:         " . $dados['cnae_fiscal_descricao'] . "\n";
