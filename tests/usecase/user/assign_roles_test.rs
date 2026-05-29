use std::sync::Arc;

use async_trait::async_trait;

use rust_clean_template::application::usecase::user::{
    AssignRolesInput, AssignRolesUseCase, AssignRolesUseCaseImpl, RoleRepository, UserRepository,
};
use rust_clean_template::domain;

struct MockUserRepo {
    user: Arc<std::sync::Mutex<Option<domain::User>>>,
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        self.user
            .lock()
            .unwrap()
            .clone()
            .ok_or(domain::Error::NotFound)
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
    async fn update(&self, user: &domain::User) -> Result<(), domain::Error> {
        *self.user.lock().unwrap() = Some(user.clone());
        Ok(())
    }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> {
        Ok(())
    }
}

struct MockRoleRepo {
    role_id: String,
}

#[async_trait]
impl RoleRepository for MockRoleRepo {
    async fn find_by_id(&self, id: &str) -> Result<domain::Role, domain::Error> {
        if id == self.role_id {
            Ok(domain::Role::new("admin".into(), "".into()).unwrap())
        } else {
            Err(domain::Error::NotFound)
        }
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
async fn test_assign_roles_success() {
    let role_id = domain::generate_id();
    let user = domain::User::new("Alice".into(), "a@b.com".into(), "123".into(), vec![]).unwrap();

    let uc = AssignRolesUseCaseImpl::new(
        Arc::new(MockUserRepo {
            user: Arc::new(std::sync::Mutex::new(Some(user))),
        }),
        Arc::new(MockRoleRepo {
            role_id: role_id.clone(),
        }),
    );

    let result = uc
        .execute(
            "1",
            AssignRolesInput {
                role_ids: vec![role_id],
            },
        )
        .await;
    assert!(result.is_ok());
}
