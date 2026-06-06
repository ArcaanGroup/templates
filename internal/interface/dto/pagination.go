package dto

// Pagination is an application-layer value object that translates page/size
// into the offset/limit integers expected by repository interfaces.
// Keeping it here (not in domain) ensures the domain layer stays free of
// delivery-mechanism concerns.
type Pagination struct {
	Page     int
	PageSize int
}

func NewPagination(page, pageSize int) Pagination {
	if page < 1 {
		page = 1
	}
	if pageSize < 1 {
		pageSize = 20
	}
	if pageSize > 100 {
		pageSize = 100
	}
	return Pagination{Page: page, PageSize: pageSize}
}

func (p Pagination) Offset() int {
	return (p.Page - 1) * p.PageSize
}

func (p Pagination) Limit() int {
	return p.PageSize
}

// PaginationRequest is the inbound DTO for paginated list endpoints.
type PaginationRequest struct {
	Page     int `json:"page"`
	PageSize int `json:"page_size"`
}

// PaginatedResponse is the generic outbound envelope for paginated lists.
type PaginatedResponse struct {
	Data       any   `json:"data"`
	Total      int64 `json:"total"`
	Page       int   `json:"page"`
	PageSize   int   `json:"page_size"`
	TotalPages int   `json:"total_pages"`
}

func NewPaginatedResponse(data any, total int64, page, pageSize int) *PaginatedResponse {
	totalPages := int(total / int64(pageSize))
	if total%int64(pageSize) > 0 {
		totalPages++
	}
	if totalPages < 1 {
		totalPages = 1
	}
	return &PaginatedResponse{
		Data:       data,
		Total:      total,
		Page:       page,
		PageSize:   pageSize,
		TotalPages: totalPages,
	}
}

type PaginatedRoleResponse struct {
	Data       []RoleResponse `json:"data"`
	Total      int64          `json:"total"`
	Page       int            `json:"page"`
	PageSize   int            `json:"page_size"`
	TotalPages int            `json:"total_pages"`
}

type PaginatedUserResponse struct {
	Data       []UserResponse `json:"data"`
	Total      int64          `json:"total"`
	Page       int            `json:"page"`
	PageSize   int            `json:"page_size"`
	TotalPages int            `json:"total_pages"`
}
