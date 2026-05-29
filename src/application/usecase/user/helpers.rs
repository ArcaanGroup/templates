use crate::application::error::AppError;
use crate::application::usecase::user::RoleRepository;

pub async fn validate_role_ids(
    role_repo: &dyn RoleRepository,
    ids: &[String],
) -> Result<(), AppError> {
    for id in ids {
        role_repo.find_by_id(id).await?;
    }
    Ok(())
}
