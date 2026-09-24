package main

// Dabra - KYC Pessoa Fisica em Go
// Custo estimado: ~R$9,00 por pessoa
// Docs: https://dabradata.com/docs

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

const kycAPIKey  = "dabra_live_SUA_CHAVE"
const kycBaseURL = "https://app.dabradata.com/api/v1/consulta"

var kycChecks = map[string]string{
	"identidade":   "receita-federal-pf",
	"pep":          "pep-exposicao",
	"ceis":         "ceis-sancoes",
	"ofac":         "ofac-sancoes",
	"antecedentes": "antecedentes-criminais",
	"processos":    "processos-agrupada",
	"mandados":     "cnj-mandados-prisao",
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
	url := fmt.Sprintf("%s/%s/%s", kycBaseURL, endpoint, cpf)
	client := &http.Client{Timeout: 30 * time.Second}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("X-API-Key", kycAPIKey)

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
	cpf = strings.NewReplacer(".", "", "-", "").Replace(cpf)
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
		if r.Status != 200 { icon = "FALHOU" }
		fmt.Printf("  [%s] %s: custo=R$%s\n", icon, r.Name, r.Cost)
		out[r.Name] = r
	}
	return out
}

func main() {
	cpf := "12345678900"
	if len(os.Args) > 1 { cpf = os.Args[1] }
	fmt.Printf("KYC PF para CPF %s:\n\n", cpf)
	res := kycPF(cpf)
	fmt.Printf("\n%d checks concluidos.\n", len(res))
	_ = os.Stdout.Sync()
}
