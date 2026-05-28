package main

import (
	"context"
	"fmt"
	"os"

	"go-clean-template/internal/infrastructure/config"
	"go-clean-template/internal/infrastructure/logger"
	"go-clean-template/internal/infrastructure/persistence"
	"go-clean-template/internal/infrastructure/seed"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to load config: %v\n", err)
		os.Exit(1)
	}

	log := logger.New(cfg.LogLevel)

	roleRepo := persistence.NewRoleRepository()
	userRepo := persistence.NewUserRepository()

	seed.Run(context.Background(), log, roleRepo, userRepo)
}
