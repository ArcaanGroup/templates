package role_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
)

func TestRoleGetAll_Success(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewListRolesUseCase(mockRepo)

	roles := []*domain.Role{
		{ID: "1", Name: "admin", Description: "Admin"},
		{ID: "2", Name: "user", Description: "User"},
	}
	mockRepo.On("FindAll").Return(roles, nil)

	resp, err := uc.Execute(context.Background(), &roleusecase.ListRolesInput{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.Equal(t, int64(2), resp.Total)
	assert.Len(t, resp.Roles, 2)
	mockRepo.AssertExpectations(t)
}

func TestRoleGetAll_Empty(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewListRolesUseCase(mockRepo)

	mockRepo.On("FindAll").Return([]*domain.Role{}, nil)

	resp, err := uc.Execute(context.Background(), &roleusecase.ListRolesInput{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.Equal(t, int64(0), resp.Total)
	assert.Empty(t, resp.Roles)
	mockRepo.AssertExpectations(t)
}
