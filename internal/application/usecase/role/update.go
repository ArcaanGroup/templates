package role

import (
	"context"

	"go-clean-template/internal/domain"
)

type UpdateRoleInput struct {
	Name        string
	Description string
}

type UpdateRoleOutput struct {
	Role *domain.Role
}

type UpdateRoleUseCase interface {
	Execute(ctx context.Context, id string, input *UpdateRoleInput) (*UpdateRoleOutput, error)
}

type updateRoleUseCase struct {
	roleRepo domain.RoleRepository
}

func NewUpdateRoleUseCase(roleRepo domain.RoleRepository) UpdateRoleUseCase {
	return &updateRoleUseCase{roleRepo: roleRepo}
}

func (uc *updateRoleUseCase) Execute(ctx context.Context, id string, input *UpdateRoleInput) (*UpdateRoleOutput, error) {
	role, err := uc.roleRepo.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if input.Name != role.Name {
		existing, _ := uc.roleRepo.FindByName(ctx, input.Name)
		if existing != nil {
			return nil, domain.ErrAlreadyExists
		}
	}
	if err := role.UpdateInfo(input.Name, input.Description); err != nil {
		return nil, err
	}
	if err := uc.roleRepo.Update(ctx, role); err != nil {
		return nil, err
	}
	return &UpdateRoleOutput{Role: role}, nil
}
