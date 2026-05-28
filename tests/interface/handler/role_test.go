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

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/domain"
	"go-clean-template/internal/interface/dto"
	"go-clean-template/internal/interface/handler"
)

// ── mock types ───────────────────────────────────────────────────────────────

type MockRoleCreateUseCase struct{ mock.Mock }

func (m *MockRoleCreateUseCase) Execute(_ context.Context, req *roleusecase.CreateRoleInput) (*roleusecase.CreateRoleOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*roleusecase.CreateRoleOutput), args.Error(1)
}

type MockRoleGetUseCase struct{ mock.Mock }

func (m *MockRoleGetUseCase) Execute(_ context.Context, req *roleusecase.GetRoleInput) (*roleusecase.GetRoleOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*roleusecase.GetRoleOutput), args.Error(1)
}

type MockRoleListUseCase struct{ mock.Mock }

func (m *MockRoleListUseCase) Execute(_ context.Context, req *roleusecase.ListRolesInput) (*roleusecase.ListRolesOutput, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*roleusecase.ListRolesOutput), args.Error(1)
}

type MockRoleUpdateUseCase struct{ mock.Mock }

func (m *MockRoleUpdateUseCase) Execute(_ context.Context, id string, req *roleusecase.UpdateRoleInput) (*roleusecase.UpdateRoleOutput, error) {
	args := m.Called(id, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*roleusecase.UpdateRoleOutput), args.Error(1)
}

type MockRoleDeleteUseCase struct{ mock.Mock }

func (m *MockRoleDeleteUseCase) Execute(_ context.Context, req *roleusecase.DeleteRoleInput) error {
	args := m.Called(req)
	return args.Error(0)
}

// ── GetAll ───────────────────────────────────────────────────────────────────

func TestRoleGetAll_Success(t *testing.T) {
	mockUC := new(MockRoleListUseCase)
	h := handler.NewRoleHandler(nil, nil, mockUC, nil, nil)

	respData := &roleusecase.ListRolesOutput{
		Roles: []*domain.Role{
			{ID: "1", Name: "admin", Description: "Admin"},
		},
		Total:      1,
		Page:       1,
		PageSize:   20,
		TotalPages: 1,
	}
	mockUC.On("Execute", mock.AnythingOfType("*role.ListRolesInput")).Return(respData, nil)

	req := httptest.NewRequest("GET", "/api/v1/roles", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/roles", h.GetAll)
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

func TestRoleGetByID_Success(t *testing.T) {
	mockUC := new(MockRoleGetUseCase)
	h := handler.NewRoleHandler(nil, mockUC, nil, nil, nil)

	mockUC.On("Execute", &roleusecase.GetRoleInput{ID: "123"}).Return(
		&roleusecase.GetRoleOutput{Role: &domain.Role{ID: "123", Name: "admin", Description: "Admin"}}, nil,
	)

	req := httptest.NewRequest("GET", "/api/v1/roles/123", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/roles/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.RoleResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "123", resp.ID)
	assert.Equal(t, "admin", resp.Name)

	mockUC.AssertExpectations(t)
}

func TestRoleGetByID_NotFound(t *testing.T) {
	mockUC := new(MockRoleGetUseCase)
	h := handler.NewRoleHandler(nil, mockUC, nil, nil, nil)

	mockUC.On("Execute", &roleusecase.GetRoleInput{ID: "999"}).Return(nil, domain.ErrNotFound)

	req := httptest.NewRequest("GET", "/api/v1/roles/999", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/roles/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	var resp map[string]string
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "not found", resp["error"])

	mockUC.AssertExpectations(t)
}

// ── Create ───────────────────────────────────────────────────────────────────

func TestRoleCreate_Success(t *testing.T) {
	mockUC := new(MockRoleCreateUseCase)
	h := handler.NewRoleHandler(mockUC, nil, nil, nil, nil)

	reqBody := `{"name":"admin","description":"Administrator role"}`
	mockUC.On("Execute", mock.AnythingOfType("*role.CreateRoleInput")).Return(
		&roleusecase.CreateRoleOutput{Role: &domain.Role{ID: "1", Name: "admin", Description: "Administrator role"}}, nil,
	)

	req := httptest.NewRequest("POST", "/api/v1/roles", bytes.NewBufferString(reqBody))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/roles", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusCreated, rec.Code)

	var resp dto.RoleResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "admin", resp.Name)

	mockUC.AssertExpectations(t)
}

func TestRoleCreate_InvalidBody(t *testing.T) {
	h := handler.NewRoleHandler(nil, nil, nil, nil, nil)

	req := httptest.NewRequest("POST", "/api/v1/roles", bytes.NewBufferString(`invalid json`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/roles", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}

func TestRoleCreate_AlreadyExists(t *testing.T) {
	mockUC := new(MockRoleCreateUseCase)
	h := handler.NewRoleHandler(mockUC, nil, nil, nil, nil)

	mockUC.On("Execute", mock.AnythingOfType("*role.CreateRoleInput")).Return(nil, domain.ErrAlreadyExists)

	req := httptest.NewRequest("POST", "/api/v1/roles", bytes.NewBufferString(`{"name":"admin","description":"Admin"}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/roles", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusConflict, rec.Code)

	mockUC.AssertExpectations(t)
}

// ── Update ───────────────────────────────────────────────────────────────────

func TestRoleUpdate_Success(t *testing.T) {
	mockUC := new(MockRoleUpdateUseCase)
	h := handler.NewRoleHandler(nil, nil, nil, mockUC, nil)

	mockUC.On("Execute", "1", mock.AnythingOfType("*role.UpdateRoleInput")).Return(
		&roleusecase.UpdateRoleOutput{Role: &domain.Role{ID: "1", Name: "updated", Description: "Updated description"}}, nil,
	)

	req := httptest.NewRequest("PUT", "/api/v1/roles/1", bytes.NewBufferString(`{"name":"updated","description":"Updated description"}`))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Put("/api/v1/roles/{id}", h.Update)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.RoleResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "updated", resp.Name)

	mockUC.AssertExpectations(t)
}

// ── Delete ───────────────────────────────────────────────────────────────────

func TestRoleDelete_Success(t *testing.T) {
	mockUC := new(MockRoleDeleteUseCase)
	h := handler.NewRoleHandler(nil, nil, nil, nil, mockUC)

	mockUC.On("Execute", &roleusecase.DeleteRoleInput{ID: "1"}).Return(nil)

	req := httptest.NewRequest("DELETE", "/api/v1/roles/1", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Delete("/api/v1/roles/{id}", h.Delete)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNoContent, rec.Code)

	mockUC.AssertExpectations(t)
}

func TestRoleDelete_NotFound(t *testing.T) {
	mockUC := new(MockRoleDeleteUseCase)
	h := handler.NewRoleHandler(nil, nil, nil, nil, mockUC)

	mockUC.On("Execute", &roleusecase.DeleteRoleInput{ID: "999"}).Return(domain.ErrNotFound)

	req := httptest.NewRequest("DELETE", "/api/v1/roles/999", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Delete("/api/v1/roles/{id}", h.Delete)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	mockUC.AssertExpectations(t)
}
