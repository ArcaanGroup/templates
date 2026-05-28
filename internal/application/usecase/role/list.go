package role

import (
	"context"

	"go-clean-template/internal/domain"
)

type ListRolesInput struct {
	Page     int
	PageSize int
}

type ListRolesOutput struct {
	Roles      []*domain.Role
	Total      int64
	Page       int
	PageSize   int
	TotalPages int
}

type ListRolesUseCase interface {
	Execute(ctx context.Context, input *ListRolesInput) (*ListRolesOutput, error)
}

type listRolesUseCase struct {
	roleRepo domain.RoleRepository
}

func NewListRolesUseCase(roleRepo domain.RoleRepository) ListRolesUseCase {
	return &listRolesUseCase{roleRepo: roleRepo}
}

func (uc *listRolesUseCase) Execute(ctx context.Context, input *ListRolesInput) (*ListRolesOutput, error) {
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
	roles, total, err := uc.roleRepo.FindAll(ctx, offset, input.PageSize)
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

	return &ListRolesOutput{
		Roles:      roles,
		Total:      total,
		Page:       input.Page,
		PageSize:   input.PageSize,
		TotalPages: totalPages,
	}, nil
}
