use crate::{
    application::usecases::CreateUserUsecase,
    infrastructure::{config::AppConfig, repositories::InMemoryUserRepository},
};
use std::sync::Arc;
use tokio;
use tracing_subscriber;

use axum::serve;

mod application;
mod domain;
mod infrastructure;
mod presentation;
mod shared_kernel;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing with environment-based configuration
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO) // Default to INFO level
        .with_target(false) // Simplify output by removing module targets
        .init();

    // Load configuration
    let config = AppConfig::from_env()?;

    // Initialize repositories
    let user_repository = InMemoryUserRepository::new();

    // Initialize use cases
    let create_user_usecase = CreateUserUsecase::new(user_repository);

    // Create shared state
    let app_state = Arc::new(create_user_usecase);

    // Create the Axum router
    let app = crate::presentation::create_app(app_state);

    // Run the server
    let addr = std::net::SocketAddr::from(([0, 0, 0, 0], config.server.port));
    tracing::info!("Server running on {}", addr);

    serve(
        tokio::net::TcpListener::bind(addr)
            .await
            .map_err(|e| Box::new(e) as Box<dyn std::error::Error>)?,
        app.into_make_service(),
    )
    .await
    .map_err(|err| err.into())
}
