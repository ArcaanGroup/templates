package role_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
)

func TestRoleGetByID_Success(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewGetRoleUseCase(mockRepo)

	role := &domain.Role{ID: "123", Name: "admin", Description: "Administrator role"}
	mockRepo.On("FindByID", "123").Return(role, nil)

	resp, err := uc.Execute(context.Background(), &roleusecase.GetRoleInput{ID: "123"})

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Role)
	assert.Equal(t, "123", resp.Role.ID)
	assert.Equal(t, "admin", resp.Role.Name)
	mockRepo.AssertExpectations(t)
}

func TestRoleGetByID_NotFound(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewGetRoleUseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	resp, err := uc.Execute(context.Background(), &roleusecase.GetRoleInput{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	assert.Nil(t, resp)
	mockRepo.AssertExpectations(t)
}
