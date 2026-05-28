package role

import (
	"context"

	"go-clean-template/internal/domain"
)

type DeleteRoleInput struct {
	ID string
}

type DeleteRoleUseCase interface {
	Execute(ctx context.Context, input *DeleteRoleInput) error
}

type deleteRoleUseCase struct {
	roleRepo domain.RoleRepository
}

func NewDeleteRoleUseCase(roleRepo domain.RoleRepository) DeleteRoleUseCase {
	return &deleteRoleUseCase{roleRepo: roleRepo}
}

func (uc *deleteRoleUseCase) Execute(ctx context.Context, input *DeleteRoleInput) error {
	if _, err := uc.roleRepo.FindByID(ctx, input.ID); err != nil {
		return err
	}
	return uc.roleRepo.Delete(ctx, input.ID)
}
