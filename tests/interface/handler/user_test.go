package handler_test

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-chi/chi/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/domain"
	"go-clean-template/internal/interface/dto"
	"go-clean-template/internal/interface/handler"
)

// ── mock types ───────────────────────────────────────────────────────────────

type MockCreateUserUseCase struct{ mock.Mock }

func (m *MockCreateUserUseCase) Execute(_ context.Context, req *userusecase.CreateUserInput) (*userusecase.CreateUserOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*userusecase.CreateUserOutput), args.Error(1)
}

type MockGetUserUseCase struct{ mock.Mock }

func (m *MockGetUserUseCase) Execute(_ context.Context, req *userusecase.GetUserInput) (*userusecase.GetUserOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*userusecase.GetUserOutput), args.Error(1)
}

type MockListUsersUseCase struct{ mock.Mock }

func (m *MockListUsersUseCase) Execute(_ context.Context, req *userusecase.ListUsersInput) (*userusecase.ListUsersOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*userusecase.ListUsersOutput), args.Error(1)
}

type MockUpdateUserUseCase struct{ mock.Mock }

func (m *MockUpdateUserUseCase) Execute(_ context.Context, id string, req *userusecase.UpdateUserInput) (*userusecase.UpdateUserOutput, error) {
	args := m.Called(id, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*userusecase.UpdateUserOutput), args.Error(1)
}

type MockDeleteUserUseCase struct{ mock.Mock }

func (m *MockDeleteUserUseCase) Execute(_ context.Context, req *userusecase.DeleteUserInput) error {
	args := m.Called(req)
	return args.Error(0)
}

type MockAssignRolesUseCase struct{ mock.Mock }

func (m *MockAssignRolesUseCase) Execute(_ context.Context, id string, req *userusecase.AssignRolesInput) error {
	args := m.Called(id, req)
	return args.Error(0)
}

type MockGetUserRolesUseCase struct{ mock.Mock }

func (m *MockGetUserRolesUseCase) Execute(_ context.Context, req *userusecase.GetUserRolesInput) (*userusecase.GetUserRolesOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*userusecase.GetUserRolesOutput), args.Error(1)
}

// ── GetAll ───────────────────────────────────────────────────────────────────

func TestGetAll_Success(t *testing.T) {
	mockUC := new(MockListUsersUseCase)
	h := handler.NewUserHandler(nil, nil, mockUC, nil, nil, nil, nil)

	respData := &userusecase.ListUsersOutput{
		Users: []*domain.User{
			{ID: "1", Name: "Alice", Email: "alice@example.com"},
		},
		Total:      1,
		Page:       1,
		PageSize:   20,
		TotalPages: 1,
	}
	mockUC.On("Execute", mock.AnythingOfType("*user.ListUsersInput")).Return(respData, nil)

	req := httptest.NewRequest("GET", "/api/v1/users", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/users", h.GetAll)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.PaginatedResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, int64(1), resp.Total)
	assert.Equal(t, 1, resp.Page)
	assert.Equal(t, 20, resp.PageSize)
	assert.Equal(t, 1, resp.TotalPages)

	mockUC.AssertExpectations(t)
}

// ── GetByID ──────────────────────────────────────────────────────────────────

func TestGetByID_Success(t *testing.T) {
	mockUC := new(MockGetUserUseCase)
	h := handler.NewUserHandler(nil, mockUC, nil, nil, nil, nil, nil)

	mockUC.On("Execute", &userusecase.GetUserInput{ID: "123"}).Return(
		&userusecase.GetUserOutput{User: &domain.User{ID: "123", Name: "Alice", Email: "alice@example.com"}}, nil,
	)

	req := httptest.NewRequest("GET", "/api/v1/users/123", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/users/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.UserResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "123", resp.ID)
	assert.Equal(t, "Alice", resp.Name)

	mockUC.AssertExpectations(t)
}

func TestGetByID_NotFound(t *testing.T) {
	mockUC := new(MockGetUserUseCase)
	h := handler.NewUserHandler(nil, mockUC, nil, nil, nil, nil, nil)

	mockUC.On("Execute", &userusecase.GetUserInput{ID: "999"}).Return(nil, domain.ErrNotFound)

	req := httptest.NewRequest("GET", "/api/v1/users/999", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/users/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	var resp map[string]string
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "not found", resp["error"])

	mockUC.AssertExpectations(t)
}

// ── Create ───────────────────────────────────────────────────────────────────

func TestCreate_Success(t *testing.T) {
	mockUC := new(MockCreateUserUseCase)
	h := handler.NewUserHandler(mockUC, nil, nil, nil, nil, nil, nil)

	reqBody := `{"name":"Bob","email":"bob@example.com","password":"secret123"}`
	mockUC.On("Execute", mock.AnythingOfType("*user.CreateUserInput")).Return(
		&userusecase.CreateUserOutput{User: &domain.User{ID: "1", Name: "Bob", Email: "bob@example.com"}}, nil,
	)

	req := httptest.NewRequest("POST", "/api/v1/users", bytes.NewBufferString(reqBody))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp dto.UserResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "Bob", resp.Name)
	assert.Equal(t, "bob@example.com", resp.Email)

	mockUC.AssertExpectations(t)
}

