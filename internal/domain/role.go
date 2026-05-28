package domain

import (
	"context"
	"strings"
	"time"
)

type Role struct {
	ID          string
	Name        string
	Description string
	CreatedAt   time.Time
	UpdatedAt   time.Time
}

func NewRole(name, description string) (*Role, error) {
	r := &Role{
		ID:          GenerateID(),
		Name:        name,
		Description: description,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	if err := r.Validate(); err != nil {
		return nil, err
	}
	return r, nil
}

func (r *Role) UpdateInfo(name, description string) error {
	r.Name = name
	r.Description = description
	r.UpdatedAt = time.Now()
	return r.Validate()
}

func (r *Role) Validate() error {
	var errs []string
	if strings.TrimSpace(r.Name) == "" {
		errs = append(errs, "name is required")
	}
	if len(errs) > 0 {
		return &DomainError{
			Code:    "VALIDATION_ERROR",
			Message: strings.Join(errs, "; "),
			Err:     ErrInvalidInput,
		}
	}
	return nil
}

// RoleRepository defines the persistence contract for Role aggregates.
// offset and limit are database-level primitives; pagination logic belongs in
// the application layer (see dto.Pagination).
type RoleRepository interface {
	FindByID(ctx context.Context, id string) (*Role, error)
	FindAll(ctx context.Context, offset, limit int) ([]*Role, int64, error)
	FindByName(ctx context.Context, name string) (*Role, error)
	Create(ctx context.Context, role *Role) error
	Update(ctx context.Context, role *Role) error
	Delete(ctx context.Context, id string) error
}
