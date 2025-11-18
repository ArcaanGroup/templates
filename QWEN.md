# Project Overview: Sepehr Ground Control Platform

Sepehr is a ground control platform designed for submarine operations, providing essential mission planning, real-time monitoring, and data management capabilities. The platform features bidirectional wireless communication via dorji DRF7020D27 radio module with submarine hardware, map-based mission planning with waypoint management, real-time telemetry visualization, offline map caching, and control parameter management.

## Technical Architecture

### Backend (Rust/Tauri)
- **Framework**: Tauri v2 for secure native desktop application
- **Language**: Rust for safety and performance
- **Database**: SQLite for lightweight, file-based data storage
- **Communication**: dorji DRF7020D27 433MHz RF transceiver module (27dBm output power)
- **Dependencies**: `serialport`, `rusqlite`, `serde`, `tokio`, `geo`

### Frontend (Svelte)
- **Framework**: SvelteKit for modern web application
- **Map Engine**: MapLibre GL JS for offline-capable maps
- **UI Components**: Custom components with TailwindCSS styling
- **Charting**: Real-time visualization with Chart.js or D3
- **Dependencies**: `svelte-kit`, `maplibre-gl`, `chart.js`, `tailwindcss`

## Core Features

### 1. RF Communication Module
- Bidirectional communication with submarine hardware via dorji DRF7020D27 module
- Wireless data transmission over 433MHz ISM band
- Configurable parameters including frequency channels, RF power levels, baud rate
- Real-time data streaming capability with RF link quality monitoring
- Exact matching of hardware specifications

### 2. Mission Planning Interface
- Map-based waypoint addition through click interface
- Auto-capture of geographic coordinates (latitude/longitude)
- Form popup for mission parameters (depth, duration, actions)
- Manual waypoint entry with coordinate validation
- Waypoint validation for coordinate ranges and parameter limits

### 3. Data Management System
- Real-time data acquisition with configurable sampling rate (0.5 to 10 seconds)
- Continuous data streaming from submarine sensors
- SQLite database with structured tables:
  - Mission Files Table (mission_name, creation_datetime, description)
  - Mission Data Table (foreign key to mission files, timestamp, sensor_data)
  - Control Parameters Table (6 float coefficients with versioning)
- Mission file browser with filtering capabilities
- One-click mission data visualization
- Export capability for analysis (CSV, JSON, MATLAB formats)

### 4. Offline Map Caching
- Map cache management with unique names, zoom levels, and center coordinates
- Duplicate prevention system using hash-based checking
- Offline availability indicator
- Cache management panel for user control
- Quick selection of cached maps at startup

### 5. Control Parameters Management
- Storage of 6 floating-point control coefficients
- Save, load, and version history operations
- Parameter validation before transmission to submarine
- Version comparison functionality

### 6. Company Profile Tab
- Static company information display
- Logo and contact details
- Rich text with image support
- Dedicated tab interface

## Development Phases

### Phase 1 (Core): Serial communication + Mission planning + Basic data storage
- Project setup and architecture
- Serial communication module
- Basic database setup
- Mission planning interface
- Real-time data integration

### Phase 2 (Enhanced): Map caching + Control parameters + Advanced data retrieval
- Offline map caching system
- Control parameters management
- Advanced data retrieval and visualization
- Enhanced mission planning

### Phase 3 (Polish): Company tab + UI refinements + Error handling
- Company profile and branding
- Comprehensive error handling
- UI/UX polish and performance
- Testing and quality assurance
- Deployment and distribution

## File Structure
```
src-tauri/
├── Cargo.toml
├── tauri.conf.json
├── capabilities/
├── src/
│   ├── lib.rs
│   ├── main.rs
│   ├── core/
│   │   ├── serial.rs
│   │   ├── db.rs
│   │   └── error.rs
│   ├── commands/
│   ├── services/
│   ├── models/
│   └── utils/
└── migrations/

src/
├── app.html
├── app.js
├── lib/
│   ├── components/
│   ├── stores/
│   ├── tauri/
│   └── styles/
├── routes/
├── hooks.client.js
└── service-worker.js
```

## Project Goals
- Windows/Linux compatibility
- Cross-platform functionality using Tauri
- Offline-capable map system for remote operations
- Real-time telemetry with configurable sampling rates
- Secure and validated control parameter transmission
- Professional UI with submarine-themed design
- Modular architecture for future expansion

## Dependencies
- Rust: `serialport`, `rusqlite`, `serde`, `tauri`, `tokio`, `geo`
- Svelte: `svelte-kit`, `maplibre-gl`, `chart.js`, `tailwindcss`, `tauri`
- System: SQLite3, MapLibre GL native dependencies

This ground control platform is designed to provide essential mission planning, real-time monitoring, and data management capabilities specifically for submarine operations.