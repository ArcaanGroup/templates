use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::role::{ListRolesInput, ListRolesUseCase, ListRolesUseCaseImpl};
use go_clean_template::application::usecase::user::RoleRepository;
use go_clean_template::domain;

struct MockRoleRepo {
    roles: Vec<domain::Role>,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::Role, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn find_all(&self, offset: usize, limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        let total = self.roles.len() as i64;
        let slice = self.roles.iter().skip(offset).take(limit).cloned().collect();
        Ok((slice, total))
    }
    async fn find_by_name(&self, _name: &str) -> Result<domain::Role, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_list_roles_success() {
    let repo = MockRoleRepo {
        roles: vec![
            domain::Role::new("admin".into(), "Admin".into()).unwrap(),
            domain::Role::new("user".into(), "User".into()).unwrap(),
        ],
    };

    let uc = ListRolesUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(ListRolesInput { page: 1, page_size: 20 }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().roles.len(), 2);
}

#[tokio::test]
async fn test_list_roles_empty() {
    let repo = MockRoleRepo { roles: vec![] };
    let uc = ListRolesUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(ListRolesInput { page: 1, page_size: 20 }).await;
    assert!(result.is_ok());
    assert!(result.unwrap().roles.is_empty());
}
