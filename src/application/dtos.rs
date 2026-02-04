use crate::domain::entities::User;
use crate::domain::value_objects::Email;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub password: String,
    pub username: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateUserRequest {
    pub user_id: Uuid,
    pub email: Option<String>,
    pub username: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GetUserResponse {
    pub id: Uuid,
    pub email: String,
    pub username: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
    pub is_active: bool,
}

impl From<User> for GetUserResponse {
    fn from(user: User) -> Self {
        GetUserResponse {
            id: user.id,
            email: user.email.as_str().to_string(),
            username: user.username,
            created_at: user.created_at,
            updated_at: user.updated_at,
            is_active: user.is_active,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginResponse {
    pub token: String,
    pub user_id: Uuid,
}
