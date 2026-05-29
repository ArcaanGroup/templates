use std::sync::Arc;

use async_trait::async_trait;

use rust_clean_template::application::usecase::role::{
    DeleteRoleInput, DeleteRoleUseCase, DeleteRoleUseCaseImpl,
};
use rust_clean_template::application::usecase::user::RoleRepository;
use rust_clean_template::domain;

struct MockRoleRepo {
    find_by_id: Arc<std::sync::Mutex<Option<Result<domain::Role, domain::Error>>>>,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        self.find_by_id
            .lock()
            .unwrap()
            .clone()
            .unwrap_or(Err(domain::Error::NotFound))
    }
    async fn find_all(
        &self,
        _offset: usize,
        _limit: usize,
    ) -> Result<(Vec<domain::Role>, i64), domain::Error> {
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
async fn test_delete_role_success() {
    let role = domain::Role::new("admin".into(), "".into()).unwrap();
    let repo = MockRoleRepo {
        find_by_id: Arc::new(std::sync::Mutex::new(Some(Ok(role)))),
    };

    let uc = DeleteRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(DeleteRoleInput { id: "1".into() }).await;
    assert!(result.is_ok());
}

#[tokio::test]
async fn test_delete_role_not_found() {
    let repo = MockRoleRepo {
        find_by_id: Arc::new(std::sync::Mutex::new(Some(Err(domain::Error::NotFound)))),
    };

    let uc = DeleteRoleUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(DeleteRoleInput { id: "999".into() }).await;
    assert!(result.is_err());
}
