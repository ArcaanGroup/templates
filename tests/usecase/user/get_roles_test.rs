use std::sync::Arc;

use async_trait::async_trait;

use go_clean_template::application::usecase::user::{
    GetUserRolesInput, GetUserRolesUseCase, GetUserRolesUseCaseImpl, RoleRepository, UserRepository,
};
use go_clean_template::domain;

struct MockUserRepo {
    user: domain::User,
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        Ok(self.user.clone())
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::User>, i64), domain::Error> {
        Ok((vec![], 0))
    }
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> { Err(domain::Error::NotFound) }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

struct MockRoleRepo {
    roles: std::collections::HashMap<String, domain::Role>,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, id: &str) -> Result<domain::Role, domain::Error> {
        self.roles.get(id).cloned().ok_or(domain::Error::NotFound)
    }
    async fn find_all(&self, _offset: usize, _limit: usize) -> Result<(Vec<domain::Role>, i64), domain::Error> {
        let v: Vec<_> = self.roles.values().cloned().collect();
        let l = v.len() as i64;
        Ok((v, l))
    }
    async fn find_by_name(&self, _name: &str) -> Result<domain::Role, domain::Error> { Err(domain::Error::NotFound) }
    async fn create(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _role: &domain::Role) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_get_user_roles_success() {
    let admin_role = domain::Role::new("admin".into(), "Admin".into()).unwrap();
    let role_id = admin_role.id.clone();

    let mut roles = std::collections::HashMap::new();
    roles.insert(role_id.clone(), admin_role.clone());

    let mut user = domain::User::new("Alice".into(), "a@b.com".into(), "123".into(), vec![]).unwrap();
    user.role_ids = vec![role_id];

    let uc = GetUserRolesUseCaseImpl::new(
        Arc::new(MockUserRepo { user }),
        Arc::new(MockRoleRepo { roles }),
    );

    let result = uc.execute(GetUserRolesInput { id: "1".into() }).await;
    assert!(result.is_ok());
    assert_eq!(result.unwrap().roles.len(), 1);
}
