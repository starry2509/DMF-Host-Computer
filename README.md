# EWOD Control Console

<p align="center">
  <img src="icon/dmf.png" width="96" alt="EWOD logo">
</p>

<p align="center">
  A dedicated controller for glass-substrate drive boards and EWOD digital microfluidic experiments.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt5-desktop-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/Status-lab%20prototype-1877AA?style=flat-square" alt="Status">
</p>

## Overview

This is a PyQt5-based EWOD (Electrowetting-on-Dielectric) control application for serial communication, chip electrode actuation, droplet movement, camera acquisition, PID temperature control, fluorescence measurement, and experiment data management.

## Technical Approach

The application uses a modular desktop architecture that separates the user interface, hardware drivers, experiment logic, visualization, and data services.

```text
PyQt5 Main Window
        |
        +-- Chip Model and Electrode Layout
        +-- Serial Communication Driver
        +-- Camera Acquisition Module
        +-- Temperature and PID Monitoring
        +-- Fluorescence Measurement
        +-- Logger and Experiment Data Manager
```

### Hardware Control

- The chip model loads the electrode layout from CSV data and maintains electrode selection, driving, and pinned states.
- Selected electrode states are converted into a hardware drive bitmap before being sent through the serial driver.
- Manual control supports directional droplet movement, zoom operations, single-electrode actuation, and multi-electrode sequences.
- Automated experiments are represented as editable step tables containing electrode frames, drive times, and camera actions.

### Data Acquisition

- `QTimer` provides periodic sampling for temperature and fluorescence measurements without blocking the GUI thread.
- Temperature channels expose temperature and power curves through `pyqtgraph`, with separate views for each channel.
- Fluorescence data supports two acquisition methods, LED control, real-time plotting, and file export/import.
- Camera acquisition is isolated in its own module and can be enabled or disabled through the application configuration.

### Visualization and Data Management

- `pyqtgraph` is used for responsive real-time plots, grid display, automatic range updates, and full-screen inspection.
- `pandas` and `openpyxl` support experiment and measurement data exchange through CSV and Excel files.
- The logging layer reports hardware status, serial messages, experiment events, and runtime errors in the desktop interface.

## Features

| Module | Capabilities |
| --- | --- |
| Chip electrodes | Select, actuate, pin, and move droplets |
| Serial driver | Scan ports, connect devices, close ports, and send hardware commands |
| Automated operation | Edit, save, load, and execute experiment steps |
| Camera acquisition | Open the camera, capture images, record video, and open a zoomed view |
| Temperature control | Monitor three temperature channels, power curves, and PID parameters |
| Fluorescence detection | Run two sampling methods, control the LED, and save measurement data |
| Logging | Display runtime logs, serial data, and connection errors |

## Run

```bash
python main_windows.py
```

Python 3.10 or newer is recommended. Install the main dependencies with:

```bash
pip install PyQt5 pyqtgraph pandas openpyxl pyserial opencv-python
```

## Build

```bash
pyinstaller build_exe.spec
```

## Project Structure

```text
cam/             Camera module
chip/            Chip model, electrode layout, and chip data
icon/            Application and control icons
logger/          Logging utilities
main_window/     UI construction and shared theme
serial_driver/   Serial communication driver
tools/           Auxiliary tools
utils/           Shared utilities such as resource paths
main_windows.py  Application entry point and business logic
```

## Controls

- Left-click to select one or more electrodes.
- Right-click to actuate a single electrode.
- Hold `Ctrl` while right-clicking to actuate multiple electrodes in sequence.
- Use the manual operation tab for directional movement and zoom controls.
- Double-click plots or the camera view to open a zoomed window; press `Esc` to close it.

## Version

Current interface version: `V2.1.0`
