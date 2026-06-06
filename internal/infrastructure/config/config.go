package config

import (
	"fmt"
	"os"
	"strconv"
)

type Config struct {
	Port         int
	LogLevel     string
	ReadTimeout  int
	WriteTimeout int
	// CORSOrigin is the value of the Access-Control-Allow-Origin header.
	// Set CORS_ORIGIN env var to restrict origins in production (e.g. "https://app.example.com").
	// Defaults to "*" which is suitable for local development only.
	CORSOrigin string
}

func Load() (*Config, error) {
	cfg := &Config{
		Port:         8080,
		LogLevel:     "info",
		ReadTimeout:  10,
		WriteTimeout: 10,
		CORSOrigin:   "*",
	}

	if v := os.Getenv("PORT"); v != "" {
		port, err := strconv.Atoi(v)
		if err != nil {
			return nil, fmt.Errorf("invalid PORT: %w", err)
		}
		cfg.Port = port
	}

	if v := os.Getenv("LOG_LEVEL"); v != "" {
		cfg.LogLevel = v
	}

	if v := os.Getenv("READ_TIMEOUT"); v != "" {
		t, err := strconv.Atoi(v)
		if err != nil {
			return nil, fmt.Errorf("invalid READ_TIMEOUT: %w", err)
		}
		cfg.ReadTimeout = t
	}

	if v := os.Getenv("WRITE_TIMEOUT"); v != "" {
		t, err := strconv.Atoi(v)
		if err != nil {
			return nil, fmt.Errorf("invalid WRITE_TIMEOUT: %w", err)
		}
		cfg.WriteTimeout = t
	}

	if v := os.Getenv("CORS_ORIGIN"); v != "" {
		cfg.CORSOrigin = v
	}

	return cfg, nil
}
