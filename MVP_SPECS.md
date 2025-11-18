# MVP Ground Control Platform Requirements - Submarine Operations
## Core System Overview
**Target Vehicle**: Submarines
**Communication Protocol**: Serial Port (RS-232/USB)
**MVP Focus**: Essential mission planning, real-time monitoring, and data management capabilities
---
## Essential Features
### 1. Serial Communication Module
- **Requirement**: Establish bidirectional serial communication between ground control station and submarine hardware
- **Specifications**:
- Data format must match provided hardware specifications exactly
- Baud rate/configurable serial parameters
- Real-time data streaming capability
### 2. Mission Planning Interface
- **Map-Based Waypoint Addition**:
- Click anywhere on map to create waypoint
- Auto-capture geographic coordinates (latitude/longitude)
- Form popup for mission parameters (depth, duration, actions, etc.)

- **Manual Waypoint Entry**:
- "Add Waypoint" button for manual coordinate entry
- Form fields for all mission parameters
- Validation for coordinate ranges and parameter limits
### 3. Data Management System
- **Real-Time Data Acquisition**:
- Configurable sampling rate: 0.5 to 10 seconds (user-adjustable)
- Continuous data streaming from submarine sensors

- **Database Structure**:
- **Mission Files Table**: mission_name, creation_datetime, description
- **Mission Data Table**: foreign key to mission files, timestamp, sensor_data
- **Control Parameters Table**: 6 float coefficients with versioning
- **Data Retrieval**:
- Mission file browser with filtering by date/name
- One-click mission data visualization
- Export capability for analysis
### 4. Offline Map Caching
- **Cache Management**:
- Save maps with: unique_name, zoom_level, center_coordinates
- Duplicate prevention system (hash-based checking)
- Offline availability indicator

- **User Experience**:
- Cache management panel
- Quick selection of cached maps at startup
- Visual indication of cached vs. online maps
### 5. Control Parameters Management
- **Storage**: 6 floating-point control coefficients
- **Operations**: Save, load, version history
- **Security**: Parameter validation before transmission to submarine
### 6. Company Profile Tab
- **Content**: Static company information, logo, contact details
- **Format**: Rich text with image support
- **Access**: Dedicated tab in main interface
---
## MVP Prioritization
**Phase 1 (Core)**: Serial communication + Mission planning + Basic data storage
**Phase 2 (Enhanced)**: Map caching + Control parameters + Advanced data retrieval
**Phase 3 (Polish)**: Company tab + UI refinements + Error handling
## Technical Constraints
- Platform: Windows/Linux compatible
- Database: SQLite (lightweight, file-based)
- Map Engine: OpenLayers/Leaflet with offline support
- Serial Library: Platform-independent serial communication library
- UI Framework: Qt or Electron for cross-platform support
This MVP specification focuses on submarine-specific requirements while maintaining a clean, modular architecture for future expansion.
