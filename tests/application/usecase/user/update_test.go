package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestUpdate_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	mockRole := new(MockRoleRepo)
	uc := userusecase.NewUpdateUserUseCase(mockRepo, mockRole)

	existing := &domain.User{ID: "1", Name: "Old", Email: "old@example.com"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRepo.On("FindByEmail", "new@example.com").Return(nil, domain.ErrNotFound)
	mockRepo.On("Update", mock.AnythingOfType("*domain.User")).Return(nil)

	req := &userusecase.UpdateUserInput{Name: "New", Email: "new@example.com"}
	resp, err := uc.Execute(context.Background(), "1", req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.User)
	assert.Equal(t, "New", resp.User.Name)
	assert.Equal(t, "new@example.com", resp.User.Email)
	mockRepo.AssertExpectations(t)
}
