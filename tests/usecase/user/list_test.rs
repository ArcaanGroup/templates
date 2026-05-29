use std::sync::{Arc, Mutex};

use async_trait::async_trait;

use go_clean_template::application::usecase::user::{ListUsersInput, ListUsersUseCase, ListUsersUseCaseImpl, UserRepository};
use go_clean_template::domain;

struct MockUserRepo {
    items: Arc<Mutex<Vec<domain::User>>>,
}

#[async_trait]
impl UserRepository for MockUserRepo {
    async fn find_by_id(&self, _id: &str) -> Result<domain::User, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn find_all(&self, offset: usize, limit: usize) -> Result<(Vec<domain::User>, i64), domain::Error> {
        let items = self.items.lock().unwrap();
        let total = items.len() as i64;
        let slice = items.iter().skip(offset).take(limit).cloned().collect();
        Ok((slice, total))
    }
    async fn find_by_email(&self, _email: &str) -> Result<domain::User, domain::Error> {
        Err(domain::Error::NotFound)
    }
    async fn create(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn update(&self, _user: &domain::User) -> Result<(), domain::Error> { Ok(()) }
    async fn delete(&self, _id: &str) -> Result<(), domain::Error> { Ok(()) }
}

#[tokio::test]
async fn test_list_users_success() {
    let repo = MockUserRepo {
        items: Arc::new(Mutex::new(vec![
            domain::User::new("Alice".into(), "alice@example.com".into(), "123".into(), vec![]).unwrap(),
            domain::User::new("Bob".into(), "bob@example.com".into(), "456".into(), vec![]).unwrap(),
        ])),
    };

    let uc = ListUsersUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(ListUsersInput { page: 1, page_size: 20 }).await;
    assert!(result.is_ok());
    let output = result.unwrap();
    assert_eq!(output.users.len(), 2);
    assert_eq!(output.total, 2);
}

#[tokio::test]
async fn test_list_users_empty() {
    let repo = MockUserRepo {
        items: Arc::new(Mutex::new(vec![])),
    };

    let uc = ListUsersUseCaseImpl::new(Arc::new(repo));
    let result = uc.execute(ListUsersInput { page: 1, page_size: 20 }).await;
    assert!(result.is_ok());
    let output = result.unwrap();
    assert!(output.users.is_empty());
    assert_eq!(output.total, 0);
}
