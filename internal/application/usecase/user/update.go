package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type UpdateUserInput struct {
	Name    string
	Email   string
	Phone   string
	Avatar  string
	RoleIDs []string
}

type UpdateUserOutput struct {
	User *domain.User
}

type UpdateUserUseCase interface {
	Execute(ctx context.Context, id string, input *UpdateUserInput) (*UpdateUserOutput, error)
}

type updateUserUseCase struct {
	userRepo domain.UserRepository
	roleRepo domain.RoleRepository
}

func NewUpdateUserUseCase(userRepo domain.UserRepository, roleRepo domain.RoleRepository) UpdateUserUseCase {
	return &updateUserUseCase{userRepo: userRepo, roleRepo: roleRepo}
}

func (uc *updateUserUseCase) Execute(ctx context.Context, id string, input *UpdateUserInput) (*UpdateUserOutput, error) {
	user, err := uc.userRepo.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if input.Email != user.Email {
		existing, _ := uc.userRepo.FindByEmail(ctx, input.Email)
		if existing != nil {
			return nil, domain.ErrAlreadyExists
		}
	}
	if err := validateRoleIDs(ctx, uc.roleRepo, input.RoleIDs); err != nil {
		return nil, err
	}
	if err := user.UpdateInfo(input.Name, input.Email, input.Phone, input.Avatar, input.RoleIDs); err != nil {
		return nil, err
	}
	if err := uc.userRepo.Update(ctx, user); err != nil {
		return nil, err
	}
	return &UpdateUserOutput{User: user}, nil
}
