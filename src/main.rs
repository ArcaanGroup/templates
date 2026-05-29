mod application;
mod domain;
mod infrastructure;
mod interface;

use std::sync::Arc;

use tokio::net::TcpListener;
use tokio::signal;
use tracing::info;

use application::usecase::role::{
    CreateRoleUseCaseImpl, DeleteRoleUseCaseImpl, GetRoleUseCaseImpl, ListRolesUseCaseImpl,
    UpdateRoleUseCaseImpl,
};
use application::usecase::user::{
    AssignRolesUseCaseImpl, CreateUserUseCaseImpl, DeleteUserUseCaseImpl, GetUserRolesUseCaseImpl,
    GetUserUseCaseImpl, ListUsersUseCaseImpl, UpdateUserUseCaseImpl,
};
use application::usecase::user::{RoleRepository, UserRepository};
use infrastructure::config::Config;
use infrastructure::persistence::{InMemoryRoleRepository, InMemoryUserRepository};
use interface::handler::role::RoleHandler;
use interface::handler::user::UserHandler;

#[tokio::main]
async fn main() {
    let cfg = Config::load().expect("failed to load config");

    infrastructure::logger::init(&cfg.log_level);
    info!("starting server");

    // --- Repositories ---
    let user_repo: Arc<dyn UserRepository> = Arc::new(InMemoryUserRepository::new());
    let role_repo: Arc<dyn RoleRepository> = Arc::new(InMemoryRoleRepository::new());

    // --- User Use Cases ---
    let create_user_uc = Box::new(CreateUserUseCaseImpl::new(
        user_repo.clone(),
        role_repo.clone(),
    ));
    let get_user_uc = Box::new(GetUserUseCaseImpl::new(user_repo.clone()));
    let list_users_uc = Box::new(ListUsersUseCaseImpl::new(user_repo.clone()));
    let update_user_uc = Box::new(UpdateUserUseCaseImpl::new(
        user_repo.clone(),
        role_repo.clone(),
    ));
    let delete_user_uc = Box::new(DeleteUserUseCaseImpl::new(user_repo.clone()));
    let assign_roles_uc = Box::new(AssignRolesUseCaseImpl::new(
        user_repo.clone(),
        role_repo.clone(),
    ));
    let get_user_roles_uc = Box::new(GetUserRolesUseCaseImpl::new(
        user_repo.clone(),
        role_repo.clone(),
    ));

    // --- Role Use Cases ---
    let create_role_uc = Box::new(CreateRoleUseCaseImpl::new(role_repo.clone()));
    let get_role_uc = Box::new(GetRoleUseCaseImpl::new(role_repo.clone()));
    let list_roles_uc = Box::new(ListRolesUseCaseImpl::new(role_repo.clone()));
    let update_role_uc = Box::new(UpdateRoleUseCaseImpl::new(role_repo.clone()));
    let delete_role_uc = Box::new(DeleteRoleUseCaseImpl::new(role_repo.clone()));

    // --- Handlers ---
    let user_handler = UserHandler::new(
        create_user_uc,
        get_user_uc,
        list_users_uc,
        update_user_uc,
        delete_user_uc,
        assign_roles_uc,
        get_user_roles_uc,
    );
    let role_handler = RoleHandler::new(
        create_role_uc,
        get_role_uc,
        list_roles_uc,
        update_role_uc,
        delete_role_uc,
    );

    // --- Seed ---
    infrastructure::seed::run(role_repo, user_repo).await;

    // --- Router ---
    let app = interface::router::new(user_handler, role_handler);

    // --- Server ---
    let addr = format!("0.0.0.0:{}", cfg.port);
    let listener = TcpListener::bind(&addr).await.unwrap_or_else(|e| {
        panic!("failed to bind to {}: {}", addr, e);
    });

    info!("server listening on {}", addr);

    axum::serve(listener, app.into_make_service())
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("server error");

    info!("server stopped");
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    info!("shutting down gracefully...");
}