func TestCreate_InvalidBody(t *testing.T) {
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, nil, nil)

	req := httptest.NewRequest("POST", "/api/v1/users", bytes.NewBufferString(`invalid json`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestCreate_AlreadyExists(t *testing.T) {
	mockUC := new(MockCreateUserUseCase)
	h := handler.NewUserHandler(mockUC, nil, nil, nil, nil, nil, nil)

	mockUC.On("Execute", mock.AnythingOfType("*user.CreateUserInput")).Return(nil, domain.ErrAlreadyExists)

	req := httptest.NewRequest("POST", "/api/v1/users", bytes.NewBufferString(`{"name":"Bob","email":"bob@example.com","password":"secret123"}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusConflict, rec.Code)

	mockUC.AssertExpectations(t)
}

// ── Update ───────────────────────────────────────────────────────────────────

func TestUpdate_Success(t *testing.T) {
	mockUC := new(MockUpdateUserUseCase)
	h := handler.NewUserHandler(nil, nil, nil, mockUC, nil, nil, nil)

	mockUC.On("Execute", "1", mock.AnythingOfType("*user.UpdateUserInput")).Return(
		&userusecase.UpdateUserOutput{User: &domain.User{ID: "1", Name: "Updated", Email: "updated@example.com"}}, nil,
	)

	req := httptest.NewRequest("PUT", "/api/v1/users/1", bytes.NewBufferString(`{"name":"Updated","email":"updated@example.com"}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Put("/api/v1/users/{id}", h.Update)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.UserResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "Updated", resp.Name)

	mockUC.AssertExpectations(t)
}

// ── Delete ───────────────────────────────────────────────────────────────────

func TestDelete_Success(t *testing.T) {
	mockUC := new(MockDeleteUserUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, mockUC, nil, nil)

	mockUC.On("Execute", &userusecase.DeleteUserInput{ID: "1"}).Return(nil)

	req := httptest.NewRequest("DELETE", "/api/v1/users/1", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Delete("/api/v1/users/{id}", h.Delete)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNoContent, rec.Code)

	mockUC.AssertExpectations(t)
}

func TestDelete_NotFound(t *testing.T) {
	mockUC := new(MockDeleteUserUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, mockUC, nil, nil)

	mockUC.On("Execute", &userusecase.DeleteUserInput{ID: "999"}).Return(domain.ErrNotFound)

	req := httptest.NewRequest("DELETE", "/api/v1/users/999", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Delete("/api/v1/users/{id}", h.Delete)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	mockUC.AssertExpectations(t)
}

// ── AssignRoles ──────────────────────────────────────────────────────────────

func TestAssignRoles_Success(t *testing.T) {
	mockUC := new(MockAssignRolesUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, mockUC, nil)

	mockUC.On("Execute", "1", mock.AnythingOfType("*user.AssignRolesInput")).Return(nil)

	req := httptest.NewRequest("POST", "/api/v1/users/1/roles", bytes.NewBufferString(`{"role_ids":["role-1","role-2"]}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users/{id}/roles", h.AssignRoles)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	mockUC.AssertExpectations(t)
}

func TestAssignRoles_InvalidBody(t *testing.T) {
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, nil, nil)

	req := httptest.NewRequest("POST", "/api/v1/users/1/roles", bytes.NewBufferString(`invalid`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users/{id}/roles", h.AssignRoles)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestAssignRoles_NotFound(t *testing.T) {
	mockUC := new(MockAssignRolesUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, mockUC, nil)

	mockUC.On("Execute", "999", mock.AnythingOfType("*user.AssignRolesInput")).Return(domain.ErrNotFound)

	req := httptest.NewRequest("POST", "/api/v1/users/999/roles", bytes.NewBufferString(`{"role_ids":["role-1"]}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/users/{id}/roles", h.AssignRoles)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	mockUC.AssertExpectations(t)
}

// ── GetUserRoles ─────────────────────────────────────────────────────────────

func TestGetUserRoles_Success(t *testing.T) {
	mockUC := new(MockGetUserRolesUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, nil, mockUC)

	respData := &userusecase.GetUserRolesOutput{
		Roles: []*domain.Role{
			{ID: "role-1", Name: "admin", Description: "Admin"},
		},
	}
	mockUC.On("Execute", &userusecase.GetUserRolesInput{ID: "1"}).Return(respData, nil)

	req := httptest.NewRequest("GET", "/api/v1/users/1/roles", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/users/{id}/roles", h.GetUserRoles)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp []*dto.RoleResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Len(t, resp, 1)
	assert.Equal(t, "admin", resp[0].Name)

	mockUC.AssertExpectations(t)
}

func TestGetUserRoles_UserNotFound(t *testing.T) {
	mockUC := new(MockGetUserRolesUseCase)
	h := handler.NewUserHandler(nil, nil, nil, nil, nil, nil, mockUC)

	mockUC.On("Execute", &userusecase.GetUserRolesInput{ID: "999"}).Return(
		&userusecase.GetUserRolesOutput{}, domain.ErrNotFound,
	)

	req := httptest.NewRequest("GET", "/api/v1/users/999/roles", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/users/{id}/roles", h.GetUserRoles)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	mockUC.AssertExpectations(t)
}
