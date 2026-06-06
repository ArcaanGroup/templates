package role

import (
	"context"

	"go-clean-template/internal/domain"
)

type CreateRoleInput struct {
	Name        string
	Description string
}

type CreateRoleOutput struct {
	Role *domain.Role
}

type CreateRoleUseCase interface {
	Execute(ctx context.Context, input *CreateRoleInput) (*CreateRoleOutput, error)
}

type createRoleUseCase struct {
	roleRepo domain.RoleRepository
}

func NewCreateRoleUseCase(roleRepo domain.RoleRepository) CreateRoleUseCase {
	return &createRoleUseCase{roleRepo: roleRepo}
}

func (uc *createRoleUseCase) Execute(ctx context.Context, input *CreateRoleInput) (*CreateRoleOutput, error) {
	role, err := domain.NewRole(input.Name, input.Description)
	if err != nil {
		return nil, err
	}
	existing, _ := uc.roleRepo.FindByName(ctx, input.Name)
	if existing != nil {
		return nil, domain.ErrAlreadyExists
	}
	if err := uc.roleRepo.Create(ctx, role); err != nil {
		return nil, err
	}
	return &CreateRoleOutput{Role: role}, nil
}
