use crate::domain;
use crate::interface::dto::RoleResponse;
use crate::interface::dto::UserResponse;

pub fn to_user_response(user: &domain::User) -> UserResponse {
    UserResponse {
        id: user.id.clone(),
        name: user.name.clone(),
        email: user.email.clone(),
        phone: user.phone.clone(),
        avatar: user.avatar.clone(),
        email_verified: user.email_verified,
        phone_verified: user.phone_verified,
        wallet_balance: user.wallet_balance,
        order_count: user.order_count,
        language: user.language.clone(),
        currency: user.currency.clone(),
        last_login_at: user.last_login_at.map(|t| t.format("%+").to_string()),
        created_at: user.created_at.format("%+").to_string(),
        updated_at: user.updated_at.format("%+").to_string(),
    }
}

pub fn to_role_response(role: &domain::Role) -> RoleResponse {
    RoleResponse {
        id: role.id.clone(),
        name: role.name.clone(),
        description: role.description.clone(),
        created_at: role.created_at.format("%+").to_string(),
        updated_at: role.updated_at.format("%+").to_string(),
    }
}
