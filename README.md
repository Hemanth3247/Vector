# VECTOR Rocketry — Avionics, CAD & Documentation
Zenith Club · Indian Institute of Technology Ropar

VECTOR is the student rocketry team at IIT Ropar. This repository contains the avionics firmware and drivers (MicroPython), CAD designs, documentation and media used for the design, testing and development of experimental sounding rockets.

---

## Contents (high level)
- Avionics_Codes/  
  - Micropython/ — MicroPython drivers, examples and a top-level main.py to run on a MicroPython-capable board  
  - Logic/ — block diagrams, logic image and supporting HTML visualizations  
- CAD_Designs/ — CAD models and versions (mechanical parts, assemblies)  
- Documentation/ — design notes, reports, presentations (design rationale, test reports)  
- Media/ — photos, renders, videos and test footage  

---

## Features
- MicroPython drivers for common sensors used in rocketry:
  - MPU6500 (IMU) — Avionics_Codes/Micropython/MPU6500
  - MS5611 (barometric altimeter) — Avionics_Codes/Micropython/MS5611
  - OV7670 (camera) — Avionics_Codes/Micropython/OV7670
  - SD card read/write helpers — Avionics_Codes/Micropython/SDCard
- Example mains for each sensor and a top-level orchestrator main.py that integrates components
- CAD files grouped by version for mechanical iteration tracking
- Documentation and media to support design reviews and presentations

---

## Quick start (hardware)
Prerequisites:
- A MicroPython-capable board (ESP32, Pyboard, or similar) with the appropriate pinout and enough GPIOs for the chosen sensors.
- A host machine with a MicroPython transfer tool (mpremote, ampy, rshell, or Thonny).
- Wiring for I2C/SPI/parallel as required by each module — see the driver source for pin names and expected interfaces.

1. Flash MicroPython on your board (follow board-specific instructions).
2. Copy the MicroPython code to the board (example using mpremote; adapt if you use another tool):
   ```bash
   mpremote connect /dev/ttyUSB0 fs put -r Avionics_Codes/Micropython
   ```
3. Connect serial and run the example main:
   ```bash
   mpremote connect /dev/ttyUSB0 run main.py
   ```
4. To test a specific sensor, run its example:
   - IMU: `Avionics_Codes/Micropython/MPU6500/main.py`
   - Barometer: `Avionics_Codes/Micropython/MS5611/main.py`
   - Camera: `Avionics_Codes/Micropython/OV7670/main.py`

Notes:
- Pin assignments are in the driver/example files (open the .py files to adapt to your board).
- Use level shifters where necessary when interfacing 3.3V vs 5V parts.

---

## Developer notes
- Driver locations:
  - MPU6500: `Avionics_Codes/Micropython/MPU6500/MPU6500_Driver.py`
  - MS5611: `Avionics_Codes/Micropython/MS5611/MS5611_Driver.py`
  - OV7670: `Avionics_Codes/Micropython/OV7670/OV7670_Driver.py` and `OV7670_Wrapper.py`
  - SD card: `Avionics_Codes/Micropython/SDCard/sdcard.py` and `SDCard_Driver.py`
- The top-level `Avionics_Codes/Micropython/main.py` coordinates start-up and logging — use it as the base for flight firmware.
- Logic and diagrams are in `Avionics_Codes/Logic/` (e.g., Logic.png and an HTML export) — include these in reports and presentations.
- CAD versions are kept in `CAD_Designs/version1` and `version2`.

---

## Testing & validation suggestions
- Bench test each sensor separately before integrating.
- Use the SDCard example to validate logging and file-system behavior.
- Validate timing and memory usage on the actual board (camera capture can be memory- and CPU-heavy).
- If possible, create a small ground-station script (serial or Wi-Fi) to capture telemetry in real time.

---

## Contributing
We welcome contributions from teammates and external collaborators.
- Fork -> branch -> PR with clear description and test steps.
- Label PRs as `bug`, `feature`, `docs`, or `hardware`.
- Include wiring diagrams and test logs for hardware changes.

---

## License
(Replace this line with your chosen license.) Suggested: MIT or CC-BY for non-software assets.

---

## Contact
VECTOR · Zenith Club, IIT Ropar  
Repository owner: Hemanth3247 (GitHub)  
For questions / instrumentation details, open an issue or submit a PR with `docs/` updates.
