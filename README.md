# pySMASH

## Description

pySMASH is a Python-based application developed with Tkinter. It automates clicking sequences based on user-defined coordinates and settings. The application allows users to capture click coordinates, configure settings for automated clicking, and save/load these configurations.

## Features

- Capture and store multiple sets of click coordinates.
- Configure sleep times and iteration counts.
- Save and load configuration settings.
- Random and sequential click sequence modes.
- User-friendly GUI with Tkinter.

## Installation

To install pySMASH, you need to have Python installed on your machine. Clone this repository, and install the required packages:

```bash
git clone https://github.com/your-username/pySMASH.git
cd pySMASH
pip install -r requirements.txt
```

## Usage

Run `main.py` to start the application:

```bash
python main.py
```

## Functionality

- Capture Clicks: Record click coordinates on your screen.
- Start Clicking: Start the automated clicking process based on captured coordinates and configurations.
- Save Config/Load Config: Save your current configurations to a file or load from a saved file.
- Random Order: Choose to execute clicks in a random order or sequentially.
- Keyboard Shortcuts
- Esc Key: Stop the automated clicking sequence at any time.
- Building an Executable
- You can create a standalone executable using PyInstaller:

```bash
pyinstaller --onefile --windowed main.py
```

## Requirements

For a full list of dependencies, see requirements.txt. Key dependencies include:

- Tkinter
- PyAutoGUI
- pynput
- json

## License

- MIT License

## Contributing

Contributions to pySMASH are welcome. Please ensure to update tests as appropriate.

## Acknowledgments

Project inspired by the need for simple automation testing within other GUI apps.
Thanks to the Python and Tkinter communities for the invaluable resources.

## Contact

For any questions or contributions, please contact Dewmrik at dewmrik@ibkc.gg.
