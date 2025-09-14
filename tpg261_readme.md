# TPG261 Pfieffer Vacuum Gauge Controller

A Python-based GUI application for interfacing with the Pfieffer TPG261 Single Gauge vacuum pressure controller. This application provides real-time pressure monitoring, data logging, and calibration management through an intuitive graphical interface.

## Features

- **Real-time Pressure Monitoring**: Continuous pressure readings with customizable update intervals
- **Interactive Plotting**: Live pressure vs. time plots with multiple view options (full range, time window, logarithmic scale)
- **Data Logging**: Automatic timestamped data collection and saving capabilities
- **Calibration Management**: Easy adjustment of calibration factors for both sensor channels
- **Multi-Controller Synchronization**: Built-in clock synchronization system for coordinated operation with other instruments
- **User-friendly GUI**: Tkinter-based interface with organized sections for monitoring and control

## Requirements

### Hardware
- Pfieffer TPG261 Single Gauge vacuum controller
- Serial/USB connection to the controller

### Software Dependencies
```
numpy
matplotlib
tkinter (usually included with Python)
pyserial
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/tpg261-controller.git
cd tpg261-controller
```

2. Install required dependencies:
```bash
pip install numpy matplotlib pyserial
```

3. Configure the COM port in the main script:
```python
ports['TPG261'] = 'COM23'  # Update with your actual port
```

## Usage

### Basic Operation

1. Connect your TPG261 controller to your computer via serial/USB
2. Update the COM port in the script to match your connection
3. Run the main application:
```bash
python cont_TPG261_Single_Pfieffer_Gauge_V3.py
```

### GUI Components

#### Real-time Plot
- **Full Time**: Display complete measurement history
- **Delta T**: Show data from the last N minutes (configurable: 1-60 minutes)
- **Log10**: Logarithmic y-axis scaling for wide pressure ranges

#### Current State Panel
- **Pressure**: Live pressure reading in Torr
- **State**: Current sensor status (Passed, Underrange, Overrange, etc.)
- **Sensor Information**: Connected sensor types for both channels
- **Calibration Factors**: View and modify calibration settings

#### Control Features
- **Clock Display**: Shows elapsed measurement time
- **Data Point Counter**: Tracks number of recorded measurements
- **Quit Button**: Safely closes connections and saves data

### Calibration Management

The application allows real-time adjustment of calibration factors:
1. Enter new calibration values in the respective fields
2. Press Enter or click elsewhere to apply changes
3. Changes are immediately sent to the controller

### Data Saving

Data is automatically saved when the application closes, including:
- Absolute timestamps
- Relative time (minutes from start)
- Pressure readings
- Sensor states

Files are saved with timestamp format: `YYYY_MM_DD-HH_MM_SS_TPG261_pressure_controller.npy`

## File Structure

### `cont_TPG261_Single_Pfieffer_Gauge_V3.py`
Main application file containing:
- `TPG261_GUI`: GUI class managing the user interface
- `Data_Structure_TPG261`: Data management and storage class
- Main loop and event handling
- Multi-controller synchronization system

### `mod_Pfieffer_TPG261.py`
Hardware interface module featuring:
- `pfieffer_single_gauge_TPG261`: Serial communication class
- Command protocol implementation
- Error handling and status reporting
- Configuration methods (units, filters, resolution)

## Communication Protocol

The application uses the Pfieffer serial protocol with standard control characters:
- **CR/LF**: Command termination
- **ACK/NAK**: Acknowledgment handling
- **ENQ**: Data request
- **ETX**: End of transmission

### Supported Commands
- `PR1`/`PR2`: Read pressure from gauge 1/2
- `TID`: Get gauge type information
- `CAL`: Set/get calibration factors
- `UNI`: Set measurement units
- `FIL`: Configure filter settings
- `DCD`: Set display resolution

## Multi-Controller Synchronization

The application includes a synchronization system for coordinating multiple instrument controllers:

1. Creates a signal file when ready
2. Waits for other controllers to signal readiness
3. Synchronizes start times across all instruments

Expected controllers:
- Substrate_Heater_Controller
- TPG261_Controller
- MKS_Pressure_Controller
- BKP_Arb_Waveform_Controller
- Ircon_Modline_Plus_Controller

## Error Handling

The application handles common error conditions:
- **Serial Communication Errors**: Connection timeouts and protocol violations
- **Sensor Status**: Underrange, overrange, sensor errors, and disconnection
- **Data Validation**: Invalid calibration values and parameter ranges

## Configuration Options

### Plot Settings
- Update interval: 200ms (5 Hz)
- Default figure size: 5" × 3"
- Line styles and colors customizable via matplotlib rcParams

### Serial Settings
- Baud rate: 9600
- Data bits: 8
- Parity: None
- Stop bits: 1
- Timeout: 1 second

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Kenneth Shepherd Jr

## Version History

- **V3 (2025-01-15)**: Added multi-controller clock synchronization
- **V2**: Enhanced GUI and data management features
- **V1**: Initial implementation with basic functionality

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository or contact the author.

## Acknowledgments

- Pfieffer Vacuum for TPG261 documentation and protocol specifications
- Python community for excellent scientific computing libraries