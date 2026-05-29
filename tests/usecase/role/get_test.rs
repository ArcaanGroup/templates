use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::role::{GetRoleInput, GetRoleUseCase, GetRoleUseCaseImpl};
use go_clean_template::application::usecase::user::RoleRepository;
use go_clean_template::domain;

struct MockRoleRepo {
    role: domain::Role,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        Ok(self.role.clone())
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
async fn test_get_role_success() {
    let role = domain::Role::new("admin".into(), "Admin".into()).unwrap();
    let uc = GetRoleUseCaseImpl::new(Arc::new(MockRoleRepo { role }));
    let result = uc.execute(GetRoleInput { id: "1".into() }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().role.name, "admin");
}
