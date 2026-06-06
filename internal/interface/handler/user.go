package handler

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"

	userusecase "go-clean-template/internal/application/usecase/user"
	"go-clean-template/internal/interface/dto"
)

type UserHandler struct {
	create       userusecase.CreateUserUseCase
	getByID      userusecase.GetUserUseCase
	getAll       userusecase.ListUsersUseCase
	update       userusecase.UpdateUserUseCase
	delete       userusecase.DeleteUserUseCase
	assignRoles  userusecase.AssignRolesUseCase
	getUserRoles userusecase.GetUserRolesUseCase
}

func NewUserHandler(
	createUC userusecase.CreateUserUseCase,
	getByIDUC userusecase.GetUserUseCase,
	getAllUC userusecase.ListUsersUseCase,
	updateUC userusecase.UpdateUserUseCase,
	deleteUC userusecase.DeleteUserUseCase,
	assignRolesUC userusecase.AssignRolesUseCase,
	getUserRolesUC userusecase.GetUserRolesUseCase,
) *UserHandler {
	return &UserHandler{
		create:       createUC,
		getByID:      getByIDUC,
		getAll:       getAllUC,
		update:       updateUC,
		delete:       deleteUC,
		assignRoles:  assignRolesUC,
		getUserRoles: getUserRolesUC,
	}
}

// GetByID returns a single user by ID.
// @Summary     Get user by ID
// @Description Get a user by their unique identifier
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       id   path     string  true  "User ID"
// @Success     200  {object} dto.UserResponse
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /users/{id} [get]
func (h *UserHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	result, err := h.getByID.Execute(r.Context(), &userusecase.GetUserInput{ID: id})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, toUserResponse(result.User))
}

// GetAll returns all users.
// @Summary     List users
// @Description Get a paginated list of all users
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       page      query  int  false  "Page number"    default(1)
// @Param       page_size query  int  false  "Items per page" default(20)
// @Success     200  {object} dto.PaginatedUserResponse
// @Failure     500  {object} map[string]string
// @Router      /users [get]
func (h *UserHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	p := parsePagination(r)
	result, err := h.getAll.Execute(r.Context(), &userusecase.ListUsersInput{Page: p.Page, PageSize: p.PageSize})
	if err != nil {
		writeError(w, err)
		return
	}
	dtos := make([]*dto.UserResponse, len(result.Users))
	for i, u := range result.Users {
		dtos[i] = toUserResponse(u)
	}
	writeJSON(w, http.StatusOK, dto.NewPaginatedResponse(dtos, result.Total, result.Page, result.PageSize))
}

// Create creates a new user.
// @Summary     Create user
// @Description Create a new user with the given payload
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       body  body      dto.CreateUserRequest  true  "User payload"
// @Success     201   {object}  dto.UserResponse
// @Failure     400   {object}  map[string]string
// @Failure     409   {object}  map[string]string
// @Failure     500   {object}  map[string]string
// @Router      /users [post]
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var reqDTO dto.CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.create.Execute(r.Context(), &userusecase.CreateUserInput{
		Name:     reqDTO.Name,
		Email:    reqDTO.Email,
		Phone:    reqDTO.Phone,
		Password: reqDTO.Password,
		RoleIDs:  reqDTO.RoleIDs,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, toUserResponse(result.User))
}

// Update updates an existing user by ID.
// @Summary     Update user
// @Description Update an existing user by their unique identifier
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       id    path    string                    true  "User ID"
// @Param       body  body    dto.UpdateUserRequest     true  "Updated user payload"
// @Success     200   {object}  dto.UserResponse
// @Failure     400   {object}  map[string]string
// @Failure     404   {object}  map[string]string
// @Failure     409   {object}  map[string]string
// @Failure     500   {object}  map[string]string
// @Router      /users/{id} [put]
func (h *UserHandler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	defer r.Body.Close()
	var reqDTO dto.UpdateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.update.Execute(r.Context(), id, &userusecase.UpdateUserInput{
		Name:    reqDTO.Name,
		Email:   reqDTO.Email,
		Phone:   reqDTO.Phone,
		Avatar:  reqDTO.Avatar,
		RoleIDs: reqDTO.RoleIDs,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, toUserResponse(result.User))
}

// Delete deletes a user by ID.
// @Summary     Delete user
// @Description Delete a user by their unique identifier
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       id   path     string  true  "User ID"
// @Success     204  "No Content"
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /users/{id} [delete]
func (h *UserHandler) Delete(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.delete.Execute(r.Context(), &userusecase.DeleteUserInput{ID: id}); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}

// AssignRoles assigns roles to a user.
// @Summary     Assign roles to user
// @Description Assign roles to a user by their unique identifier
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       id    path  string                    true  "User ID"
// @Param       body  body  dto.AssignRolesRequest    true  "Role IDs payload"
// @Success     200  "OK"
// @Failure     400  {object} map[string]string
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /users/{id}/roles [post]
func (h *UserHandler) AssignRoles(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	defer r.Body.Close()
	var reqDTO dto.AssignRolesRequest
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	if err := h.assignRoles.Execute(r.Context(), id, &userusecase.AssignRolesInput{RoleIDs: reqDTO.RoleIDs}); err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

// GetUserRoles returns all roles assigned to a user.
// @Summary     Get user roles
// @Description Get all roles assigned to a user
// @Tags        users
// @Accept      json
// @Produce     json
// @Param       id   path     string  true  "User ID"
// @Success     200  {array}  dto.RoleResponse
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /users/{id}/roles [get]
func (h *UserHandler) GetUserRoles(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	result, err := h.getUserRoles.Execute(r.Context(), &userusecase.GetUserRolesInput{ID: id})
	if err != nil {
		writeError(w, err)
		return
	}
	dtos := make([]*dto.RoleResponse, len(result.Roles))
	for i, ro := range result.Roles {
		dtos[i] = toRoleResponse(ro)
	}
	writeJSON(w, http.StatusOK, dtos)
}
