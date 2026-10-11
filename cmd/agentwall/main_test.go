package main

import (
	"bytes"
	"errors"
	"strings"
	"testing"
)

func TestRun(t *testing.T) {
	tests := []struct {
		name       string
		args       []string
		code       int
		stdoutText string
		stderrText string
	}{
		{name: "scaffold", code: 0, stdoutText: "proxy functionality is not implemented"},
		{name: "help", args: []string{"-help"}, code: 0, stderrText: "Usage: agentwall"},
		{name: "invalid flag", args: []string{"-serve"}, code: 2, stderrText: "flag provided but not defined"},
		{name: "unexpected argument", args: []string{"serve"}, code: 2, stderrText: "unexpected arguments"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var stdout, stderr bytes.Buffer
			if code := run(tt.args, &stdout, &stderr); code != tt.code {
				t.Fatalf("exit code = %d, want %d", code, tt.code)
			}
			for _, output := range []struct{ got, want string }{
				{stdout.String(), tt.stdoutText}, {stderr.String(), tt.stderrText},
			} {
				if output.want == "" && output.got != "" {
					t.Errorf("unexpected output: %q", output.got)
				} else if !strings.Contains(output.got, output.want) {
					t.Errorf("output %q does not contain %q", output.got, output.want)
				}
			}
		})
	}
}

type failingWriter struct{}

func (failingWriter) Write([]byte) (int, error) {
	return 0, errors.New("output unavailable")
}

func TestRunOutputFailure(t *testing.T) {
	var stderr bytes.Buffer
	if code := run(nil, failingWriter{}, &stderr); code != 1 {
		t.Fatalf("exit code = %d, want 1", code)
	}
	if !strings.Contains(stderr.String(), "output unavailable") {
		t.Fatalf("missing output error: %q", stderr.String())
	}
}
