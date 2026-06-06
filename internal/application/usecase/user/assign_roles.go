package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type AssignRolesInput struct {
	RoleIDs []string
}

type AssignRolesUseCase interface {
	Execute(ctx context.Context, id string, input *AssignRolesInput) error
}

type assignRolesUseCase struct {
	userRepo domain.UserRepository
	roleRepo domain.RoleRepository
}

func NewAssignRolesUseCase(userRepo domain.UserRepository, roleRepo domain.RoleRepository) AssignRolesUseCase {
	return &assignRolesUseCase{userRepo: userRepo, roleRepo: roleRepo}
}

func (uc *assignRolesUseCase) Execute(ctx context.Context, id string, input *AssignRolesInput) error {
	user, err := uc.userRepo.FindByID(ctx, id)
	if err != nil {
		return err
	}
	if err := validateRoleIDs(ctx, uc.roleRepo, input.RoleIDs); err != nil {
		return err
	}
	user.AssignRoles(input.RoleIDs)
	return uc.userRepo.Update(ctx, user)
}
