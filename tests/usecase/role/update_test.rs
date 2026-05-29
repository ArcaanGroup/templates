use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::role::{UpdateRoleInput, UpdateRoleUseCase, UpdateRoleUseCaseImpl};
use go_clean_template::application::usecase::user::RoleRepository;
use go_clean_template::domain;

struct MockRoleRepo {
    find_by_id: Arc<std::sync::Mutex<Option<Result<domain::Role, domain::Error>>>>,
    find_by_name: Arc<std::sync::Mutex<Option<Result<domain::Role, domain::Error>>>>,
    update_called: Arc<std::sync::Mutex<bool>>,
}

impl MockRoleRepo {
    fn new() -> Self {
        MockRoleRepo {
            find_by_id: Arc::new(std::sync::Mutex::new(None)),
            find_by_name: Arc::new(std::sync::Mutex::new(None)),
            update_called: Arc::new(std::sync::Mutex::new(false)),
        }
    }
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        self.find_by_id.lock().unwrap().clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_name(&self, _name: &str) -> Result<domain::Role, domain::Error> {
        self.find_by_name.lock().unwrap().clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> {
        *self.update_called.lock().unwrap() = true;
        Ok(())
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_update_role_success() {
    let role = domain::Role::new("original".into(), "Original".into()).unwrap();
    let repo = MockRoleRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Ok(role));
    *repo.find_by_name.lock().unwrap() = Some(Err(domain::Error::NotFound));

    let uc = UpdateRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute("1", UpdateRoleInput {
        name: "updated".into(),
        description: "Updated".into(),
    }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().role.name, "updated");
}

#[tokio::test]
async fn test_update_role_not_found() {
    let repo = MockRoleRepo::new();
    *repo.find_by_id.lock().unwrap() = Some(Err(domain::Error::NotFound));

    let uc = UpdateRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute("999", UpdateRoleInput {
        name: "test".into(),
        description: "test".into(),
    }).await;
    assert!(result.is_err());
}
