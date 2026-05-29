use crate::domain::error::Error;
use crate::domain::id::generate_id;
use chrono::{DateTime, Utc};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone)]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
    pub phone: String,
    pub password_hash: String,
    pub email_verified: bool,
    pub phone_verified: bool,
    pub avatar: String,
    pub role_ids: Vec<String>,
    pub order_count: i32,
    pub wallet_balance: i64,
    pub language: String,
    pub currency: String,
    pub last_login_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub deleted_at: Option<DateTime<Utc>>,
}

impl User {
    pub fn new(
        name: String,
        email: String,
        phone: String,
        role_ids: Vec<String>,
    ) -> Result<Self, Error> {
        let u = User {
            id: generate_id(),
            name,
            email,
            phone,
            password_hash: String::new(),
            email_verified: false,
            phone_verified: false,
            avatar: String::new(),
            role_ids,
            order_count: 0,
            wallet_balance: 0,
            language: "fa".to_string(),
            currency: "IRR".to_string(),
            last_login_at: None,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            deleted_at: None,
        };
        u.validate()?;
        Ok(u)
    }

    pub fn update_info(
        &mut self,
        name: String,
        email: String,
        phone: String,
        avatar: String,
        role_ids: Vec<String>,
    ) -> Result<(), Error> {
        self.name = name;
        self.email = email;
        self.phone = phone;
        self.avatar = avatar;
        self.role_ids = role_ids;
        self.updated_at = Utc::now();
        self.validate()
    }

    pub fn assign_roles(&mut self, role_ids: Vec<String>) {
        self.role_ids = role_ids;
        self.updated_at = Utc::now();
    }

    pub fn mark_deleted(&mut self) {
        self.deleted_at = Some(Utc::now());
        self.updated_at = Utc::now();
    }

    pub fn validate(&self) -> Result<(), Error> {
        let mut errs = Vec::new();
        if self.name.trim().is_empty() {
            errs.push("name is required");
        }
        if self.email.trim().is_empty() {
            errs.push("email is required");
        }
        if !errs.is_empty() {
            return Err(Error::InvalidInput(errs.join("; ")));
        }
        Ok(())
    }

    pub fn set_password(&mut self, password: &str) -> Result<(), Error> {
        if password.is_empty() {
            return Err(Error::InvalidInput("password is required".to_string()));
        }
        self.password_hash = hash_password(password);
        Ok(())
    }
}

fn hash_password(password: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_user_valid() {
        let u = User::new(
            "Alice".into(),
            "alice@example.com".into(),
            "123".into(),
            vec![],
        );
        assert!(u.is_ok());
        let u = u.unwrap();
        assert_eq!(u.name, "Alice");
        assert_eq!(u.email, "alice@example.com");
        assert_eq!(u.language, "fa");
    }

    #[test]
    fn test_new_user_invalid_empty_name() {
        let u = User::new(
            "".into(),
            "alice@example.com".into(),
            "123".into(),
            vec![],
        );
        assert!(u.is_err());
        assert_eq!(u.unwrap_err(), Error::InvalidInput("name is required".into()));
    }

    #[test]
    fn test_set_password() {
        let mut u = User::new(
            "Alice".into(),
            "alice@example.com".into(),
            "123".into(),
            vec![],
        )
        .unwrap();
        assert!(u.set_password("secret123").is_ok());
        assert_eq!(u.password_hash.len(), 64);
    }

    #[test]
    fn test_mark_deleted() {
        let mut u = User::new(
            "Alice".into(),
            "alice@example.com".into(),
            "123".into(),
            vec![],
        )
        .unwrap();
        assert!(u.deleted_at.is_none());
        u.mark_deleted();
        assert!(u.deleted_at.is_some());
    }

}
