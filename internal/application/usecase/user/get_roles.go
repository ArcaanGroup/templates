package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type GetUserRolesInput struct {
	ID string
}

type GetUserRolesOutput struct {
	Roles []*domain.Role
}

type GetUserRolesUseCase interface {
	Execute(ctx context.Context, input *GetUserRolesInput) (*GetUserRolesOutput, error)
}

type getUserRolesUseCase struct {
	userRepo domain.UserRepository
	roleRepo domain.RoleRepository
}

func NewGetUserRolesUseCase(userRepo domain.UserRepository, roleRepo domain.RoleRepository) GetUserRolesUseCase {
	return &getUserRolesUseCase{userRepo: userRepo, roleRepo: roleRepo}
}

func (uc *getUserRolesUseCase) Execute(ctx context.Context, input *GetUserRolesInput) (*GetUserRolesOutput, error) {
	user, err := uc.userRepo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	roles := make([]*domain.Role, 0, len(user.RoleIDs))
	for _, rid := range user.RoleIDs {
		role, err := uc.roleRepo.FindByID(ctx, rid)
		if err != nil {
			continue
		}
		roles = append(roles, role)
	}
	return &GetUserRolesOutput{Roles: roles}, nil
}
