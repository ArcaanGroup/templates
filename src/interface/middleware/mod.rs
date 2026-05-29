use axum::body::Body;
use axum::http::{HeaderValue, Method, Request, StatusCode};
use axum::response::Response;
use axum::middleware::Next;
use tokio::time::Instant;
use tracing::{error, info};

use crate::domain::generate_id;

pub async fn request_id(
    mut req: Request<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let id = req
        .headers()
        .get("X-Request-ID")
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string())
        .unwrap_or_else(generate_id);

    req.headers_mut()
        .insert("X-Request-ID", HeaderValue::from_str(&id).unwrap());

    let mut res = next.run(req).await;
    res.headers_mut()
        .insert("X-Request-ID", HeaderValue::from_str(&id).unwrap());

    Ok(res)
}

pub async fn logger_middleware(
    req: Request<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let start = Instant::now();
    let method = req.method().clone();
    let uri = req.uri().clone();
    let request_id = req
        .headers()
        .get("X-Request-ID")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("unknown")
        .to_string();

    let res = next.run(req).await;

    let status = res.status();
    let duration = start.elapsed();

    info!(
        method = %method,
        path = %uri.path(),
        status = %status,
        duration = %format!("{:?}", duration),
        request_id = %request_id,
        "request completed"
    );

    Ok(res)
}

pub async fn recover_middleware(
    req: Request<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let uri = req.uri().clone();
    let method = req.method().clone();

    let res = next.run(req).await;

    if res.status().is_server_error() {
        error!(%method, path = %uri.path(), "internal server error");
        return Err(StatusCode::INTERNAL_SERVER_ERROR);
    }

    Ok(res)
}

pub fn cors_layer() -> tower_http::cors::CorsLayer {
    tower_http::cors::CorsLayer::new()
        .allow_origin(tower_http::cors::Any)
        .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE, Method::OPTIONS])
        .allow_headers([
            axum::http::header::CONTENT_TYPE,
            axum::http::header::AUTHORIZATION,
            axum::http::header::HeaderName::from_static("x-request-id"),
        ])
}
