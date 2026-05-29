use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::UserRepository;
use crate::domain;

pub struct ListUsersInput {
    pub page: i32,
    pub page_size: i32,
}

pub struct ListUsersOutput {
    pub users: Vec<domain::User>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
}

#[async_trait]
pub trait ListUsersUseCase: Send + Sync {
    async fn execute(&self, input: ListUsersInput) -> Result<ListUsersOutput, AppError>;
}

pub struct ListUsersUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
}

impl ListUsersUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>) -> Self {
        ListUsersUseCaseImpl { user_repo }
    }
}

#[async_trait]
impl ListUsersUseCase for ListUsersUseCaseImpl {
    async fn execute(&self, input: ListUsersInput) -> Result<ListUsersOutput, AppError> {
        let page = if input.page < 1 { 1 } else { input.page };
        let page_size = if input.page_size < 1 {
            20
        } else if input.page_size > 100 {
            100
        } else {
            input.page_size
        };

        let offset = ((page - 1) * page_size) as usize;
        let (users, total) = self.user_repo.find_all(offset, page_size as usize).await?;

        Ok(ListUsersOutput {
            users,
            total,
            page,
            page_size,
        })
    }
}
