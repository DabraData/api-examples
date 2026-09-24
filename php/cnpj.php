<?php
// Dabra - Consultar CNPJ em PHP
// Docs: https://dabradata.com/docs

$API_KEY = 'dabra_live_SUA_CHAVE';
$BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

function consultarCNPJ(string $cnpj, string $apiKey, string $baseUrl): array {
    $cnpj = preg_replace('/[.\-\/]/', '', $cnpj);
    $url = "{$baseUrl}/consulta-cnpj-receita/{$cnpj}";

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => ["X-API-Key: {$apiKey}"],
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_HEADER         => true,
    ]);

    $response  = curl_exec($ch);
    $httpCode  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);

    $headers = substr($response, 0, $headerSize);
    $body    = substr($response, $headerSize);

    preg_match('/X-Request-Cost:\s*([\d.]+)/i', $headers, $cost);
    echo "Custo: R$ " . ($cost[1] ?? 'N/A') . "\n";

    if ($httpCode !== 200) {
        throw new RuntimeException("Erro HTTP {$httpCode}: {$body}");
    }

    return json_decode($body, true);
}

$dados = consultarCNPJ('00.000.000/0001-91', $API_KEY, $BASE_URL);
echo "Razao social: " . $dados['razao_social'] . "\n";
echo "Situacao:     " . $dados['situacao_cadastral'] . "\n";
echo "CNAE:         " . $dados['cnae_fiscal_descricao'] . "\n";
