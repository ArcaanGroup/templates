package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestGetUserRoles_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewGetUserRolesUseCase(mockRepo, mockRole)

	user := &domain.User{ID: "1", Name: "Alice", Email: "alice@example.com", RoleIDs: []string{"role-1", "role-2"}}
	role1 := &domain.Role{ID: "role-1", Name: "admin", Description: "Admin"}
	role2 := &domain.Role{ID: "role-2", Name: "editor", Description: "Editor"}

	mockRepo.On("FindByID", "1").Return(user, nil)
	mockRole.On("FindByID", "role-1").Return(role1, nil)
	mockRole.On("FindByID", "role-2").Return(role2, nil)

	resp, err := uc.Execute(context.Background(), &userusecase.GetUserRolesInput{ID: "1"})

	assert.NoError(t, err)
	assert.Len(t, resp.Roles, 2)
	mockRepo.AssertExpectations(t)
	mockRole.AssertExpectations(t)
}
