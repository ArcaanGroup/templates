package user

import (
	"context"

	"go-clean-template/internal/domain"
)

func validateRoleIDs(ctx context.Context, roleRepo domain.RoleRepository, ids []string) error {
	for _, id := range ids {
		if _, err := roleRepo.FindByID(ctx, id); err != nil {
			return err
		}
	}
	return nil
}
