use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::user::{
    CreateUserInput, CreateUserUseCase, CreateUserUseCaseImpl, RoleRepository, UserRepository,
};
use go_clean_template::domain;

struct MockUserRepo {
    find_by_email: Arc<std::sync::Mutex<Option<Result<domain::User, domain::Error>>>>,
    create: Arc<std::sync::Mutex<Option<Result<(), domain::Error>>>>,
}

impl MockUserRepo {
    fn new() -> Self {
        MockUserRepo {
            find_by_email: Arc::new(std::sync::Mutex::new(None)),
            create: Arc::new(std::sync::Mutex::new(None)),
        }
    }
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::User>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> {
        let lock = self.find_by_email.lock().unwrap();
        lock.clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> {
        let lock = self.create.lock().unwrap();
        lock.clone().unwrap_or(Ok(()))
    }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> {
        Ok(())
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> {
        Ok(())
    }
}

struct MockRoleRepo;

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_name(&self, _name: &str) -> Result<domain::Role, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> {
        Ok(())
    }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> {
        Ok(())
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> {
        Ok(())
    }
}

#[tokio::test]
async fn test_create_user_success() {
    let user_repo = MockUserRepo::new();
    *user_repo.find_by_email.lock().unwrap() = Some(Err(domain::Error::NotFound));
    *user_repo.create.lock().unwrap() = Some(Ok(()));

    let uc = CreateUserUseCaseImpl::new(
        Arc::new(user_repo),
        Arc::new(MockRoleRepo),
    );

    let input = CreateUserInput {
        name: "Alice".into(),
        email: "alice@example.com".into(),
        phone: "123".into(),
        password: "secret".into(),
        role_ids: vec![],
    };

    let result = uc.execute(input).await;
    assert!(result.is_ok());
    let output = result.unwrap();
    assert_eq!(output.user.name, "Alice");
    assert_eq!(output.user.email, "alice@example.com");
}

#[tokio::test]
async fn test_create_user_duplicate_email() {
    let user_repo = MockUserRepo::new();
    let existing = domain::User::new(
        "Existing".into(),
        "alice@example.com".into(),
        "123".into(),
        vec![],
    )
    .unwrap();
    *user_repo.find_by_email.lock().unwrap() = Some(Ok(existing));

    let uc = CreateUserUseCaseImpl::new(Arc::new(user_repo), Arc::new(MockRoleRepo));

    let input = CreateUserInput {
        name: "Alice".into(),
        email: "alice@example.com".into(),
        phone: "123".into(),
        password: "secret".into(),
        role_ids: vec![],
    };

    let result = uc.execute(input).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn test_create_user_invalid_name() {
    let user_repo = MockUserRepo::new();
    *user_repo.find_by_email.lock().unwrap() = Some(Err(domain::Error::NotFound));

    let uc = CreateUserUseCaseImpl::new(Arc::new(user_repo), Arc::new(MockRoleRepo));

    let input = CreateUserInput {
        name: "".into(),
        email: "alice@example.com".into(),
        phone: "123".into(),
        password: "secret".into(),
        role_ids: vec![],
    };

    let result = uc.execute(input).await;
    assert!(result.is_err());
}
