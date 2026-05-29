use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
pub struct PaginationParams {
    pub page: Option<i32>,
    pub page_size: Option<i32>,
}

#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T: Serialize> {
    pub data: Vec<T>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
    pub total_pages: i32,
}

impl<T: Serialize> PaginatedResponse<T> {
    pub fn new(data: Vec<T>, total: i64, page: i32, page_size: i32) -> Self {
        let total_pages = if total == 0 {
            1
        } else {
            (total as f64 / page_size as f64).ceil() as i32
        };
        PaginatedResponse {
            data,
            total,
            page,
            page_size,
            total_pages,
        }
    }
}
