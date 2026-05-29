use std::sync::Arc;

use async_trait::async_trait;

use crate::application::error::AppError;
use crate::application::usecase::user::UserRepository;

pub struct DeleteUserInput {
    pub id: String,
}

#[async_trait]
pub trait DeleteUserUseCase: Send + Sync {
    async fn execute(&self, input: DeleteUserInput) -> Result<(), AppError>;
}

pub struct DeleteUserUseCaseImpl {
    user_repo: Arc<dyn UserRepository>,
}

impl DeleteUserUseCaseImpl {
    pub fn new(user_repo: Arc<dyn UserRepository>) -> Self {
        DeleteUserUseCaseImpl { user_repo }
    }
}

#[async_trait]
impl DeleteUserUseCase for DeleteUserUseCaseImpl {
    async fn execute(&self, input: DeleteUserInput) -> Result<(), AppError> {
        self.user_repo.find_by_id(&input.id).await?;
        self.user_repo.delete(&input.id).await?;
        Ok(())
    }
}
