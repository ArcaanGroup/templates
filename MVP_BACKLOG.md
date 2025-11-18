# MVP Ground Control Platform - Submarine Operations Backlog
## **Phase 1: Core Foundation (Weeks 1-6)**
*Serial communication + Mission planning + Basic data storage*
---
### **Step 1.1: Project Setup & Architecture**
#### **Rust Services**
- [ ] Create Tauri project structure with Rust backend
- [ ] Configure Cargo.toml with dependencies: `serialport`, `serde`, `rusqlite`, `tauri`
- [ ] Set up workspace structure: `core/`, `services/`, `models/`, `utils/`
- [ ] Implement platform detection for Windows/Linux serial port handling
- [ ] Create build scripts for cross-platform compilation (Windows/Linux)
#### **Svelte UI**
- [ ] Initialize SvelteKit project with Tauri integration
- [ ] Configure Vite build pipeline for Tauri
- [ ] Set up TailwindCSS for styling with submarine-themed color palette
- [ ] Create basic application shell with navigation tabs
- [ ] Implement responsive layout system for desktop/tablet compatibility
---
### **Step 1.2: Serial Communication Module**
#### **Rust Services**
- [ ] Implement `SerialPortService` struct with connection management
- [ ] Create serial configuration struct: `BaudRate`, `DataBits`, `Parity`, `StopBits`
- [ ] Implement bidirectional communication: `send_command()` and `receive_data()` methods
- [ ] Add data parsing for submarine-specific protocol (match hardware specs exactly)
- [ ] Implement connection state management and error handling
- [ ] Create event system for notifying UI of connection status changes
#### **Svelte UI**
- [ ] Design serial connection panel with dropdown for available ports
- [ ] Create configuration form for serial parameters (baud rate, data bits, etc.)
- [ ] Implement connection status indicator (LED-style visual feedback)
- [ ] Add real-time data stream display area with scrollable text viewer
- [ ] Create error toast notifications for connection failures
---
### **Step 1.3: Basic Database Setup**
#### **Rust Services**
- [ ] Create SQLite database schema with migrations system
- [ ] Implement `MissionFiles` table: `id INTEGER PRIMARY KEY`, `mission_name TEXT`, `creation_datetime DATETIME`, `description TEXT`
- [ ] Implement `MissionData` table: `id INTEGER PRIMARY KEY`, `mission_id INTEGER`, `timestamp DATETIME`, `sensor_data TEXT`
- [ ] Create database connection pool with connection management
- [ ] Implement CRUD operations for mission files and data
- [ ] Add data validation and sanitization for all database operations
#### **Svelte UI**
- [ ] Design mission creation dialog with basic fields (name, description)
- [ ] Create mission file browser with table view
- [ ] Implement mission selection interface with visual feedback
- [ ] Add basic data visualization placeholder (chart container)
- [ ] Create loading states for database operations
---
### **Step 1.4: Mission Planning Interface - Core**
#### **Rust Services**
- [ ] Create `MissionPlanningService` with waypoint validation logic
- [ ] Implement coordinate validation: check latitude (-90 to 90), longitude (-180 to 180)
- [ ] Add depth validation: minimum 0m, maximum submarine-rated depth
- [ ] Create waypoint data structure with all required parameters
- [ ] Implement mission serialization/deserialization for submarine protocol
#### **Svelte UI**
- [ ] Integrate MapLibre GL JS as map engine (offline-capable)
- [ ] Create map container with basic controls (zoom, pan)
- [ ] Implement click-to-add-waypoint functionality
- [ ] Design waypoint parameter form with validation feedback
- [ ] Create waypoint list sidebar with drag-and-drop reordering
- [ ] Add visual waypoint markers on map with numbering
---
### **Step 1.5: Real-Time Data Integration**
#### **Rust Services**
- [ ] Create `TelemetryService` with configurable sampling rate (0.5-10s)
- [ ] Implement data buffering and batch processing for efficiency
- [ ] Add real-time data streaming to UI via Tauri events
- [ ] Create mission data storage service with automatic timestamping
- [ ] Implement data format conversion for visualization
#### **Svelte UI**
- [ ] Design real-time telemetry dashboard with multiple sensor displays
- [ ] Create configurable sampling rate slider (0.5s to 10s)
- [ ] Implement live updating charts using Chart.js or D3
- [ ] Add data logging toggle switch with visual feedback
- [ ] Create alert system for out-of-range sensor values
- [ ] Implement mission timeline visualization
---
## **Phase 2: Enhanced Capabilities (Weeks 7-10)**
*Map caching + Control parameters + Advanced data retrieval*
---
### **Step 2.1: Offline Map Caching System**
#### **Rust Services**
- [ ] Create `MapCacheService` with tile storage management
- [ ] Implement cache metadata: `unique_name`, `zoom_level`, `center_coordinates`, `bbox`
- [ ] Add hash-based duplicate detection for map tiles
- [ ] Create cache cleanup system with LRU algorithm
- [ ] Implement offline availability checking logic
- [ ] Add map export/import functionality for sharing cached areas
#### **Svelte UI**
- [ ] Design cache management panel with list of saved maps
- [ ] Create map caching interface: draw rectangle or enter coordinates
- [ ] Implement visual cache status indicators on main map (different colored borders)
- [ ] Add cache size display and cleanup controls
- [ ] Create startup screen with cached map selection
- [ ] Design visual differentiation between online and offline map modes
---
### **Step 2.2: Control Parameters Management**
#### **Rust Services**
- [ ] Create `ControlParameters` struct with 6 float coefficients
- [ ] Implement versioning system with timestamps and descriptions
- [ ] Add parameter validation rules before transmission
- [ ] Create safe transmission protocol with confirmation handshake
- [ ] Implement parameter history storage in SQLite database
- [ ] Add parameter comparison functionality (diff between versions)
#### **Svelte UI**
- [ ] Design control parameters editor with 6 input fields
- [ ] Create parameter validation feedback with real-time error highlighting
- [ ] Implement version history browser with timeline view
- [ ] Add parameter comparison side-by-side view
- [ ] Create transmission confirmation dialog with safety warnings
- [ ] Design parameter presets management system
---
### **Step 2.3: Advanced Data Retrieval & Visualization**
#### **Rust Services**
- [ ] Create advanced query system with date range filtering
- [ ] Implement data aggregation functions (min, max, avg, std dev)
- [ ] Add data export functionality: CSV, JSON, MATLAB formats
- [ ] Create mission comparison service for side-by-side analysis
- [ ] Implement data annotation system for marking events
- [ ] Add data preprocessing capabilities (filtering, smoothing)
#### **Svelte UI**
- [ ] Design advanced mission browser with filtering by date/name
- [ ] Create multi-chart dashboard with synchronized time axes
- [ ] Implement chart customization: add/remove sensors, change scales
- [ ] Add data export buttons with format selection
- [ ] Create mission comparison interface with split-screen view
- [ ] Design annotation tools for marking significant events on charts
---
### **Step 2.4: Enhanced Mission Planning**
#### **Rust Services**
- [ ] Implement manual waypoint entry with coordinate validation
- [ ] Create mission template system for common operation patterns
- [ ] Add mission simulation service for validation before execution
- [ ] Implement mission optimization algorithms for efficient paths
- [ ] Create safety constraint checking (minimum depth, no-go zones)
- [ ] Add mission duration estimation based on waypoints
#### **Svelte UI**
- [ ] Design "Add Waypoint" button with manual entry dialog
- [ ] Create coordinate input fields with format validation
- [ ] Implement mission template gallery with preview
- [ ] Add simulation mode toggle with visual feedback
- [ ] Create safety constraint visualization on map (colored zones)
- [ ] Design mission summary panel with duration and distance estimates
---
## **Phase 3: Polish & Production Readiness (Weeks 11-12)**
*Company tab + UI refinements + Error handling*
---
### **Step 3.1: Company Profile & Branding**
#### **Rust Services**
- [ ] Create configuration service for company information
- [ ] Implement logo and asset management system
- [ ] Add contact information validation and storage
- [ ] Create version information service with build details
- [ ] Implement license management system
#### **Svelte UI**
- [ ] Design dedicated Company tab with professional layout
- [ ] Create rich text editor for company description with image support
- [ ] Implement logo upload and display functionality
- [ ] Add contact information section with clickable links
- [ ] Design about screen with version information and license details
- [ ] Create branded loading screens and splash screens
---
### **Step 3.2: Comprehensive Error Handling**
#### **Rust Services**
- [ ] Implement global error handling middleware
- [ ] Create detailed error logging system with rotation
- [ ] Add error categorization: communication, database, validation, system
- [ ] Implement automatic recovery strategies for common failures
- [ ] Create error reporting service with anonymized diagnostics
- [ ] Add user-friendly error messages with actionable solutions
#### **Svelte UI**
- [ ] Design global error boundary component
- [ ] Create error toast notification system with categories
- [ ] Implement detailed error modals with troubleshooting steps
- [ ] Add error logging viewer for technical users
- [ ] Create connection recovery interface with manual retry options
- [ ] Design offline mode indicators and functionality
---
### **Step 3.3: UI/UX Polish & Performance**
#### **Rust Services**
- [ ] Optimize database queries with indexing and caching
- [ ] Implement background processing for heavy operations
- [ ] Add performance monitoring and profiling hooks
- [ ] Create resource cleanup system for memory management
- [ ] Implement lazy loading for large datasets
- [ ] Add compression for data transmission and storage
#### **Svelte UI**
- [ ] Implement smooth animations for transitions and state changes
- [ ] Create responsive design for tablet and mobile form factors
- [ ] Add keyboard shortcuts for power users
- [ ] Design dark mode with submarine-themed color scheme
- [ ] Implement loading skeletons for async operations
- [ ] Create comprehensive user documentation with tooltips
- [ ] Add undo/redo functionality for critical operations
---
### **Step 3.4: Testing & Quality Assurance**
#### **Rust Services**
- [ ] Write unit tests for all core services (serial, database, mission planning)
- [ ] Implement integration tests for end-to-end workflows
- [ ] Create mock hardware interface for testing without submarine
- [ ] Add performance benchmarks for critical paths
- [ ] Implement static code analysis with Clippy and security scans
#### **Svelte UI**
- [ ] Write component tests with Vitest and Svelte Testing Library
- [ ] Create end-to-end tests with Playwright for critical user journeys
- [ ] Implement visual regression testing for UI consistency
- [ ] Add accessibility testing (WCAG compliance)
- [ ] Create performance profiling for UI rendering and interactions
- [ ] Implement user session recording for bug reproduction
---
### **Step 3.5: Deployment & Distribution**
#### **Rust Services**
- [ ] Create platform-specific build scripts for Windows/Linux
- [ ] Implement automatic update system with delta patches
- [ ] Add installation package generation (MSI for Windows, DEB for Linux)
- [ ] Create configuration migration system for version upgrades
- [ ] Implement backup and restore functionality for user data
#### **Svelte UI**
- [ ] Design first-run setup wizard with configuration steps
- [ ] Create user preference management panel
- [ ] Implement theme customization options
- [ ] Add language selection and internationalization support
- [ ] Design update notification system with changelog display
- [ ] Create backup/restore interface with visual progress
---
## **Technical Implementation Notes**
### **Rust Backend Architecture (Tauri v2)**
src-tauri/
├── Cargo.toml # workspace with tauri v2 features
├── tauri.conf.json # v2 permissions, capabilities, mobile opts
├── capabilities/ # fine-grained ACL (v2 style)
│ ├── default.json
│ └── serialport.json
├── src/
│ ├── lib.rs # #[tauri::command] handlers + setup()
│ ├── main.rs # tauri::Builder::default().run()
│ ├── core/
│ │ ├── serial.rs # tokio-serial / futures-codec
│ │ ├── db.rs # sqlx or rusqlite + deadpool
│ │ └── error.rs # thiserror types mapped to tauri::Error
│ ├── commands/ # one file per domain → thin handler layer
│ │ ├── mission_cmd.rs
│ │ ├── telemetry_cmd.rs
│ │ ├── map_cache_cmd.rs
│ │ └── control_cmd.rs
│ ├── services/ # pure Rust logic (no tauri deps)
│ │ ├── mission_planning.rs
│ │ ├── telemetry.rs
│ │ ├── map_cache.rs
│ │ └── control_params.rs
│ ├── models/ # serde Serialize/Deserialize
│ │ ├── mission.rs
│ │ ├── waypoint.rs
│ │ └── telemetry.rs
│ └── utils/
│ ├── platform.rs # Windows/Linux port helpers
│ └── validation.rs
└── migrations/ # SQLx migrate files (if using sqlx)
----------------------------------------------------------
### **Svelte UI Structure (Svelte 5 + SvelteKit v2)**
src/
├── app.html # %sveltekit.head% / %sveltekit.body%
├── app.js # app-wide client setup (tauri plugin init)
├── lib/
│ ├── components/ # .svelte files (Svelte 5 runes)
│ │ ├── ui/ # generic: Button, Toast, Modal …
│ │ ├── telemetry/ # DashboardGrid, SensorCard …
│ │ ├── mission/ # WaypointEditor, MissionMap …
│ │ └── map/ # MapLibreCanvas, CacheDrawer …
│ ├── stores/ # Svelte 5 runes-based state
│ │ ├── serial.s.js # serial connection state
│ │ ├── mission.s.js # current mission + waypoints
│ │ └── settings.s.js # user prefs & company profile
│ ├── tauri/ # typed wrapper around @tauri-apps/api
│ │ ├── mission.ts
│ │ ├── telemetry.ts
│ │ └── db.ts
│ └── styles/
│ ├── submarine.css # TailwindCSS theme extensions
│ └── animations.css
├── routes/ # SvelteKit v2 file-system router
│ ├── +layout.svelte # shell with tabs / titlebar
│ ├── +error.svelte # global error boundary
│ ├── (app)/ # group layout (desktop only)
│ │ ├── dashboard/
│ │ │ └── +page.svelte # real-time telemetry
│ │ ├── planning/
│ │ │ └── +page.svelte # mission builder + map
│ │ ├── data/
│ │ │ └── +page.svelte # history / export
│ │ └── settings/
│ │ └── +page.svelte # serial, cache, params
│ └── company/
│ └── +page.svelte # branded info & licences
├── hooks.client.js # sentry, tauri event listeners
└── service-worker.js # optional offline PWA layer
### **Critical Dependencies**
- **Rust**: `serialport`, `rusqlite`, `serde`, `geo`, `tauri`, `tokio`
- **Svelte**: `svelte-kit`, `maplibre-gl`, `chart.js`, `tailwindcss`, `tauri`
- **System**: SQLite3, MapLibre GL native dependencies
This backlog provides a complete, granular roadmap for the MVP development with clear separation between Rust backend services and Svelte frontend components, ensuring parallel development while maintaining architectural integrity.
