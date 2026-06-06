package user_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
)

func TestGetAll_Success(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewListUsersUseCase(mockRepo)

	users := []*domain.User{
		{ID: "1", Name: "Alice", Email: "alice@example.com"},
		{ID: "2", Name: "Bob", Email: "bob@example.com"},
	}
	mockRepo.On("FindAll").Return(users, nil)

	resp, err := uc.Execute(context.Background(), &userusecase.ListUsersInput{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.Equal(t, int64(2), resp.Total)
	assert.Len(t, resp.Users, 2)
	mockRepo.AssertExpectations(t)
}

func TestGetAll_Empty(t *testing.T) {
	mockRepo := new(MockUserRepo)
	uc := userusecase.NewListUsersUseCase(mockRepo)

	mockRepo.On("FindAll").Return([]*domain.User{}, nil)

	resp, err := uc.Execute(context.Background(), &userusecase.ListUsersInput{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.Equal(t, int64(0), resp.Total)
	assert.Empty(t, resp.Users)
	mockRepo.AssertExpectations(t)
}
