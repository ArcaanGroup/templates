package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type DeleteUserInput struct {
	ID string
}

type DeleteUserUseCase interface {
	Execute(ctx context.Context, input *DeleteUserInput) error
}

type deleteUserUseCase struct {
	userRepo domain.UserRepository
}

func NewDeleteUserUseCase(userRepo domain.UserRepository) DeleteUserUseCase {
	return &deleteUserUseCase{userRepo: userRepo}
}

func (uc *deleteUserUseCase) Execute(ctx context.Context, input *DeleteUserInput) error {
	if _, err := uc.userRepo.FindByID(ctx, input.ID); err != nil {
		return err
	}
	return uc.userRepo.Delete(ctx, input.ID)
}
