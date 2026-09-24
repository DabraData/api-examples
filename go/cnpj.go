package main

// Dabra - Consultar CNPJ em Go
// Docs: https://dabradata.com/docs

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

const apiKey  = "dabra_live_SUA_CHAVE"
const baseURL = "https://app.dabradata.com/api/v1/consulta"

func consultarCNPJ(cnpj string) (map[string]interface{}, error) {
	cnpj = strings.NewReplacer(".", "", "/", "", "-", "").Replace(cnpj)
	url := fmt.Sprintf("%s/consulta-cnpj-receita/%s", baseURL, cnpj)

	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-API-Key", apiKey)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	fmt.Printf("Custo: R$ %s | Saldo: R$ %s\n",
		resp.Header.Get("X-Request-Cost"),
		resp.Header.Get("X-Balance-Remaining"))

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, body)
	}

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
	fmt.Printf("Situacao:     %v\n", dados["situacao_cadastral"])
	fmt.Printf("CNAE:         %v\n", dados["cnae_fiscal_descricao"])
}
