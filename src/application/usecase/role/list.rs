use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;
use crate::domain;

pub struct ListRolesInput {
    pub page: i32,
    pub page_size: i32,
}

pub struct ListRolesOutput {
    pub roles: Vec<domain::Role>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
}

#[async_trait]
pub trait ListRolesUseCase: Send + Sync {
    async fn execute(&self, input: ListRolesInput) -> Result<ListRolesOutput, AppError>;
}

pub struct ListRolesUseCaseImpl {
    role_repo: Arc<dyn RoleRepository>,
}

impl ListRolesUseCaseImpl {
    pub fn new(role_repo: Arc<dyn RoleRepository>) -> Self {
        ListRolesUseCaseImpl { role_repo }
    }
}

#[async_trait]
impl ListRolesUseCase for ListRolesUseCaseImpl {
    async fn execute(&self, input: ListRolesInput) -> Result<ListRolesOutput, AppError> {
        let page = if input.page < 1 { 1 } else { input.page };
        let page_size = if input.page_size < 1 {
            20
        } else if input.page_size > 100 {
            100
        } else {
            input.page_size
        };

        let offset = ((page - 1) * page_size) as usize;
        let (roles, total) = self.role_repo.find_all(offset, page_size as usize).await?;

        Ok(ListRolesOutput {
            roles,
            total,
            page,
            page_size,
        })
    }
}
