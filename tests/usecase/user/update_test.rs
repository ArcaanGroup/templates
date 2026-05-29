use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::user::{
    RoleRepository, UpdateUserInput, UpdateUserUseCase, UpdateUserUseCaseImpl, UserRepository,
};
use go_clean_template::domain;

struct MockUserRepo {
    find_by_id: Arc<std::sync::Mutex<Option<Result<domain::User, domain::Error>>>>,
    find_by_email: Arc<std::sync::Mutex<Option<Result<domain::User, domain::Error>>>>,
    update: Arc<std::sync::Mutex<Option<Result<(), domain::Error>>>>,
}

impl MockUserRepo {
    fn new() -> Self {
        MockUserRepo {
            find_by_id: Arc::new(std::sync::Mutex::new(None)),
            find_by_email: Arc::new(std::sync::Mutex::new(None)),
            update: Arc::new(std::sync::Mutex::new(None)),
        }
    }
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        self.find_by_id.lock().unwrap().clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::User>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> {
        self.find_by_email.lock().unwrap().clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> {
        self.update.lock().unwrap().clone().unwrap_or(Ok(()))
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
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
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_update_user_success() {
    let user = domain::User::new("Original".into(), "orig@example.com".into(), "123".into(), vec![]).unwrap();
    let repo = MockUserRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Ok(user));
    *repo.find_by_email.lock().unwrap() = Some(Err(domain::Error::NotFound));
    *repo.update.lock().unwrap() = Some(Ok(()));

    let uc = UpdateUserUseCaseImpl::new(Arc::new(repo), Arc::new(MockRoleRepo));
    let result = uc.execute("1", UpdateUserInput {
        name: "Updated".into(),
        email: "new@example.com".into(),
        phone: "456".into(),
        avatar: "".into(),
        role_ids: vec![],
    }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().user.name, "Updated");
}

#[tokio::test]
async fn test_update_user_not_found() {
    let repo = MockUserRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Err(domain::Error::NotFound));

    let uc = UpdateUserUseCaseImpl::new(Arc::new(repo), Arc::new(MockRoleRepo));
    let result = uc.execute("999", UpdateUserInput {
        name: "Test".into(),
        email: "test@example.com".into(),
        phone: "".into(),
        avatar: "".into(),
        role_ids: vec![],
    }).await;
    assert!(result.is_err());
}
