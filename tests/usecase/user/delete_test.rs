use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::user::{DeleteUserInput, DeleteUserUseCase, DeleteUserUseCaseImpl, UserRepository};
use go_clean_template::domain;

struct MockUserRepo {
    find_by_id: Arc<std::sync::Mutex<Option<Result<domain::User, domain::Error>>>>,
    delete: Arc<std::sync::Mutex<Option<Result<(), domain::Error>>>>,
}

impl MockUserRepo {
    fn new() -> Self {
        MockUserRepo {
            find_by_id: Arc::new(std::sync::Mutex::new(None)),
            delete: Arc::new(std::sync::Mutex::new(None)),
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
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> { Err(domain::Error::NotFound) }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> {
        self.delete.lock().unwrap().clone().unwrap_or(Ok(()))
    }
}

#[tokio::test]
async fn test_delete_user_success() {
    let user = domain::User::new("Alice".into(), "a@b.com".into(), "123".into(), vec![]).unwrap();
    let repo = MockUserRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Ok(user));
    *repo.delete.lock().unwrap() = Some(Ok(()));

    let uc = DeleteUserUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(DeleteUserInput { id: "1".into() }).await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_delete_user_not_found() {
    let repo = MockUserRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Err(domain::Error::NotFound));

    let uc = DeleteUserUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(DeleteUserInput { id: "999".into() }).await;
    assert!(result.is_err());
}
