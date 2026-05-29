use std::sync::Arc;

use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use async_trait::async_trait;

use go_clean_template::application::usecase::role::*;
use go_clean_template::application::error::AppError;
use go_clean_template::domain;
use go_clean_template::interface::dto::CreateRoleRequest;
use go_clean_template::interface::handler::role::RoleHandler;

struct MockCreateRoleUC;
#[async_trait]
impl CreateRoleUseCase for MockCreateRoleUC {
    async fn execute(&self, input: CreateRoleInput) -> Result<CreateRoleOutput, AppError> {
        let role = domain::Role::new(input.name, input.description)?;
        Ok(CreateRoleOutput { role })
    }
}

struct MockGetRoleUC;
#[async_trait]
impl GetRoleUseCase for MockGetRoleUC {
    async fn execute(&self, input: GetRoleInput) -> Result<GetRoleOutput, AppError> {
        if input.id == "999" {
            return Err(AppError::NotFound);
        }
        let role = domain::Role::new("admin".into(), "Admin".into()).unwrap();
        Ok(GetRoleOutput { role })
    }
}

struct MockListRolesUC;
#[async_trait]
impl ListRolesUseCase for MockListRolesUC {
    async fn execute(&self, _input: ListRolesInput) -> Result<ListRolesOutput, AppError> {
        Ok(ListRolesOutput { roles: vec![], total: 0, page: 1, page_size: 20, total_pages: 1 })
    }
}

struct MockUpdateRoleUC;
#[async_trait]
impl UpdateRoleUseCase for MockUpdateRoleUC {
    async fn execute(&self, _id: &str, _input: UpdateRoleInput) -> Result<UpdateRoleOutput, AppError> {
        let role = domain::Role::new("admin".into(), "Admin".into()).unwrap();
        Ok(UpdateRoleOutput { role })
    }
}

struct MockDeleteRoleUC;
#[async_trait]
impl DeleteRoleUseCase for MockDeleteRoleUC {
    async fn execute(&self, _input: DeleteRoleInput) -> Result<(), AppError> { Ok(()) }
}

fn test_role_handler() -> RoleHandler {
    RoleHandler::new(
        Box::new(MockCreateRoleUC),
        Box::new(MockGetRoleUC),
        Box::new(MockListRolesUC),
        Box::new(MockUpdateRoleUC),
        Box::new(MockDeleteRoleUC),
    )
}

#[tokio::test]
async fn test_role_get_by_id_success() {
    let handler = Arc::new(test_role_handler());
    let response = RoleHandler::get_by_id(
        State(handler),
        Path("1".into()),
    ).await.into_response();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_role_get_by_id_not_found() {
    let handler = Arc::new(test_role_handler());
    let response = RoleHandler::get_by_id(
        State(handler),
        Path("999".into()),
    ).await.into_response();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn test_role_create_success() {
    let handler = Arc::new(test_role_handler());
    let response = RoleHandler::create(
        State(handler),
        axum::Json(CreateRoleRequest { name: "admin".into(), description: "Admin role".into() }),
    ).await.into_response();
    assert_eq!(response.status(), StatusCode::CREATED);
}

#[tokio::test]
async fn test_role_delete_success() {
    let handler = Arc::new(test_role_handler());
    let response = RoleHandler::delete(
        State(handler),
        Path("1".into()),
    ).await.into_response();
    assert_eq!(response.status(), StatusCode::NO_CONTENT);
}
