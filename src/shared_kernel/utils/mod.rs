use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};

/// JWT claims structure
#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    pub exp: usize,
    pub iat: usize,
}

/// Utility function to generate a JWT token
pub fn generate_jwt_token(
    subject: String,
    secret: &str,
    expiration_time: i64,
) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
    let expiration = chrono::Utc::now()
        .checked_add_signed(chrono::Duration::seconds(expiration_time))
        .expect("Valid timestamp")
        .timestamp() as usize;

    let claims = Claims {
        sub: subject,
        exp: expiration,
        iat: chrono::Utc::now().timestamp() as usize,
    };

    let token = encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_ref()),
    )?;

    Ok(token)
}

/// Utility function to validate a JWT token
pub fn validate_jwt_token(
    token: &str,
    secret: &str,
) -> Result<Claims, Box<dyn std::error::Error + Send + Sync>> {
    let validation = Validation::default();
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_ref()),
        &validation,
    )?;

    Ok(token_data.claims)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_and_validate_jwt() {
        let secret = "my_secret_key";
        let subject = "test_user".to_string();
        let token = generate_jwt_token(subject.clone(), secret, 3600).unwrap();

        let claims = validate_jwt_token(&token, secret).unwrap();
        assert_eq!(claims.sub, subject);
    }
}
