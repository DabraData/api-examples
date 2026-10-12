<?php
// Dabra - Consulta com comprovante em PHP (7.4+, ext-curl)
// Docs: https://dabradata.com/docs/comprovante
//
// Consulta tst-cndt (R$ 0,54 + 25% so quando o link do comprovante vem, tabela de 24/09/2026)
// com comprovante=1 e baixa comprovante[0]. O link e aberto (sem chave) e vale 7 dias:
// 202 = ainda sendo preparado (tente de novo), 410 = vencido (refaca a consulta).
// Com a chave de teste (dabra_test_...) a resposta e o exemplo, sem custo, e o link e ficticio.

$API_KEY  = getenv('DABRA_API_KEY') ?: 'dabra_test_SUA_CHAVE';
$BASE_URL = 'https://app.dabradata.com/api/v1/consulta';

// Faz um GET e devolve [codigo, cabecalhos, corpo].
function get(string $url, array $headers = []): array {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_HEADER         => true,
    ]);
    $response = curl_exec($ch);
    if ($response === false) {
        throw new RuntimeException('Falha de rede: ' . curl_error($ch));
    }
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    curl_close($ch);
    return [$code, substr($response, 0, $size), substr($response, $size)];
}

function consultarComComprovante(string $cnpj, string $apiKey, string $baseUrl): string {
    $url = $baseUrl . '/tst-cndt?' . http_build_query(['cnpj' => $cnpj, 'comprovante' => 1]);
    [$code, $headers, $raw] = get($url, ["X-API-Key: {$apiKey}"]);
    $body = json_decode($raw, true);
    if ($code !== 200) {
        $erro = $body['error'] ?? [];
        throw new RuntimeException("HTTP {$code} " . ($erro['code'] ?? '') . ': ' . ($erro['message'] ?? ''));
    }
    preg_match('/^X-Request-Cost:\s*([\d.]+)/mi', $headers, $cost);
    preg_match('/^X-Balance-Remaining:\s*([\d.-]+)/mi', $headers, $saldo);
    echo "Custo: R$ " . ($cost[1] ?? 'N/A') . " | Saldo: R$ " . ($saldo[1] ?? 'N/A') . "\n";
    if (empty($body['comprovante'][0])) {
        throw new RuntimeException('A resposta nao trouxe comprovante (e nada foi cobrado por ele).');
    }
    return $body['comprovante'][0];
}

function baixarComprovante(string $link, int $tentativas = 6): string {
    for ($i = 1; $i <= $tentativas; $i++) {
        [$code, $headers, $corpo] = get($link); // link aberto: sem X-API-Key
        if ($code === 200) {
            $arquivo = 'comprovante.bin';
            if (preg_match('/^Content-Type:\s*(\S+)/mi', $headers, $t)) {
                if (stripos($t[1], 'pdf') !== false) $arquivo = 'comprovante.pdf';
                elseif (stripos($t[1], 'html') !== false) $arquivo = 'comprovante.html';
            }
            file_put_contents($arquivo, $corpo);
            return $arquivo;
        }
        if ($code === 202) {
            $espera = preg_match('/^Retry-After:\s*(\d+)/mi', $headers, $r) ? (int)$r[1] : 5;
            echo "Ainda sendo preparado, tentando de novo em {$espera} s ({$i}/{$tentativas})...\n";
            sleep($espera);
            continue;
        }
        if ($code === 410) {
            throw new RuntimeException('Link vencido (7 dias) ou indisponivel: faca uma nova consulta.');
        }
        throw new RuntimeException("HTTP {$code} ao baixar o comprovante");
    }
    throw new RuntimeException("Comprovante ainda nao ficou pronto; tente o link mais tarde: {$link}");
}

try {
    $link = consultarComComprovante($argv[1] ?? '00.000.000/0001-91', $API_KEY, $BASE_URL);
    echo "Comprovante salvo em " . baixarComprovante($link) . "\n";
} catch (RuntimeException $e) {
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}
