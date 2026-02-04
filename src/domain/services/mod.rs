use crate::domain::entities::User;
use crate::domain::DomainResult;
use async_trait::async_trait;

#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: uuid::Uuid) -> DomainResult<User>;
    async fn find_by_email(&self, email: &str) -> DomainResult<User>;
    async fn save(&self, user: User) -> DomainResult<()>;
    async fn delete(&self, id: uuid::Uuid) -> DomainResult<()>;
}

#[async_trait]
pub trait EventBus: Send + Sync {
    async fn publish<T: Send + Sync>(&self, event: T) -> DomainResult<()>
    where
        T: crate::domain::DomainEvent;
}
