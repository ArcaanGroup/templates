use crate::application::{
    dtos::{CreateUserRequest, GetUserResponse},
    ports::UserService,
    ApplicationResult,
};
use crate::domain::entities::User;
use crate::domain::services::UserRepository;
use crate::domain::value_objects::{Email, Password};
use async_trait::async_trait;
use tracing;

pub struct CreateUserUsecase<R: UserRepository> {
    user_repository: R,
}

impl<R: UserRepository> CreateUserUsecase<R> {
    pub fn new(user_repository: R) -> Self {
        Self { user_repository }
    }

    pub async fn execute(&self, req: CreateUserRequest) -> ApplicationResult<GetUserResponse> {
        tracing::info!("Creating new user with email: {}", req.email);

        // Store email for logging purposes before moving it
        let email_str = req.email.clone();

        // Validate input
        let email = Email::new(req.email)?;
        let password = Password::new(req.password)?;

        // Check if user already exists
        if let Ok(_) = self.user_repository.find_by_email(email.as_str()).await {
            tracing::warn!("Attempt to create user with existing email: {}", email_str);
            return Err(crate::domain::DomainError::BusinessRuleViolation {
                message: "User with this email already exists".to_string(),
            }
            .into());
        }

        // Create user
        let mut user = User::new(email, password, req.username)?;

        // Save user
        self.user_repository.save(user.clone()).await?;
        tracing::info!("Successfully created user with ID: {}", user.id);

        // Convert to response
        Ok(GetUserResponse::from(user))
    }
}

pub struct GetUserByIdUsecase<R: UserRepository> {
    user_repository: R,
}

impl<R: UserRepository> GetUserByIdUsecase<R> {
    pub fn new(user_repository: R) -> Self {
        Self { user_repository }
    }

    pub async fn execute(&self, user_id: uuid::Uuid) -> ApplicationResult<GetUserResponse> {
        tracing::debug!("Fetching user by ID: {}", user_id);
        let user = self.user_repository.find_by_id(user_id).await?;
        tracing::debug!("Successfully fetched user: {}", user.email.as_str());
        Ok(GetUserResponse::from(user))
    }
}

pub struct UpdateUserUsecase<R: UserRepository> {
    user_repository: R,
}

impl<R: UserRepository> UpdateUserUsecase<R> {
    pub fn new(user_repository: R) -> Self {
        Self { user_repository }
    }

    pub async fn execute(&self, mut user: User) -> ApplicationResult<GetUserResponse> {
        tracing::info!("Updating user: {}", user.id);

        // Update timestamps
        user.updated_at = chrono::Utc::now();

        // Save user
        self.user_repository.save(user.clone()).await?;
        tracing::info!("Successfully updated user: {}", user.id);

        // Convert to response
        Ok(GetUserResponse::from(user))
    }
}

pub struct DeleteUserUsecase<R: UserRepository> {
    user_repository: R,
}

impl<R: UserRepository> DeleteUserUsecase<R> {
    pub fn new(user_repository: R) -> Self {
        Self { user_repository }
    }

    pub async fn execute(&self, user_id: uuid::Uuid) -> ApplicationResult<()> {
        tracing::info!("Deleting user: {}", user_id);
        self.user_repository.delete(user_id).await?;
        tracing::info!("Successfully deleted user: {}", user_id);
        Ok(())
    }
}

pub struct AuthenticateUserUsecase<R: UserRepository> {
    user_repository: R,
}

impl<R: UserRepository> AuthenticateUserUsecase<R> {
    pub fn new(user_repository: R) -> Self {
        Self { user_repository }
    }

    pub async fn execute(&self, email: &str, password: &str) -> ApplicationResult<GetUserResponse> {
        tracing::debug!("Authenticating user with email: {}", email);
        let user = self.user_repository.find_by_email(email).await?;

        if !user.password.verify(password)? {
            tracing::warn!("Authentication failed for user: {}", email);
            return Err(crate::domain::DomainError::InvalidOperation {
                message: "Invalid credentials".to_string(),
            }
            .into());
        }

        tracing::debug!("Successfully authenticated user: {}", email);
        Ok(GetUserResponse::from(user))
    }
}
