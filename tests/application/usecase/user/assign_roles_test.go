package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestAssignRoles_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewAssignRolesUseCase(mockRepo, mockRole)

	existing := &domain.User{ID: "1", Name: "Alice", Email: "alice@example.com"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRole.On("FindByID", "role-1").Return(&domain.Role{ID: "role-1", Name: "admin"}, nil)
	mockRepo.On("Update", mock.AnythingOfType("*domain.User")).Return(nil)

	err := uc.Execute(context.Background(), "1", &userusecase.AssignRolesInput{RoleIDs: []string{"role-1"}})

	assert.NoError(t, err)
	mockRepo.AssertExpectations(t)
	mockRole.AssertExpectations(t)
}

func TestAssignRoles_UserNotFound(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewAssignRolesUseCase(mockRepo, mockRole)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	err := uc.Execute(context.Background(), "999", &userusecase.AssignRolesInput{RoleIDs: []string{"role-1"}})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	mockRepo.AssertExpectations(t)
}

func TestAssignRoles_InvalidRole(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewAssignRolesUseCase(mockRepo, mockRole)

	existing := &domain.User{ID: "1", Name: "Alice", Email: "alice@example.com"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRole.On("FindByID", "bad-role").Return(nil, domain.ErrNotFound)

	err := uc.Execute(context.Background(), "1", &userusecase.AssignRolesInput{RoleIDs: []string{"bad-role"}})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	mockRole.AssertExpectations(t)
}
