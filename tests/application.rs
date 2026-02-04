#[cfg(test)]
mod tests {
    use crate::application::{dtos::CreateUserRequest, usecases::CreateUserUsecase};
    use crate::domain::{
        value_objects::{Email, Password},
        User,
    };
    use async_trait::async_trait;
    use std::collections::HashMap;
    use uuid::Uuid;

    // Mock repository for testing
    #[derive(Clone)]
    struct MockUserRepository {
        users: std::sync::Arc<tokio::sync::Mutex<HashMap<Uuid, User>>>,
    }

    impl MockUserRepository {
        fn new() -> Self {
            Self {
                users: std::sync::Arc::new(tokio::sync::Mutex::new(HashMap::new())),
            }
        }
    }

    #[async_trait]
    impl crate::domain::services::UserRepository for MockUserRepository {
        async fn find_by_id(&self, id: Uuid) -> Result<User, crate::domain::DomainError> {
            let users = self.users.lock().await;
            users
                .get(&id)
                .cloned()
                .ok_or_else(|| crate::domain::DomainError::NotFound {
                    entity: "User".to_string(),
                    id,
                })
        }

        async fn find_by_email(&self, email: &str) -> Result<User, crate::domain::DomainError> {
            let users = self.users.lock().await;
            users
                .iter()
                .find(|(_, user)| user.email.as_str() == email)
                .map(|(_, user)| user.clone())
                .ok_or_else(|| crate::domain::DomainError::NotFound {
                    entity: "User".to_string(),
                    id: Uuid::nil(),
                })
        }

        async fn save(&self, user: User) -> Result<(), crate::domain::DomainError> {
            let mut users = self.users.lock().await;
            users.insert(user.id, user);
            Ok(())
        }

        async fn delete(&self, id: Uuid) -> Result<(), crate::domain::DomainError> {
            let mut users = self.users.lock().await;
            users.remove(&id);
            Ok(())
        }
    }

    #[tokio::test]
    async fn test_create_user_usecase_success() {
        let repo = MockUserRepository::new();
        let usecase = CreateUserUsecase::new(repo);

        let request = CreateUserRequest {
            email: "test@example.com".to_string(),
            password: "securepassword123".to_string(),
            username: "testuser".to_string(),
        };

        let result = usecase.execute(request).await;

        assert!(result.is_ok());
        let response = result.unwrap();
        assert_eq!(response.username, "testuser");
    }

    #[tokio::test]
    async fn test_create_duplicate_user_fails() {
        let repo = MockUserRepository::new();
        let usecase = CreateUserUsecase::new(repo.clone());

        // First creation should succeed
        let request = CreateUserRequest {
            email: "test@example.com".to_string(),
            password: "securepassword123".to_string(),
            username: "testuser".to_string(),
        };

        let result = usecase.execute(request).await;
        assert!(result.is_ok());

        // Second creation with same email should fail
        let request = CreateUserRequest {
            email: "test@example.com".to_string(),
            password: "anotherpassword".to_string(),
            username: "anotheruser".to_string(),
        };

        let result = usecase.execute(request).await;
        assert!(result.is_err());
    }
}
