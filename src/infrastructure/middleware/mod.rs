use axum::{body::Body, http::Request, middleware::Next, response::Response};
use tracing::info;

pub async fn logging_middleware(req: Request<Body>, next: Next) -> Result<Response, Response> {
    let method = req.method().clone();
    let uri = req.uri().clone();

    info!("Started {} {}", method, uri);

    let start = std::time::Instant::now();
    let response = next.run(req).await;
    let duration = start.elapsed();

    info!(
        "Completed {} {} with status {} in {:?}",
        method,
        uri,
        response.status(),
        duration
    );

    Ok(response)
}
