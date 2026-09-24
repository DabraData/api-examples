package main

// Dabra - Consultar CNPJ em Go (stdlib)
// Uso: go run cnpj.go 00.000.000/0001-91
// Docs: https://dabradata.com/docs/receita-federal/receita-federal-pj
//
// Chave: variavel de ambiente DABRA_API_KEY. Com a chave de teste (dabra_test_...)
// a resposta e o exemplo do endpoint, a custo zero, com o header X-Example: true.

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"time"
)

const baseURL = "https://app.dabradata.com/api/v1/consulta"

func apiKey() string {
	if k := os.Getenv("DABRA_API_KEY"); k != "" {
		return k
	}
	return "dabra_test_SUA_CHAVE"
}

// Receita Federal PJ (R$ 0,43): cadastro, CNAE, endereco e QSA.
func consultarCNPJ(cnpj string) (map[string]interface{}, error) {
	endpoint := baseURL + "/receita-federal-pj?" + url.Values{"cnpj": {cnpj}}.Encode()

	client := &http.Client{Timeout: 60 * time.Second}
	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-API-Key", apiKey())

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, body)
	}

	if resp.Header.Get("X-Example") == "true" {
		fmt.Println("(chave de teste: resposta de exemplo, sem custo)")
	}
	fmt.Printf("Custo: R$ %s | Saldo: R$ %s\n",
		resp.Header.Get("X-Request-Cost"),
		resp.Header.Get("X-Balance-Remaining"))

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}
	return result, nil
}

func main() {
	cnpj := "00000000000191"
	if len(os.Args) > 1 {
		cnpj = os.Args[1]
	}

	dados, err := consultarCNPJ(cnpj)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Erro:", err)
		os.Exit(1)
	}

	fmt.Printf("Razao social: %v\n", dados["razao_social"])
	fmt.Printf("Situacao:     %v\n", dados["descricao_situacao_cadastral"])
	fmt.Printf("CNAE:         %v\n", dados["cnae_fiscal_descricao"])
}
