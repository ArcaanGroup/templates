package role_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
)

func TestDeleteRole_Success(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewDeleteRoleUseCase(mockRepo)

	role := &domain.Role{ID: "1", Name: "admin", Description: "Admin"}
	mockRepo.On("FindByID", "1").Return(role, nil)
	mockRepo.On("Delete", "1").Return(nil)

	err := uc.Execute(context.Background(), &roleusecase.DeleteRoleInput{ID: "1"})

	assert.NoError(t, err)
	mockRepo.AssertExpectations(t)
}

func TestDeleteRole_NotFound(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewDeleteRoleUseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	err := uc.Execute(context.Background(), &roleusecase.DeleteRoleInput{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	mockRepo.AssertExpectations(t)
}
