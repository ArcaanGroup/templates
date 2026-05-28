package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type CreateUserInput struct {
	Name     string
	Email    string
	Phone    string
	Password string
	RoleIDs  []string
}

type CreateUserOutput struct {
	User *domain.User
}

type CreateUserUseCase interface {
	Execute(ctx context.Context, input *CreateUserInput) (*CreateUserOutput, error)
}

type createUserUseCase struct {
	userRepo domain.UserRepository
	roleRepo domain.RoleRepository
}

func NewCreateUserUseCase(userRepo domain.UserRepository, roleRepo domain.RoleRepository) CreateUserUseCase {
	return &createUserUseCase{userRepo: userRepo, roleRepo: roleRepo}
}

func (uc *createUserUseCase) Execute(ctx context.Context, input *CreateUserInput) (*CreateUserOutput, error) {
	user, err := domain.NewUser(input.Name, input.Email, input.Phone, input.RoleIDs)
	if err != nil {
		return nil, err
	}
	if err := user.SetPassword(input.Password); err != nil {
		return nil, err
	}
	existing, _ := uc.userRepo.FindByEmail(ctx, input.Email)
	if existing != nil {
		return nil, domain.ErrAlreadyExists
	}
	if err := validateRoleIDs(ctx, uc.roleRepo, input.RoleIDs); err != nil {
		return nil, err
	}
	if err := uc.userRepo.Create(ctx, user); err != nil {
		return nil, err
	}
	return &CreateUserOutput{User: user}, nil
}
