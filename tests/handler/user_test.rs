use std::sync::Arc;

use async_trait::async_trait;
use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;

use rust_clean_template::application::usecase::user::*;
use rust_clean_template::domain;
use rust_clean_template::interface::dto::CreateUserRequest;
use rust_clean_template::interface::handler::user::UserHandler;

struct MockCreateUserUC;
#[async_trait]
impl CreateUserUseCase for MockCreateUserUC {
    async fn execute(
        &self,
        input: CreateUserInput,
    ) -> Result<CreateUserOutput, rust_clean_template::application::error::AppError> {
        let user = domain::User::new(input.name, input.email, input.phone, input.role_ids).unwrap();
        Ok(CreateUserOutput { user })
    }
}

struct MockGetUserUC;
#[async_trait]
impl GetUserUseCase for MockGetUserUC {
    async fn execute(
        &self,
        input: GetUserInput,
    ) -> Result<GetUserOutput, rust_clean_template::application::error::AppError> {
        if input.id == "999" {
            return Err(rust_clean_template::application::error::AppError::NotFound);
        }
        let user = domain::User::new(
            "Alice".into(),
            "alice@example.com".into(),
            "123".into(),
            vec![],
        )
        .unwrap();
        Ok(GetUserOutput { user })
    }
}

struct MockListUsersUC;
#[async_trait]
impl ListUsersUseCase for MockListUsersUC {
    async fn execute(
        &self,
        _input: ListUsersInput,
    ) -> Result<ListUsersOutput, rust_clean_template::application::error::AppError> {
        Ok(ListUsersOutput {
            users: vec![],
            total: 0,
            page: 1,
            page_size: 20,
        })
    }
}

struct MockUpdateUserUC;
#[async_trait]
impl UpdateUserUseCase for MockUpdateUserUC {
    async fn execute(
        &self,
        _id: &str,
        _input: UpdateUserInput,
    ) -> Result<UpdateUserOutput, rust_clean_template::application::error::AppError> {
        let user = domain::User::new("A".into(), "a@b.com".into(), "0".into(), vec![]).unwrap();
        Ok(UpdateUserOutput { user })
    }
}

struct MockDeleteUserUC;
#[async_trait]
impl DeleteUserUseCase for MockDeleteUserUC {
    async fn execute(
        &self,
        _input: DeleteUserInput,
    ) -> Result<(), rust_clean_template::application::error::AppError> {
        Ok(())
    }
}

struct MockAssignRolesUC;
#[async_trait]
impl AssignRolesUseCase for MockAssignRolesUC {
    async fn execute(
        &self,
        _id: &str,
        _input: AssignRolesInput,
    ) -> Result<(), rust_clean_template::application::error::AppError> {
        Ok(())
    }
}

struct MockGetUserRolesUC;
#[async_trait]
impl GetUserRolesUseCase for MockGetUserRolesUC {
    async fn execute(
        &self,
        _input: GetUserRolesInput,
    ) -> Result<GetUserRolesOutput, rust_clean_template::application::error::AppError> {
        Ok(GetUserRolesOutput { roles: vec![] })
    }
}

fn test_user_handler() -> UserHandler {
    UserHandler::new(
        Box::new(MockCreateUserUC),
        Box::new(MockGetUserUC),
        Box::new(MockListUsersUC),
        Box::new(MockUpdateUserUC),
        Box::new(MockDeleteUserUC),
        Box::new(MockAssignRolesUC),
        Box::new(MockGetUserRolesUC),
    )
}

#[tokio::test]
async fn test_user_get_by_id_success() {
    let handler = Arc::new(test_user_handler());
    let response = UserHandler::get_by_id(State(handler), Path("123".into()))
        .await
        .into_response();
    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_user_get_by_id_not_found() {
    let handler = Arc::new(test_user_handler());
    let response = UserHandler::get_by_id(State(handler), Path("999".into()))
        .await
        .into_response();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn test_user_create_success() {
    let handler = Arc::new(test_user_handler());
    let req = CreateUserRequest {
        name: "Alice".into(),
        email: "alice@example.com".into(),
        phone: "123".into(),
        password: "secret".into(),
        role_ids: vec![],
    };
    let response = UserHandler::create(State(handler), axum::Json(req))
        .await
        .into_response();
    assert_eq!(response.status(), StatusCode::CREATED);
}

#[tokio::test]
async fn test_user_delete_success() {
    let handler = Arc::new(test_user_handler());
    let response = UserHandler::delete(State(handler), Path("1".into()))
        .await
        .into_response();
    assert_eq!(response.status(), StatusCode::NO_CONTENT);
}
