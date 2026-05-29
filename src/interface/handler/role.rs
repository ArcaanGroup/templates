use std::sync::Arc;

use axum::extract::{Path, Query, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::Json;

use crate::application::usecase::role::{
    CreateRoleUseCase, DeleteRoleUseCase, GetRoleUseCase, ListRolesUseCase, UpdateRoleUseCase,
};
use crate::interface::dto::{
    CreateRoleRequest, PaginatedResponse, PaginationParams, RoleResponse, UpdateRoleRequest,
};
use crate::interface::handler::helpers::to_role_response;

pub struct RoleHandler {
    pub create: Box<dyn CreateRoleUseCase>,
    pub get_by_id: Box<dyn GetRoleUseCase>,
    pub list: Box<dyn ListRolesUseCase>,
    pub update: Box<dyn UpdateRoleUseCase>,
    pub delete: Box<dyn DeleteRoleUseCase>,
}

impl RoleHandler {
    pub fn new(
        create: Box<dyn CreateRoleUseCase>,
        get_by_id: Box<dyn GetRoleUseCase>,
        list: Box<dyn ListRolesUseCase>,
        update: Box<dyn UpdateRoleUseCase>,
        delete: Box<dyn DeleteRoleUseCase>,
    ) -> Self {
        RoleHandler {
            create,
            get_by_id,
            list,
            update,
            delete,
        }
    }

    pub async fn list_all(
        State(handler): State<Arc<Self>>,
        Query(params): Query<PaginationParams>,
    ) -> impl IntoResponse {
        let page = params.page.unwrap_or(1);
        let page_size = params.page_size.unwrap_or(20);
        let input = crate::application::usecase::role::ListRolesInput { page, page_size };
        match handler.list.execute(input).await {
            Ok(output) => {
                let dtos: Vec<RoleResponse> =
                    output.roles.iter().map(to_role_response).collect();
                let resp = PaginatedResponse::new(dtos, output.total, output.page, output.page_size);
                Ok(Json(resp))
            }
            Err(e) => Err(e),
        }
    }

    pub async fn get_by_id(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::role::GetRoleInput { id };
        match handler.get_by_id.execute(input).await {
            Ok(output) => Ok(Json(to_role_response(&output.role))),
            Err(e) => Err(e),
        }
    }

    pub async fn create(
        State(handler): State<Arc<Self>>,
        Json(req): Json<CreateRoleRequest>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::role::CreateRoleInput {
            name: req.name,
            description: req.description,
        };
        match handler.create.execute(input).await {
            Ok(output) => Ok((StatusCode::CREATED, Json(to_role_response(&output.role)))),
            Err(e) => Err(e),
        }
    }

    pub async fn update(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
        Json(req): Json<UpdateRoleRequest>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::role::UpdateRoleInput {
            name: req.name,
            description: req.description,
        };
        match handler.update.execute(&id, input).await {
            Ok(output) => Ok(Json(to_role_response(&output.role))),
            Err(e) => Err(e),
        }
    }

    pub async fn delete(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::role::DeleteRoleInput { id };
        match handler.delete.execute(input).await {
            Ok(_) => Ok(StatusCode::NO_CONTENT),
            Err(e) => Err(e),
        }
    }
}
