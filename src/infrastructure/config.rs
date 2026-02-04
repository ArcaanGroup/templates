use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;
use std::env;

#[derive(Debug, Deserialize, Clone)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub jwt: JwtConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Deserialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct JwtConfig {
    pub secret: String,
    pub expiration_time: i64, // in seconds
}

impl AppConfig {
    pub fn from_env() -> Result<Self, ConfigError> {
        let mut s = Config::builder()
            // Start off by merging in the "default" values
            .set_default("server.host", "127.0.0.1")?
            .set_default("server.port", 8080)?
            .set_default("jwt.expiration_time", 3600)? // 1 hour
            // Add in a local configuration file
            .add_source(File::with_name("config/default").required(false))
            // Add in a global configuration file
            .add_source(File::with_name("/etc/myapp/config").required(false))
            // Add in environment variables prefixed with APP_
            .add_source(Environment::with_prefix("APP").separator("__"))
            // Build the configuration
            .build()?;

        s.try_deserialize()
    }
}
