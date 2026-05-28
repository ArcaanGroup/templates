package handler

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"time"

	"go-clean-template/internal/domain"
	"go-clean-template/internal/interface/dto"
)

func parsePagination(r *http.Request) dto.PaginationRequest {
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	pageSize, _ := strconv.Atoi(r.URL.Query().Get("page_size"))
	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}
	return dto.PaginationRequest{Page: page, PageSize: pageSize}
}

func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, err error) {
	var domainErr *domain.DomainError

	switch {
	case errors.Is(err, domain.ErrNotFound):
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "not found"})
	case errors.Is(err, domain.ErrAlreadyExists):
		writeJSON(w, http.StatusConflict, map[string]string{"error": "already exists"})
	case errors.Is(err, domain.ErrInvalidInput):
		if errors.As(err, &domainErr) {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": domainErr.Message})
		} else {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid input"})
		}
	default:
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal server error"})
	}
}

func toUserResponse(user *domain.User) *dto.UserResponse {
	r := &dto.UserResponse{
		ID:            user.ID,
		Name:          user.Name,
		Email:         user.Email,
		Phone:         user.Phone,
		Avatar:        user.Avatar,
		EmailVerified: user.EmailVerified,
		PhoneVerified: user.PhoneVerified,
		WalletBalance: user.WalletBalance,
		OrderCount:    user.OrderCount,
		Language:      user.Language,
		Currency:      user.Currency,
		CreatedAt:     user.CreatedAt.Format(time.RFC3339),
		UpdatedAt:     user.UpdatedAt.Format(time.RFC3339),
	}
	if user.LastLoginAt != nil {
		s := user.LastLoginAt.Format(time.RFC3339)
		r.LastLoginAt = &s
	}
	return r
}

func toRoleResponse(role *domain.Role) *dto.RoleResponse {
	return &dto.RoleResponse{
		ID:          role.ID,
		Name:        role.Name,
		Description: role.Description,
		CreatedAt:   role.CreatedAt.Format(time.RFC3339),
		UpdatedAt:   role.UpdatedAt.Format(time.RFC3339),
	}
}
