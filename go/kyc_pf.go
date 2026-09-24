package main

// Dabra - KYC Pessoa Fisica em Go (stdlib)
// Uso: go run kyc_pf.go 123.456.789-09
// Custo de referencia: R$ 6,00 por pessoa (7 consultas, precos de tabela em 24/09/2026)
// Docs: https://dabradata.com/docs

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"sync"
	"time"
)

const kycBaseURL = "https://app.dabradata.com/api/v1/consulta"

func kycAPIKey() string {
	if k := os.Getenv("DABRA_API_KEY"); k != "" {
		return k
	}
	return "dabra_test_SUA_CHAVE"
}

var kycChecks = map[string]string{
	"identidade":         "receita-federal-pf",    // R$ 0,54
	"pep":                "pep-exposicao",         // R$ 0,43
	"listas_restritivas": "listas-restritivas",    // R$ 1,49 (17 listas, inclui OFAC/ONU/UE)
	"ceis":               "ceis-sancoes",          // R$ 0,43
	"antecedentes":       "antecedentes-federais", // R$ 0,60
	"processos":          "processos-agrupada",    // R$ 1,65
	"mandados":           "cnj-mandados-prisao",   // R$ 0,86
}

type CheckResult struct {
	Name   string
	Status int
	Data   map[string]interface{}
	Cost   string
	Err    error
}

func runCheck(name, endpoint, cpf string, wg *sync.WaitGroup, results chan<- CheckResult) {
	defer wg.Done()
	u := fmt.Sprintf("%s/%s?%s", kycBaseURL, endpoint, url.Values{"cpf": {cpf}}.Encode())
	client := &http.Client{Timeout: 120 * time.Second}
	req, _ := http.NewRequest("GET", u, nil)
	req.Header.Set("X-API-Key", kycAPIKey())

	resp, err := client.Do(req)
	if err != nil {
		results <- CheckResult{Name: name, Err: err}
		return
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var data map[string]interface{}
	json.Unmarshal(body, &data)
	results <- CheckResult{Name: name, Status: resp.StatusCode, Data: data, Cost: resp.Header.Get("X-Request-Cost")}
}

func kycPF(cpf string) map[string]CheckResult {
	ch := make(chan CheckResult, len(kycChecks))
	var wg sync.WaitGroup
	for name, endpoint := range kycChecks {
		wg.Add(1)
		go runCheck(name, endpoint, cpf, &wg, ch)
	}
	wg.Wait()
	close(ch)

	out := map[string]CheckResult{}
	for r := range ch {
		icon := "OK"
		if r.Err != nil {
			icon = "erro"
		} else if r.Status != 200 {
			icon = fmt.Sprintf("HTTP %d", r.Status)
		}
		fmt.Printf("  [%s] %s: custo=R$%s\n", icon, r.Name, r.Cost)
		out[r.Name] = r
	}
	return out
}

func main() {
	cpf := "12345678909"
	if len(os.Args) > 1 {
		cpf = os.Args[1]
	}
	fmt.Printf("KYC PF para CPF %s:\n\n", cpf)
	res := kycPF(cpf)
	fmt.Printf("\n%d consultas concluidas.\n", len(res))
	_ = os.Stdout.Sync()
}
