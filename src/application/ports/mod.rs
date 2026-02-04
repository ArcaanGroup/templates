use crate::application::ApplicationResult;
use crate::domain::entities::User;
use async_trait::async_trait;

#[async_trait]
pub trait UserService: Send + Sync {
    async fn create_user(
        &self,
        email: String,
        password: String,
        username: String,
    ) -> ApplicationResult<User>;
    async fn get_user_by_id(&self, id: uuid::Uuid) -> ApplicationResult<User>;
    async fn update_user(&self, user: User) -> ApplicationResult<User>;
    async fn delete_user(&self, id: uuid::Uuid) -> ApplicationResult<()>;
    async fn authenticate_user(&self, email: &str, password: &str) -> ApplicationResult<User>;
}
