package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestCreateUser_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewCreateUserUseCase(mockRepo, mockRole)

	mockRepo.On("FindByEmail", "test@example.com").Return(nil, domain.ErrNotFound)
	mockRepo.On("Create", mock.AnythingOfType("*domain.User")).Return(nil)

	req := &userusecase.CreateUserInput{Name: "Alice", Email: "test@example.com", Password: "secret123"}
	resp, err := uc.Execute(context.Background(), req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.User)
	assert.Equal(t, "Alice", resp.User.Name)
	assert.Equal(t, "test@example.com", resp.User.Email)
	mockRepo.AssertExpectations(t)
}

func TestCreateUser_DuplicateEmail(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewCreateUserUseCase(mockRepo, mockRole)

	existing := &domain.User{ID: "1", Name: "Existing", Email: "dup@example.com"}
	mockRepo.On("FindByEmail", "dup@example.com").Return(existing, nil)

	req := &userusecase.CreateUserInput{Name: "Test", Email: "dup@example.com", Password: "secret123"}
	resp, err := uc.Execute(context.Background(), req)

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrAlreadyExists)
	assert.Nil(t, resp)
	mockRepo.AssertExpectations(t)
}

func TestCreateUser_InvalidInput(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewCreateUserUseCase(mockRepo, mockRole)

	resp, err := uc.Execute(context.Background(), &userusecase.CreateUserInput{Name: "", Email: "", Password: ""})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
	assert.Nil(t, resp)
}

func TestCreateUser_WithRoles(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewCreateUserUseCase(mockRepo, mockRole)

	mockRepo.On("FindByEmail", "test@example.com").Return(nil, domain.ErrNotFound)
	mockRole.On("FindByID", "role-1").Return(&domain.Role{ID: "role-1", Name: "admin"}, nil)
	mockRepo.On("Create", mock.AnythingOfType("*domain.User")).Return(nil)

	req := &userusecase.CreateUserInput{Name: "Alice", Email: "test@example.com", Password: "secret123", RoleIDs: []string{"role-1"}}
	resp, err := uc.Execute(context.Background(), req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.User)
	mockRepo.AssertExpectations(t)
	mockRole.AssertExpectations(t)
}

func TestCreateUser_InvalidRole(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewCreateUserUseCase(mockRepo, mockRole)

	mockRepo.On("FindByEmail", "test@example.com").Return(nil, domain.ErrNotFound)
	mockRole.On("FindByID", "bad-role").Return(nil, domain.ErrNotFound)

	req := &userusecase.CreateUserInput{Name: "Alice", Email: "test@example.com", Password: "secret123", RoleIDs: []string{"bad-role"}}
	resp, err := uc.Execute(context.Background(), req)

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	assert.Nil(t, resp)
	mockRole.AssertExpectations(t)
}
