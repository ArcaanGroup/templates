pub mod config;
pub mod middleware;
pub mod repositories;

pub struct InfrastructureLayer {}

impl InfrastructureLayer {
    pub fn new() -> Self {
        Self {}
    }
}
