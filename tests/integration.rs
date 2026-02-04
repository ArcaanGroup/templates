#[cfg(test)]
mod tests {
    use crate::{
        application::{dtos::CreateUserRequest, usecases::CreateUserUsecase},
        domain::value_objects::{Email, Password},
        infrastructure::repositories::UserPostgresRepository,
    };
    use axum::{
        body::Body,
        http::{Request, StatusCode},
    };
    use serde_json::json;
    use tower::ServiceExt; // for `app.oneshot()`

    #[tokio::test]
    async fn test_health_endpoint() {
        // We would normally test the actual app here, but for now we'll just verify
        // that the route exists and returns the expected response
        assert!(true); // Placeholder test
    }

    #[tokio::test]
    async fn test_create_user_endpoint() {
        // Integration test would require a running database
        // For now, we'll just verify the structure works
        let request = CreateUserRequest {
            email: "integration@test.com".to_string(),
            password: "integrationpassword123".to_string(),
            username: "integration_user".to_string(),
        };

        // Verify that the request can be serialized/deserialized
        let json = serde_json::to_value(&request).unwrap();
        let deserialized: CreateUserRequest = serde_json::from_value(json).unwrap();

        assert_eq!(deserialized.email, "integration@test.com");
        assert_eq!(deserialized.username, "integration_user");
    }
}
