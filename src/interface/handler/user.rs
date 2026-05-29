use std::sync::Arc;

use axum::extract::{Path, Query, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::Json;

use crate::application::usecase::user::{
    AssignRolesUseCase, CreateUserUseCase, DeleteUserUseCase, GetUserRolesUseCase, GetUserUseCase,
    ListUsersUseCase, UpdateUserUseCase,
};
use crate::interface::dto::{
    AssignRolesRequest, CreateUserRequest, PaginatedResponse, PaginationParams, UpdateUserRequest,
    UserResponse,
};
use crate::interface::handler::helpers::to_user_response;

pub struct UserHandler {
    pub create: Box<dyn CreateUserUseCase>,
    pub get_by_id: Box<dyn GetUserUseCase>,
    pub list: Box<dyn ListUsersUseCase>,
    pub update: Box<dyn UpdateUserUseCase>,
    pub delete: Box<dyn DeleteUserUseCase>,
    pub assign_roles: Box<dyn AssignRolesUseCase>,
    pub get_user_roles: Box<dyn GetUserRolesUseCase>,
}

impl UserHandler {
    pub fn new(
        create: Box<dyn CreateUserUseCase>,
        get_by_id: Box<dyn GetUserUseCase>,
        list: Box<dyn ListUsersUseCase>,
        update: Box<dyn UpdateUserUseCase>,
        delete: Box<dyn DeleteUserUseCase>,
        assign_roles: Box<dyn AssignRolesUseCase>,
        get_user_roles: Box<dyn GetUserRolesUseCase>,
    ) -> Self {
        UserHandler {
            create,
            get_by_id,
            list,
            update,
            delete,
            assign_roles,
            get_user_roles,
        }
    }

    pub async fn list_all(
        State(handler): State<Arc<Self>>,
        Query(params): Query<PaginationParams>,
    ) -> impl IntoResponse {
        let page = params.page.unwrap_or(1);
        let page_size = params.page_size.unwrap_or(20);
        let input = crate::application::usecase::user::ListUsersInput { page, page_size };
        match handler.list.execute(input).await {
            Ok(output) => {
                let dtos: Vec<UserResponse> =
                    output.users.iter().map(to_user_response).collect();
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
        let input = crate::application::usecase::user::GetUserInput { id };
        match handler.get_by_id.execute(input).await {
            Ok(output) => Ok(Json(to_user_response(&output.user))),
            Err(e) => Err(e),
        }
    }

    pub async fn create(
        State(handler): State<Arc<Self>>,
        Json(req): Json<CreateUserRequest>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::user::CreateUserInput {
            name: req.name,
            email: req.email,
            phone: req.phone,
            password: req.password,
            role_ids: req.role_ids,
        };
        match handler.create.execute(input).await {
            Ok(output) => Ok((StatusCode::CREATED, Json(to_user_response(&output.user)))),
            Err(e) => Err(e),
        }
    }

    pub async fn update(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
        Json(req): Json<UpdateUserRequest>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::user::UpdateUserInput {
            name: req.name,
            email: req.email,
            phone: req.phone,
            avatar: req.avatar,
            role_ids: req.role_ids,
        };
        match handler.update.execute(&id, input).await {
            Ok(output) => Ok(Json(to_user_response(&output.user))),
            Err(e) => Err(e),
        }
    }

    pub async fn delete(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::user::DeleteUserInput { id };
        match handler.delete.execute(input).await {
            Ok(_) => Ok(StatusCode::NO_CONTENT),
            Err(e) => Err(e),
        }
    }

    pub async fn assign_roles(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
        Json(req): Json<AssignRolesRequest>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::user::AssignRolesInput {
            role_ids: req.role_ids,
        };
        match handler.assign_roles.execute(&id, input).await {
            Ok(_) => Ok(Json(serde_json::json!({"status": "ok"}))),
            Err(e) => Err(e),
        }
    }

    pub async fn get_roles(
        State(handler): State<Arc<Self>>,
        Path(id): Path<String>,
    ) -> impl IntoResponse {
        let input = crate::application::usecase::user::GetUserRolesInput { id };
        match handler.get_user_roles.execute(input).await {
            Ok(output) => {
                let dtos: Vec<crate::interface::dto::RoleResponse> =
                    output.roles.iter().map(to_role_response).collect();
                Ok(Json(dtos))
            }
            Err(e) => Err(e),
        }
    }
}

fn to_role_response(role: &crate::domain::Role) -> crate::interface::dto::RoleResponse {
    crate::interface::handler::helpers::to_role_response(role)
}
