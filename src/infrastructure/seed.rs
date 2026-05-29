use std::sync::Arc;

use tracing::info;

use crate::application::usecase::user::{RoleRepository, UserRepository};
use crate::domain;

pub async fn run(
    role_repo: Arc<dyn RoleRepository>,
    user_repo: Arc<dyn UserRepository>,
) {
    seed_roles(&*role_repo).await;
    seed_users(&*user_repo, &*role_repo).await;
}

async fn seed_roles(role_repo: &dyn RoleRepository) {
    let (existing, _) = role_repo.find_all(0, 1).await.unwrap_or_default();
    if !existing.is_empty() {
        info!("roles already seeded, skipping");
        return;
    }

    let roles = vec![
        ("admin", "Full system access"),
        ("user", "Standard user access"),
    ];

    for (name, desc) in roles {
        match domain::Role::new(name.to_string(), desc.to_string()) {
            Ok(role) => {
                if let Err(e) = role_repo.create(&role).await {
                    tracing::error!("failed to seed role {}: {:?}", name, e);
                } else {
                    info!("seeded role {}", name);
                }
            }
            Err(e) => tracing::error!("invalid role {}: {:?}", name, e),
        }
    }
}

async fn seed_users(user_repo: &dyn UserRepository, role_repo: &dyn RoleRepository) {
    let (existing, _) = user_repo.find_all(0, 1).await.unwrap_or_default();
    if !existing.is_empty() {
        info!("users already seeded, skipping");
        return;
    }

    let (roles, _) = role_repo.find_all(0, 100).await.unwrap_or_default();
    let role_map: std::collections::HashMap<&str, &str> = roles
        .iter()
        .map(|r| (r.name.as_str(), r.id.as_str()))
        .collect();

    let users = vec![
        ("Admin User", "admin@example.com", "09000000001", "admin"),
        ("Regular User", "user@example.com", "09000000002", "user"),
    ];

    for (name, email, phone, role_name) in users {
        let role_ids = role_map
            .get(role_name)
            .map(|id| vec![id.to_string()])
            .unwrap_or_default();

        match domain::User::new(name.to_string(), email.to_string(), phone.to_string(), role_ids)
        {
            Ok(mut user) => {
                let _ = user.set_password("default123");
                if let Err(e) = user_repo.create(&user).await {
                    tracing::error!("failed to seed user {}: {:?}", email, e);
                } else {
                    info!("seeded user {}", email);
                }
            }
            Err(e) => tracing::error!("invalid user {}: {:?}", email, e),
        }
    }
}
