package seed

import (
	"context"
	"log/slog"

	"go-clean-template/internal/domain"
)

func Run(
	ctx context.Context, log *slog.Logger,
	roleRepo domain.RoleRepository,
	userRepo domain.UserRepository,
) {
	seedRoles(ctx, log, roleRepo)
	seedUsers(ctx, log, userRepo, roleRepo)
}

func seedRoles(ctx context.Context, log *slog.Logger, repo domain.RoleRepository) {
	// Use offset=0, limit=1 — we only need to know if any record exists.
	existing, _, _ := repo.FindAll(ctx, 0, 1)
	if len(existing) > 0 {
		log.Info("roles already seeded, skipping")
		return
	}

	roles := []struct {
		name        string
		description string
	}{
		{"admin", "Full system access"},
		{"user", "Standard user access"},
	}

	for _, r := range roles {
		role, err := domain.NewRole(r.name, r.description)
		if err != nil {
			log.Error("invalid role", "name", r.name, "error", err)
			continue
		}
		if err := repo.Create(ctx, role); err != nil {
			log.Error("failed to seed role", "name", r.name, "error", err)
			continue
		}
		log.Info("seeded role", "name", r.name)
	}
}

func seedUsers(ctx context.Context, log *slog.Logger, repo domain.UserRepository, roleRepo domain.RoleRepository) {
	existing, _, _ := repo.FindAll(ctx, 0, 1)
	if len(existing) > 0 {
		log.Info("users already seeded, skipping")
		return
	}

	roles, _, _ := roleRepo.FindAll(ctx, 0, 100)
	roleMap := make(map[string]string, len(roles))
	for _, r := range roles {
		roleMap[r.Name] = r.ID
	}

	users := []struct {
		name     string
		email    string
		phone    string
		roleName string
	}{
		{"Admin User", "admin@example.com", "09000000001", "admin"},
		{"Regular User", "user@example.com", "09000000002", "user"},
	}

	for _, u := range users {
		var roleIDs []string
		if roleID, ok := roleMap[u.roleName]; ok {
			roleIDs = []string{roleID}
		}
		user, err := domain.NewUser(u.name, u.email, u.phone, roleIDs)
		if err != nil {
			log.Error("invalid user", "email", u.email, "error", err)
			continue
		}
		if err := repo.Create(ctx, user); err != nil {
			log.Error("failed to seed user", "email", u.email, "error", err)
			continue
		}
		log.Info("seeded user", "email", u.email)
	}
}
