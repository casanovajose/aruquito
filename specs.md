Specification: Agnostic ArUco MIDI Bridge (v2.0)
1. Project Overview

A serverless, browser-based application designed to track up to 32 physical fiducial markers (ArUco) via webcam and translate their spatial data into MIDI Control Change (CC) messages. The system is designed to interface directly with Purr Data or any MIDI-capable software without intermediate servers.
2. Technical Stack

    Vision Engine: OpenCV.js (using DICT_4X4_50 for high performance).

    Communication: Web MIDI API (Native browser support).

    Frontend: HTML5, CSS3, and Vanilla JavaScript (ES6+).

    Asset Generation: Canvas-to-DataURL (PNG) for robust printing.

3. Vision & Processing Pipeline
3.1 Camera Integration

    Unified Resolution: Selection between 640×480 (Performance) and 1280×720 (Precision).

    Synchronization: Detection and HUD overlay use the same pixel grid to ensure 1:1 visual accuracy.

    Mirroring: Visuals are mirrored for natural interaction, but coordinate math is corrected to maintain spatial logic.

3.2 Detection Logic

    Fiducial Type: ArUco 4x4 squares (IDs 0–31).

    Dead-Zoning (DZ): Individualized pixel-change threshold per marker to filter camera sensor noise and prevent MIDI data floods.

    Calibration (Zeroing): Relative coordinate system. Users can "Zero" a marker, setting its current X,Y, and Rotation as the center reference (64 in MIDI).

4. MIDI Mapping & Data Flow
4.1 Transmission Logic

    Precision: Standard 7-bit MIDI (0 to 127).

    Channel Mapping: Configurable per marker (Default: Channel 1).

    CC Mapping: * Auto-assignment formula: BaseCC=(ID×3)+10

        Manual Override: Users can define a custom BaseCC for any specific ID.

        Parameter Offsets: * X-Position: BaseCC

            Y-Position: BaseCC+1

            Rotation: BaseCC+2

4.2 Data Normalization

Coordinates are mapped from the camera pixel grid to the MIDI range:
ValueMIDI​=clamp((ResolutionPoscurrent​−Poszero​​+0.5)×127,0,127)
5. User Interface (UI) Components
5.1 Main Viewport & HUD

    Signal Indicator: A visual "Signal Light" that turns green when any marker is detected.

    Bounding Boxes: Real-time cyan squares drawn around detected markers with ID labels.

    Loading Overlay: A progress indicator for the OpenCV.js engine initialization (10MB+ payload).

5.2 Sidebar Management

    Camera Selector: Dropdown for available system video devices.

    Global Controls: Marker count (1–32) and Print Size (mm).

    Marker Assignments List: Scrollable list showing every active ID, its MIDI Channel, Base CC, and individual Dead-Zone (DZ) slider.

6. Integrated Print Utility

    Graphic Fidelity: Markers are rendered via OpenCV's native drawMarker logic to ensure 100% compatibility between the printed asset and the tracker.

    Reliability Fix: Canvases are converted to static PNG images before printing to bypass browser "Background Graphics" restrictions.

    Scaling: User-defined size in millimeters (e.g., 35mm) using CSS mm units for physical accuracy.

    Labels: Each printed marker includes its ID and Base CC for physical-to-digital reference.

7. Operational Requirements

    Environment: Must run on an HTTPS connection or localhost for Camera/MIDI permissions.

    Recommended Browsers: Chrome, Edge, or Opera (Native Web MIDI support).

    System Loop: 1.  OpenCV loads → 2. User selects Camera → 3. User generates/prints Markers → 4. Start Engine → 5. Connect to MIDI Target.