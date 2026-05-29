mod assign_roles;
mod create;
mod delete;
mod get;
mod get_roles;
mod helpers;
mod list;
mod update;

pub use assign_roles::{AssignRolesInput, AssignRolesUseCase, AssignRolesUseCaseImpl};
#[allow(unused_imports)]
pub use create::{CreateUserInput, CreateUserOutput, CreateUserUseCase, CreateUserUseCaseImpl};
pub use delete::{DeleteUserInput, DeleteUserUseCase, DeleteUserUseCaseImpl};
#[allow(unused_imports)]
pub use get::{GetUserInput, GetUserOutput, GetUserUseCase, GetUserUseCaseImpl};
#[allow(unused_imports)]
pub use get_roles::{GetUserRolesInput, GetUserRolesOutput, GetUserRolesUseCase, GetUserRolesUseCaseImpl};
#[allow(unused_imports)]
pub use list::{ListUsersInput, ListUsersOutput, ListUsersUseCase, ListUsersUseCaseImpl};
#[allow(unused_imports)]
pub use update::{UpdateUserInput, UpdateUserOutput, UpdateUserUseCase, UpdateUserUseCaseImpl};

use async_trait::async_trait;
use crate::domain;

#[async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: &str) -> Result<domain::User, domain::Error>;
    async fn find_all(&self, offset: usize, limit: usize) -> Result<(Vec<domain::User>, i64), domain::Error>;
    async fn find_by_email(&self, email: &str) -> Result<domain::User, domain::Error>;
    async fn create(&self, user: &domain::User) -> Result<(), domain::Error>;
    async fn update(&self, user: &domain::User) -> Result<(), domain::Error>;
    async fn delete(&self, id: &str) -> Result<(), domain::Error>;
}

#[async_trait]
pub trait RoleRepository: Send + Sync {
    async fn find_by_id(&self, id: &str) -> Result<domain::Role, domain::Error>;
    async fn find_all(&self, offset: usize, limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error>;
    async fn find_by_name(&self, name: &str) -> Result<domain::Role, domain::Error>;
    async fn create(&self, role: &domain::Role) -> Result<(), domain::Error>;
    async fn update(&self, role: &domain::Role) -> Result<(), domain::Error>;
    async fn delete(&self, id: &str) -> Result<(), domain::Error>;
}
