package server

import (
	"io"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
)

func TestServerHealth(t *testing.T) {
	server := httptest.NewServer(NewRouter())
	defer server.Close()
	client := server.Client()
	resp, err := client.Get(server.URL + "/health")
	if err != nil {
		t.Fatalf("Error %v", err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Errorf("Expected code 200. Got %d", resp.StatusCode)
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Error when reading response body. %v", err)
	}
	if string(body) != "ok" {
		t.Errorf("Expected body 'ok'. Got %q", body)
	}
}

func TestConcurrentHealth(t *testing.T) {
	server := httptest.NewServer(NewRouter())
	defer server.Close()
	client := server.Client()
	var wg sync.WaitGroup

	for range 10 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			resp, err := client.Get(server.URL + "/health")
			if err != nil {
				t.Errorf("Error %v", err)
				return
			}
			defer resp.Body.Close()
			if resp.StatusCode != http.StatusOK {
				t.Errorf("Expected code 200. Got %d", resp.StatusCode)
			}
			body, err := io.ReadAll(resp.Body)
			if err != nil {
				t.Errorf("Error when reading response body. %v", err)
				return
			}
			if string(body) != "ok" {
				t.Errorf("Expected body 'ok'. Got %q", body)
			}
		}()
	}
	wg.Wait()
}
