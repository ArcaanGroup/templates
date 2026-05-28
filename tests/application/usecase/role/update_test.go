package role_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
)

func TestUpdateRole_Success(t *testing.T) {
	mockRepo := new(MockRoleRepo)
	uc := roleusecase.NewUpdateRoleUseCase(mockRepo)

	existing := &domain.Role{ID: "1", Name: "old", Description: "Old description"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRepo.On("FindByName", "new").Return(nil, domain.ErrNotFound)
	mockRepo.On("Update", mock.AnythingOfType("*domain.Role")).Return(nil)

	req := &roleusecase.UpdateRoleInput{Name: "new", Description: "New description"}
	resp, err := uc.Execute(context.Background(), "1", req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.Role)
	assert.Equal(t, "new", resp.Role.Name)
	assert.Equal(t, "New description", resp.Role.Description)
	mockRepo.AssertExpectations(t)
}
