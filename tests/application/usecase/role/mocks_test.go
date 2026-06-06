package role_test

import (
	"context"

	"github.com/stretchr/testify/mock"

	"go-clean-template/internal/domain"
)

type MockRoleRepo struct {
	mock.Mock
}

func (m *MockRoleRepo) FindByID(_ context.Context, id string) (*domain.Role, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.Role), args.Error(1)
}

func (m *MockRoleRepo) FindAll(_ context.Context, _, _ int) ([]*domain.Role, int64, error) {
	args := m.Called()
	return args.Get(0).([]*domain.Role), int64(len(args.Get(0).([]*domain.Role))), args.Error(1)
}

func (m *MockRoleRepo) FindByName(_ context.Context, name string) (*domain.Role, error) {
	args := m.Called(name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.Role), args.Error(1)
}

func (m *MockRoleRepo) Create(_ context.Context, role *domain.Role) error {
	args := m.Called(role)
	return args.Error(0)
}

func (m *MockRoleRepo) Update(_ context.Context, role *domain.Role) error {
	args := m.Called(role)
	return args.Error(0)
}

func (m *MockRoleRepo) Delete(_ context.Context, id string) error {
	args := m.Called(id)
	return args.Error(0)
}
