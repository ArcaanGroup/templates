package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestGetByID_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewGetUserUseCase(mockRepo)

	user := &domain.User{ID: "123", Name: "Alice", Email: "alice@example.com"}
	mockRepo.On("FindByID", "123").Return(user, nil)

	resp, err := uc.Execute(context.Background(), &userusecase.GetUserInput{ID: "123"})

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.NotNil(t, resp.User)
	assert.Equal(t, "123", resp.User.ID)
	assert.Equal(t, "Alice", resp.User.Name)

	mockRepo.AssertExpectations(t)
}

func TestGetByID_NotFound(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewGetUserUseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	resp, err := uc.Execute(context.Background(), &userusecase.GetUserInput{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	assert.Nil(t, resp)
	mockRepo.AssertExpectations(t)
}
