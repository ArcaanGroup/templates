package persistence

import (
	"context"
	"sort"
	"sync"

	"go-clean-template/internal/domain"
)

type UserRepository struct {
	mu    sync.RWMutex
	users map[string]*domain.User
}

func NewUserRepository() *UserRepository {
	return &UserRepository{
		users: make(map[string]*domain.User),
	}
}

func (r *UserRepository) FindByID(_ context.Context, id string) (*domain.User, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	user, ok := r.users[id]
	if !ok || user.DeletedAt != nil {
		return nil, domain.ErrNotFound
	}
	return user, nil
}

// FindAll returns non-deleted users sorted by CreatedAt ascending, then applies
// offset/limit. The deterministic sort ensures stable pagination across calls.
func (r *UserRepository) FindAll(_ context.Context, offset, limit int) ([]*domain.User, int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	all := make([]*domain.User, 0, len(r.users))
	for _, user := range r.users {
		if user.DeletedAt == nil {
			all = append(all, user)
		}
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

func (r *UserRepository) FindByEmail(_ context.Context, email string) (*domain.User, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	for _, user := range r.users {
		if user.DeletedAt == nil && user.Email == email {
			return user, nil
		}
	}
	return nil, domain.ErrNotFound
}

func (r *UserRepository) Create(_ context.Context, user *domain.User) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.users[user.ID] = user
	return nil
}

func (r *UserRepository) Update(_ context.Context, user *domain.User) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.users[user.ID]; !ok {
		return domain.ErrNotFound
	}
	r.users[user.ID] = user
	return nil
}

// Delete performs a soft-delete by calling MarkDeleted on the entity.
// The record remains in the store but is invisible to all Find* methods.
func (r *UserRepository) Delete(_ context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	user, ok := r.users[id]
	if !ok || user.DeletedAt != nil {
		return domain.ErrNotFound
	}
	user.MarkDeleted()
	return nil
}
