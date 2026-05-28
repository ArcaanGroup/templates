package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type GetUserInput struct {
	ID string
}

type GetUserOutput struct {
	User *domain.User
}

type GetUserUseCase interface {
	Execute(ctx context.Context, input *GetUserInput) (*GetUserOutput, error)
}

type getUserUseCase struct {
	userRepo domain.UserRepository
}

func NewGetUserUseCase(userRepo domain.UserRepository) GetUserUseCase {
	return &getUserUseCase{userRepo: userRepo}
}

func (uc *getUserUseCase) Execute(ctx context.Context, input *GetUserInput) (*GetUserOutput, error) {
	user, err := uc.userRepo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	return &GetUserOutput{User: user}, nil
}
