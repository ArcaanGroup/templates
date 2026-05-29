use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::role::{
    CreateRoleInput, CreateRoleUseCase, CreateRoleUseCaseImpl,
};
use go_clean_template::application::usecase::user::RoleRepository;
use go_clean_template::domain;

struct MockRoleRepo {
    find_by_name: Arc<std::sync::Mutex<Option<Result<domain::Role, domain::Error>>>>,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_name(&self, _name: &str) -> Result<domain::Role, domain::Error> {
        self.find_by_name.lock().unwrap().clone().unwrap_or(Err(domain::Error::NotFound))
    }
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_create_role_success() {
    let repo = MockRoleRepo {
        find_by_name: Arc::new(std::sync::Mutex::new(Some(Err(domain::Error::NotFound)))),
    };

    let uc = CreateRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(CreateRoleInput {
        name: "admin".into(),
        description: "Admin role".into(),
    }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().role.name, "admin");
}

#[tokio::test]
async fn test_create_role_duplicate() {
    let existing = domain::Role::new("admin".into(), "".into()).unwrap();
    let repo = MockRoleRepo {
        find_by_name: Arc::new(std::sync::Mutex::new(Some(Ok(existing)))),
    };

    let uc = CreateRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(CreateRoleInput {
        name: "admin".into(),
        description: "".into(),
    }).await;
    assert!(result.is_err());
}
