package role

import (
	"context"

	"go-clean-template/internal/domain"
)

type GetRoleInput struct {
	ID string
}

type GetRoleOutput struct {
	Role *domain.Role
}

type GetRoleUseCase interface {
	Execute(ctx context.Context, input *GetRoleInput) (*GetRoleOutput, error)
}

type getRoleUseCase struct {
	roleRepo domain.RoleRepository
}

func NewGetRoleUseCase(roleRepo domain.RoleRepository) GetRoleUseCase {
	return &getRoleUseCase{roleRepo: roleRepo}
}

func (uc *getRoleUseCase) Execute(ctx context.Context, input *GetRoleInput) (*GetRoleOutput, error) {
	role, err := uc.roleRepo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	return &GetRoleOutput{Role: role}, nil
}
