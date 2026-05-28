package persistence

import (
	"context"
	"sort"
	"sync"

	"go-clean-template/internal/domain"
)

type RoleRepository struct {
	mu    sync.RWMutex
	roles map[string]*domain.Role
}

func NewRoleRepository() *RoleRepository {
	return &RoleRepository{
		roles: make(map[string]*domain.Role),
	}
}

func (r *RoleRepository) FindByID(_ context.Context, id string) (*domain.Role, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	role, ok := r.roles[id]
	if !ok {
		return nil, domain.ErrNotFound
	}
	return role, nil
}

// FindAll returns all roles sorted by CreatedAt ascending, then applies
// offset/limit. The deterministic sort ensures stable pagination across calls.
func (r *RoleRepository) FindAll(_ context.Context, offset, limit int) ([]*domain.Role, int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	all := make([]*domain.Role, 0, len(r.roles))
	for _, role := range r.roles {
		all = append(all, role)
	}
	sort.Slice(all, func(i, j int) bool {
		return all[i].CreatedAt.Before(all[j].CreatedAt)
	})

	total := int64(len(all))
	if offset >= len(all) {
		return nil, total, nil
	}
	end := offset + limit
	if end > len(all) {
		end = len(all)
	}
	return all[offset:end], total, nil
}

func (r *RoleRepository) FindByName(_ context.Context, name string) (*domain.Role, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	for _, role := range r.roles {
		if role.Name == name {
			return role, nil
		}
	}
	return nil, domain.ErrNotFound
}

func (r *RoleRepository) Create(_ context.Context, role *domain.Role) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.roles[role.ID] = role
	return nil
}

func (r *RoleRepository) Update(_ context.Context, role *domain.Role) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.roles[role.ID]; !ok {
		return domain.ErrNotFound
	}
	r.roles[role.ID] = role
	return nil
}

func (r *RoleRepository) Delete(_ context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.roles[id]; !ok {
		return domain.ErrNotFound
	}
	delete(r.roles, id)
	return nil
}
