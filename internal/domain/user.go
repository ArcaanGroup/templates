package domain

import (
	"context"
	"crypto/sha256"
	"fmt"
	"strings"
	"time"
)

type User struct {
	ID            string
	Name          string
	Email         string
	Phone         string
	NationalID    string
	PasswordHash  string
	EmailVerified bool
	PhoneVerified bool
	Avatar        string
	RoleIDs       []string
	OrderCount    int
	TotalSpent    int64
	WalletBalance int64
	Language      string
	Currency      string
	LastLoginAt   *time.Time
	LastIP        string
	CreatedAt     time.Time
	UpdatedAt     time.Time
	DeletedAt     *time.Time
}

func NewUser(name, email, phone string, roleIDs []string) (*User, error) {
	u := &User{
		ID:        GenerateID(),
		Name:      name,
		Email:     email,
		Phone:     phone,
		RoleIDs:   roleIDs,
		Language:  "fa",
		Currency:  "IRR",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	if err := u.Validate(); err != nil {
		return nil, err
	}
	return u, nil
}

func (u *User) UpdateInfo(name, email, phone, avatar string, roleIDs []string) error {
	u.Name = name
	u.Email = email
	u.Phone = phone
	u.Avatar = avatar
	u.RoleIDs = roleIDs
	u.UpdatedAt = time.Now()
	return u.Validate()
}

func (u *User) AssignRoles(roleIDs []string) {
	u.RoleIDs = roleIDs
	u.UpdatedAt = time.Now()
}

// MarkDeleted performs a soft-delete by stamping DeletedAt.
// The repository implementation is responsible for honouring this field.
func (u *User) MarkDeleted() {
	now := time.Now()
	u.DeletedAt = &now
	u.UpdatedAt = now
}

// UpdateWallet applies delta to WalletBalance, enforcing the non-negative invariant.
// Call repo.Update after this to persist the change.
func (u *User) UpdateWallet(delta int64) error {
	if u.WalletBalance+delta < 0 {
		return &DomainError{
			Code:    "INSUFFICIENT_BALANCE",
			Message: "wallet balance cannot be negative",
			Err:     ErrInvalidInput,
		}
	}
	u.WalletBalance += delta
	u.UpdatedAt = time.Now()
	return nil
}

func (u *User) Validate() error {
	var errs []string
	if strings.TrimSpace(u.Name) == "" {
		errs = append(errs, "name is required")
	}
	if strings.TrimSpace(u.Email) == "" {
		errs = append(errs, "email is required")
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

func (u *User) SetPassword(password string) error {
	if password == "" {
		return &DomainError{
			Code:    "VALIDATION_ERROR",
			Message: "password is required",
			Err:     ErrInvalidInput,
		}
	}
	u.PasswordHash = hashPassword(password)
	return nil
}

func hashPassword(password string) string {
	sum := sha256.Sum256([]byte(password))
	return fmt.Sprintf("%x", sum)
}

// UserRepository defines the persistence contract for User aggregates.
// offset and limit are database-level primitives; pagination logic belongs in
// the application layer (see dto.Pagination).
type UserRepository interface {
	FindByID(ctx context.Context, id string) (*User, error)
	FindAll(ctx context.Context, offset, limit int) ([]*User, int64, error)
	FindByEmail(ctx context.Context, email string) (*User, error)
	Create(ctx context.Context, user *User) error
	Update(ctx context.Context, user *User) error
	Delete(ctx context.Context, id string) error
}
