#[derive(Debug, Clone)]
pub struct Config {
    pub port: u16,
    pub log_level: String,
}

impl Config {
    pub fn load() -> Result<Self, anyhow::Error> {
        let port = std::env::var("PORT")
            .ok()
            .and_then(|v| v.parse::<u16>().ok())
            .unwrap_or(8080);

        let log_level = std::env::var("LOG_LEVEL").unwrap_or_else(|_| "info".to_string());

        Ok(Config { port, log_level })
    }
}
