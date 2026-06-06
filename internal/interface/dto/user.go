package dto

type CreateUserRequest struct {
	Name     string   `json:"name"     example:"Alice"`
	Email    string   `json:"email"    example:"alice@example.com"`
	Phone    string   `json:"phone"    example:"09121234567"`
	Password string   `json:"password" example:"secret123"`
	RoleIDs  []string `json:"role_ids" example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
}

type UpdateUserRequest struct {
	Name    string   `json:"name"     example:"Alice"`
	Email   string   `json:"email"    example:"alice@example.com"`
	Phone   string   `json:"phone"    example:"09121234567"`
	Avatar  string   `json:"avatar"   example:"https://example.com/avatar.jpg"`
	RoleIDs []string `json:"role_ids" example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
}

type AssignRolesRequest struct {
	RoleIDs []string `json:"role_ids" example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
}

type UserResponse struct {
	ID            string  `json:"id"             example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
	Name          string  `json:"name"           example:"Alice"`
	Email         string  `json:"email"          example:"alice@example.com"`
	Phone         string  `json:"phone"          example:"09121234567"`
	Avatar        string  `json:"avatar"         example:"https://example.com/avatar.jpg"`
	EmailVerified bool    `json:"email_verified" example:"true"`
	PhoneVerified bool    `json:"phone_verified" example:"true"`
	WalletBalance int64   `json:"wallet_balance" example:"1000000"`
	OrderCount    int     `json:"order_count"    example:"5"`
	Language      string  `json:"language"       example:"fa"`
	Currency      string  `json:"currency"       example:"IRR"`
	LastLoginAt   *string `json:"last_login_at"  example:"2024-01-01T00:00:00Z"`
	CreatedAt     string  `json:"created_at"     example:"2024-01-01T00:00:00Z"`
	UpdatedAt     string  `json:"updated_at"     example:"2024-01-01T00:00:00Z"`
}
