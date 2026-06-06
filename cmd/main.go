// @title           Go Clean Template API
// @version         1.0
// @description     Clean Architecture API template
// @host            localhost:8080
// @BasePath        /api/v1
package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	_ "go-clean-template/docs"

	userusecase "go-clean-template/internal/application/usecase/user"
	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/infrastructure/config"
	"go-clean-template/internal/infrastructure/logger"
	"go-clean-template/internal/infrastructure/persistence"
	"go-clean-template/internal/infrastructure/seed"
	"go-clean-template/internal/interface/handler"
	"go-clean-template/internal/interface/router"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to load config: %v\n", err)
		os.Exit(1)
	}

	log := logger.New(cfg.LogLevel)
	log.Info("starting server", "port", cfg.Port)

	// --- Repositories ---
	userRepo := persistence.NewUserRepository()
	roleRepo := persistence.NewRoleRepository()

	// --- Use Cases ---
	createUserUC := userusecase.NewCreateUserUseCase(userRepo, roleRepo)
	getUserUC := userusecase.NewGetUserUseCase(userRepo)
	listUsersUC := userusecase.NewListUsersUseCase(userRepo)
	updateUserUC := userusecase.NewUpdateUserUseCase(userRepo, roleRepo)
	deleteUserUC := userusecase.NewDeleteUserUseCase(userRepo)
	assignRolesUC := userusecase.NewAssignRolesUseCase(userRepo, roleRepo)
	getUserRolesUC := userusecase.NewGetUserRolesUseCase(userRepo, roleRepo)

	createRoleUC := roleusecase.NewCreateRoleUseCase(roleRepo)
	getRoleUC := roleusecase.NewGetRoleUseCase(roleRepo)
	listRolesUC := roleusecase.NewListRolesUseCase(roleRepo)
	updateRoleUC := roleusecase.NewUpdateRoleUseCase(roleRepo)
	deleteRoleUC := roleusecase.NewDeleteRoleUseCase(roleRepo)

	// --- Handlers ---
	userHandler := handler.NewUserHandler(
		createUserUC, getUserUC, listUsersUC, updateUserUC,
		deleteUserUC, assignRolesUC, getUserRolesUC,
	)
	roleHandler := handler.NewRoleHandler(
		createRoleUC, getRoleUC, listRolesUC, updateRoleUC, deleteRoleUC,
	)

	// --- Seed ---
	seed.Run(context.Background(), log, roleRepo, userRepo)

	// --- Router ---
	r := router.New(log, cfg.CORSOrigin, userHandler, roleHandler)

	// --- Server ---
	srv := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Port),
		Handler:      r,
		ReadTimeout:  time.Duration(cfg.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(cfg.WriteTimeout) * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	go func() {
		log.Info("server listening", "addr", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Error("server error", "error", err)
			os.Exit(1)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("shutting down gracefully...")

	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer shutdownCancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		log.Error("server forced to shutdown", "error", err)
		os.Exit(1)
	}

	log.Info("server stopped")
}
