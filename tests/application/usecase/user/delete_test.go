package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestDelete_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewDeleteUserUseCase(mockRepo)

	user := &domain.User{ID: "1", Name: "Alice", Email: "alice@example.com"}
	mockRepo.On("FindByID", "1").Return(user, nil)
	mockRepo.On("Delete", "1").Return(nil)

	err := uc.Execute(context.Background(), &userusecase.DeleteUserInput{ID: "1"})

	assert.NoError(t, err)
	mockRepo.AssertExpectations(t)
}

func TestDelete_NotFound(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewDeleteUserUseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	err := uc.Execute(context.Background(), &userusecase.DeleteUserInput{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	mockRepo.AssertExpectations(t)
}
