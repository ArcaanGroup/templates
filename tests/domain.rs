#[cfg(test)]
mod tests {
    use crate::domain::{
        entities::User,
        value_objects::{Email, Password},
    };

    #[tokio::test]
    async fn test_create_user_success() {
        let email = Email::new("test@example.com".to_string()).unwrap();
        let password = Password::new("securepassword123".to_string()).unwrap();
        let user = User::new(email, password, "testuser".to_string()).unwrap();

        assert!(!user.id.is_nil());
        assert_eq!(user.username, "testuser");
        assert!(user.is_active);
    }

    #[tokio::test]
    async fn test_create_invalid_email_fails() {
        let result = Email::new("invalid-email".to_string());

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_create_short_password_fails() {
        let result = Password::new("short".to_string());

        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_user_activation_deactivation() {
        let mut user = User::new(
            Email::new("test@example.com".to_string()).unwrap(),
            Password::new("securepassword123".to_string()).unwrap(),
            "testuser".to_string(),
        )
        .unwrap();

        user.deactivate();
        assert!(!user.is_active);

        user.activate();
        assert!(user.is_active);
    }
}
