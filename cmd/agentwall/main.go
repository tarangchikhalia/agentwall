package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/tarangchikhalia/agentwall/internal/server"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	flags := flag.NewFlagSet("agentwall", flag.ContinueOnError)
	flagIsDev := flags.Bool("dev-http", false, "Explicitely enables local HTTP")
	flagAddr := flags.String("addr", "127.0.0.1:8080", "Provide listener address")
	flags.SetOutput(stderr)
	flags.Usage = func() {
		fmt.Fprintln(stderr, "Usage: agentwall [-help]")
		fmt.Fprintln(stderr, "Foundation scaffold; proxy functionality is not implemented.")
	}
	if err := flags.Parse(args); err != nil {
		if err == flag.ErrHelp {
			return 0
		}
		return 2
	}
	if flags.NArg() != 0 {
		fmt.Fprintln(stderr, "agentwall: unexpected arguments")
		flags.Usage()
		return 2
	}

	if *flagIsDev {
		newserver := server.NewServer(*flagAddr)
		fmt.Fprintf(stdout ,"Listening on address: %s ... \n", *flagAddr)
		
		if err := newserver.ListenAndServe(); err != nil {
			fmt.Fprintf(stderr, "agentwall: listener failed: %v\n", err)
			return 1
		}
	} else {
		if _, err := fmt.Fprintln(stdout, "AgentWall foundation scaffold: proxy functionality is not implemented."); err != nil {
				fmt.Fprintf(stderr, "agentwall: write output: %v\n", err)
				return 1
			}
	}
	return 0
}
