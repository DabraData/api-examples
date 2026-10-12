package main

// Dabra - Consulta com comprovante em Go (stdlib)
// Uso: go run comprovante.go 00.000.000/0001-91
// Docs: https://dabradata.com/docs/comprovante
//
// Consulta tst-cndt (R$ 0,54 + 25% so quando o link do comprovante vem, tabela de 24/09/2026)
// com comprovante=1 e baixa comprovante[0]. O link e aberto (sem chave) e vale 7 dias:
// 202 = ainda sendo preparado (tente de novo), 410 = vencido (refaca a consulta).
// Com a chave de teste (dabra_test_...) a resposta e o exemplo, sem custo, e o link e ficticio.

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

const baseURL = "https://app.dabradata.com/api/v1/consulta"

var client = &http.Client{Timeout: 60 * time.Second}

func apiKey() string {
	if k := os.Getenv("DABRA_API_KEY"); k != "" {
		return k
	}
	return "dabra_test_SUA_CHAVE"
}

func consultarComComprovante(cnpj string) (string, error) {
	q := url.Values{"cnpj": {cnpj}, "comprovante": {"1"}}
	req, err := http.NewRequest("GET", baseURL+"/tst-cndt?"+q.Encode(), nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("X-API-Key", apiKey())
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("HTTP %d: %s", resp.StatusCode, body)
	}
	fmt.Printf("Custo: R$ %s | Saldo: R$ %s\n",
		resp.Header.Get("X-Request-Cost"), resp.Header.Get("X-Balance-Remaining"))

	var dados struct {
		Comprovante []string `json:"comprovante"`
	}
	if err := json.Unmarshal(body, &dados); err != nil {
		return "", err
	}
	if len(dados.Comprovante) == 0 {
		return "", errors.New("a resposta nao trouxe comprovante (e nada foi cobrado por ele)")
	}
	return dados.Comprovante[0], nil
}

func salvar(resp *http.Response) (string, error) {
	defer resp.Body.Close()
	nome := "comprovante.bin"
	tipo := resp.Header.Get("Content-Type")
	if strings.Contains(tipo, "pdf") {
		nome = "comprovante.pdf"
	} else if strings.Contains(tipo, "html") {
		nome = "comprovante.html"
	}
	f, err := os.Create(nome)
	if err != nil {
		return "", err
	}
	defer f.Close()
	if _, err := io.Copy(f, resp.Body); err != nil {
		return "", err
	}
	return nome, nil
}

func baixarComprovante(link string, tentativas int) (string, error) {
	for i := 1; i <= tentativas; i++ {
		resp, err := client.Get(link) // link aberto: sem X-API-Key
		if err != nil {
			return "", err
		}
		switch resp.StatusCode {
		case 200:
			return salvar(resp)
		case 202:
			espera, _ := strconv.Atoi(resp.Header.Get("Retry-After"))
			resp.Body.Close()
			if espera <= 0 {
				espera = 5
			}
			fmt.Printf("Ainda sendo preparado, tentando de novo em %d s (%d/%d)...\n", espera, i, tentativas)
			time.Sleep(time.Duration(espera) * time.Second)
		case 410:
			resp.Body.Close()
			return "", errors.New("link vencido (7 dias) ou indisponivel: faca uma nova consulta")
		default:
			resp.Body.Close()
			return "", fmt.Errorf("HTTP %d ao baixar o comprovante", resp.StatusCode)
		}
	}
	return "", fmt.Errorf("comprovante ainda nao ficou pronto; tente o link mais tarde: %s", link)
}

func main() {
	cnpj := "00000000000191"
	if len(os.Args) > 1 {
		cnpj = os.Args[1]
	}
	link, err := consultarComComprovante(cnpj)
	if err == nil {
		var nome string
		if nome, err = baixarComprovante(link, 6); err == nil {
			fmt.Println("Comprovante salvo em", nome)
			return
		}
	}
	fmt.Fprintln(os.Stderr, "Erro:", err)
	os.Exit(1)
}
