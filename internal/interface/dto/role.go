package dto

type CreateRoleRequest struct {
	Name        string `json:"name"        example:"admin"`
	Description string `json:"description" example:"Administrator role with full access"`
}

type UpdateRoleRequest struct {
	Name        string `json:"name"        example:"admin"`
	Description string `json:"description" example:"Administrator role with full access"`
}

type RoleResponse struct {
	ID          string `json:"id"          example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
	Name        string `json:"name"        example:"admin"`
	Description string `json:"description" example:"Administrator role with full access"`
	CreatedAt   string `json:"created_at"  example:"2024-01-01T00:00:00Z"`
	UpdatedAt   string `json:"updated_at"  example:"2024-01-01T00:00:00Z"`
}
