package server

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHealth(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	resp := httptest.NewRecorder()
	router := NewRouter()
	router.ServeHTTP(resp, req)
	if resp.Code != http.StatusOK {
		t.Errorf("Expected status 200. Got %d", resp.Code)
	}
	if resp.Body.String() != "ok" {
		t.Errorf("Expected body 'ok'. Got %q", resp.Body.String())
	}
}

func TestHealthMethodNotAllowed(t *testing.T) {
	req := httptest.NewRequest(http.MethodPost, "/health", nil)
	resp := httptest.NewRecorder()
	router := NewRouter()
	router.ServeHTTP(resp, req)
	if resp.Code != http.StatusMethodNotAllowed {
		t.Errorf("Expected status 405. Got %d", resp.Code)
	}
}

func TestUnknownPath(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/missing", nil)
	resp := httptest.NewRecorder()
	router := NewRouter()
	router.ServeHTTP(resp, req)
	if resp.Code != http.StatusNotFound {
		t.Errorf("Expected status 404. Got %d", resp.Code)
	}
}
