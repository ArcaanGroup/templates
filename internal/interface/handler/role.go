package handler

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"

	roleusecase "go-clean-template/internal/application/usecase/role"
	"go-clean-template/internal/interface/dto"
)

type RoleHandler struct {
	create  roleusecase.CreateRoleUseCase
	getByID roleusecase.GetRoleUseCase
	getAll  roleusecase.ListRolesUseCase
	update  roleusecase.UpdateRoleUseCase
	delete  roleusecase.DeleteRoleUseCase
}

func NewRoleHandler(
	createUC roleusecase.CreateRoleUseCase,
	getByIDUC roleusecase.GetRoleUseCase,
	getAllUC roleusecase.ListRolesUseCase,
	updateUC roleusecase.UpdateRoleUseCase,
	deleteUC roleusecase.DeleteRoleUseCase,
) *RoleHandler {
	return &RoleHandler{
		create:  createUC,
		getByID: getByIDUC,
		getAll:  getAllUC,
		update:  updateUC,
		delete:  deleteUC,
	}
}

// GetByID returns a single role by ID.
// @Summary     Get role by ID
// @Description Get a role by their unique identifier
// @Tags        roles
// @Accept      json
// @Produce     json
// @Param       id   path     string  true  "Role ID"
// @Success     200  {object} dto.RoleResponse
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /roles/{id} [get]
func (h *RoleHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	result, err := h.getByID.Execute(r.Context(), &roleusecase.GetRoleInput{ID: id})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, toRoleResponse(result.Role))
}

// GetAll returns all roles.
// @Summary     List roles
// @Description Get a paginated list of all roles
// @Tags        roles
// @Accept      json
// @Produce     json
// @Param       page      query  int  false  "Page number"    default(1)
// @Param       page_size query  int  false  "Items per page" default(20)
// @Success     200  {object} dto.PaginatedRoleResponse
// @Failure     500  {object} map[string]string
// @Router      /roles [get]
func (h *RoleHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	p := parsePagination(r)
	result, err := h.getAll.Execute(r.Context(), &roleusecase.ListRolesInput{Page: p.Page, PageSize: p.PageSize})
	if err != nil {
		writeError(w, err)
		return
	}
	dtos := make([]*dto.RoleResponse, len(result.Roles))
	for i, ro := range result.Roles {
		dtos[i] = toRoleResponse(ro)
	}
	writeJSON(w, http.StatusOK, dto.NewPaginatedResponse(dtos, result.Total, result.Page, result.PageSize))
}

// Create creates a new role.
// @Summary     Create role
// @Description Create a new role with the given payload
// @Tags        roles
// @Accept      json
// @Produce     json
// @Param       body  body      dto.CreateRoleRequest  true  "Role payload"
// @Success     201   {object}  dto.RoleResponse
// @Failure     400   {object}  map[string]string
// @Failure     409   {object}  map[string]string
// @Failure     500   {object}  map[string]string
// @Router      /roles [post]
func (h *RoleHandler) Create(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var reqDTO dto.CreateRoleRequest
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.create.Execute(r.Context(), &roleusecase.CreateRoleInput{
		Name:        reqDTO.Name,
		Description: reqDTO.Description,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, toRoleResponse(result.Role))
}

// Update updates an existing role by ID.
// @Summary     Update role
// @Description Update an existing role by their unique identifier
// @Tags        roles
// @Accept      json
// @Produce     json
// @Param       id    path    string                    true  "Role ID"
// @Param       body  body    dto.UpdateRoleRequest     true  "Updated role payload"
// @Success     200   {object}  dto.RoleResponse
// @Failure     400   {object}  map[string]string
// @Failure     404   {object}  map[string]string
// @Failure     409   {object}  map[string]string
// @Failure     500   {object}  map[string]string
// @Router      /roles/{id} [put]
func (h *RoleHandler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	defer r.Body.Close()
	var reqDTO dto.UpdateRoleRequest
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.update.Execute(r.Context(), id, &roleusecase.UpdateRoleInput{
		Name:        reqDTO.Name,
		Description: reqDTO.Description,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, toRoleResponse(result.Role))
}

// Delete deletes a role by ID.
// @Summary     Delete role
// @Description Delete a role by their unique identifier
// @Tags        roles
// @Accept      json
// @Produce     json
// @Param       id   path     string  true  "Role ID"
// @Success     204  "No Content"
// @Failure     404  {object} map[string]string
// @Failure     500  {object} map[string]string
// @Router      /roles/{id} [delete]
func (h *RoleHandler) Delete(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.delete.Execute(r.Context(), &roleusecase.DeleteRoleInput{ID: id}); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
