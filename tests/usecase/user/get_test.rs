use std::sync::Arc;

use async_trait::async_trait;

use rust_clean_template::application::usecase::user::{
    GetUserInput, GetUserUseCase, GetUserUseCaseImpl, UserRepository,
};
use rust_clean_template::domain;

struct MockUserRepo {
    result: Arc<std::sync::Mutex<Option<Result<domain::User, domain::Error>>>>,
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        self.result
            .lock()
            .unwrap()
            .clone()
            .unwrap_or(Err(domain::Error::NotFound))
    }
    async fn find_all(
        &self,
        _offset: usize,
        _limit: usize,
    ) -> Result<(Vec<domain::User>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> {
        Ok(())
    }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> {
        Ok(())
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> {
        Ok(())
    }
}

#[tokio::test]
async fn test_get_user_success() {
    let user = domain::User::new(
        "Alice".into(),
        "alice@example.com".into(),
        "123".into(),
        vec![],
    )
    .unwrap();
    let repo = MockUserRepo {
        result: Arc::new(std::sync::Mutex::new(Some(Ok(user)))),
    };

    let uc = GetUserUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(GetUserInput { id: "123".into() }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().user.name, "Alice");
}

#[tokio::test]
async fn test_get_user_not_found() {
    let repo = MockUserRepo {
        result: Arc::new(std::sync::Mutex::new(Some(Err(domain::Error::NotFound)))),
    };

    let uc = GetUserUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(GetUserInput { id: "999".into() }).await;
    assert!(result.is_err());
}
