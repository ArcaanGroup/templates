use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
    #[serde(default)]
    pub phone: String,
    #[serde(default)]
    pub password: String,
    #[serde(default)]
    pub role_ids: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateUserRequest {
    pub name: String,
    pub email: String,
    #[serde(default)]
    pub phone: String,
    #[serde(default)]
    pub avatar: String,
    #[serde(default)]
    pub role_ids: Vec<String>,
}

#[derive(Debug, Deserialize)]
pub struct AssignRolesRequest {
    pub role_ids: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct UserResponse {
    pub id: String,
    pub name: String,
    pub email: String,
    pub phone: String,
    pub avatar: String,
    pub email_verified: bool,
    pub phone_verified: bool,
    pub wallet_balance: i64,
    pub order_count: i32,
    pub language: String,
    pub currency: String,
    pub last_login_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}
