package role_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
)

func TestCreateRole_Success(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewCreateRoleUseCase(mockRepo)

	mockRepo.On("FindByName", "admin").Return(nil, domain.ErrNotFound)
	mockRepo.On("Create", mock.AnythingOfType("*domain.Role")).Return(nil)

	req := &roleusecase.CreateRoleInput{Name: "admin", Description: "Administrator role"}
	resp, err := uc.Execute(context.Background(), req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Role)
	assert.Equal(t, "admin", resp.Role.Name)
	assert.Equal(t, "Administrator role", resp.Role.Description)
	mockRepo.AssertExpectations(t)
}

func TestCreateRole_DuplicateName(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewCreateRoleUseCase(mockRepo)

	existing := &domain.Role{ID: "1", Name: "admin", Description: "Existing"}
	mockRepo.On("FindByName", "admin").Return(existing, nil)

	req := &roleusecase.CreateRoleInput{Name: "admin", Description: "Duplicate"}
	resp, err := uc.Execute(context.Background(), req)

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrAlreadyExists)
	assert.Nil(t, resp)
	mockRepo.AssertExpectations(t)
}

func TestCreateRole_InvalidInput(t *testing.T) {
	uc := roleusecase.NewCreateRoleUseCase(nil)

	resp, err := uc.Execute(context.Background(), &roleusecase.CreateRoleInput{Name: ""})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
	assert.Nil(t, resp)
}
