package main

import (
	"flag"
	"fmt"
	"io"
	"os"
)

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(args []string, stdout, stderr io.Writer) int {
	flags := flag.NewFlagSet("agentwall", flag.ContinueOnError)
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
	if _, err := fmt.Fprintln(stdout, "AgentWall foundation scaffold: proxy functionality is not implemented."); err != nil {
		fmt.Fprintf(stderr, "agentwall: write output: %v\n", err)
		return 1
	}
	return 0
}
