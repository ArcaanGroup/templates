package user

import (
	"context"

	"go-clean-template/internal/domain"
)

type ListUsersInput struct {
	Page     int
	PageSize int
}

type ListUsersOutput struct {
	Users      []*domain.User
	Total      int64
	Page       int
	PageSize   int
	TotalPages int
}

type ListUsersUseCase interface {
	Execute(ctx context.Context, input *ListUsersInput) (*ListUsersOutput, error)
}

type listUsersUseCase struct {
	userRepo domain.UserRepository
}

func NewListUsersUseCase(userRepo domain.UserRepository) ListUsersUseCase {
	return &listUsersUseCase{userRepo: userRepo}
}

func (uc *listUsersUseCase) Execute(ctx context.Context, input *ListUsersInput) (*ListUsersOutput, error) {
	if input.Page < 1 {
		input.Page = 1
	}
	if input.PageSize < 1 {
		input.PageSize = 20
	}
	if input.PageSize > 100 {
		input.PageSize = 100
	}
	offset := (input.Page - 1) * input.PageSize
	users, total, err := uc.userRepo.FindAll(ctx, offset, input.PageSize)
	if err != nil {
		return nil, err
	}

	totalPages := int(total / int64(input.PageSize))
	if total%int64(input.PageSize) > 0 {
		totalPages++
	}
	if totalPages < 1 {
		totalPages = 1
	}

	return &ListUsersOutput{
		Users:      users,
		Total:      total,
		Page:       input.Page,
		PageSize:   input.PageSize,
		TotalPages: totalPages,
	}, nil
}
