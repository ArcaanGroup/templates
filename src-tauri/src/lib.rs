use std::collections::HashMap;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str, locale: Option<String>) -> String {
    // Define localized greetings
    let mut greetings: HashMap<&str, &str> = HashMap::new();
    greetings.insert("en", "Hello");
    greetings.insert("fa", "سلام");
    // Add more languages as needed

    // Use 'en' as fallback if locale is not provided or not found in the map
    let greeting = match locale.as_deref() {
        Some("fa") => greetings.get("fa").unwrap_or(&"Hello"),
        _ => greetings.get("en").unwrap_or(&"Hello"),
    };

    format!("{}, {}!", greeting, name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
