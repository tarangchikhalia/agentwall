package server

import "net/http"

func NewServer (address string) *http.Server {
	server := http.Server{Addr: address, Handler: NewRouter()}
	return &server
}