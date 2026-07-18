# JobHunter Launcher

A native macOS launcher for the **JobHunter** ecosystem.

The launcher provides a single interface to start and stop all required services without opening multiple terminals or manually running commands.

---

## Features

- Start Docker Desktop
- Start the JobHunter Docker container
- Launch the Search API (FastAPI) in the background
- Launch the Auto Applier in a dedicated Terminal window
- Stop all JobHunter services with a single click
- Native macOS application built using Automator and AppleScript

---

## Project Structure

```text
macOS_Launcher/
├── JobHunter.applescript
├── launch.sh
├── stop.sh
├── run_applier.sh
└── README.md
```

---

## Components

### launch.sh

Responsible for launching the backend services.

It performs the following actions:

- Starts Docker Desktop
- Waits until the Docker Engine is ready
- Starts the `job-hunter-ai` container
- Starts the FastAPI Search API

---

### run_applier.sh

Starts the Auto Applier.

Actions:

- Opens the project directory
- Activates the Python virtual environment
- Executes

```bash
python3 mac.py
```

The Auto Applier is intentionally launched in a Terminal window so that logs and browser automation remain visible.

---

### stop.sh

Stops every running JobHunter component.

Actions:

- Stops FastAPI
- Stops the Auto Applier
- Stops the Docker container
- Stops Docker Desktop

---

## Requirements

- macOS
- Docker Desktop
- Python 3
- zsh
- Automator

---

## Folder Layout

Expected project structure:

```text
JobHunter/
│
├── auto-applier/
├── search-scraper/
├── database/
├── workflows/
├── macOS_Launcher/
│   ├── launch.sh
│   ├── stop.sh
│   ├── run_applier.sh
│   └── JobHunter.applescript
```

---

## Installation

Clone the repository.

Make the launcher scripts executable.

```bash
chmod +x launch.sh
chmod +x stop.sh
chmod +x run_applier.sh
```

---

## Creating the macOS Application

1. Open **Automator**
2. Create a new **Application**
3. Add a **Run AppleScript** action
4. Copy the contents of `JobHunter.applescript`
5. Save the application as

```text
JobHunter.app
```

You can now:

- Place it inside `/Applications`
- Add it to the Dock
- Launch JobHunter with a single click

---

## Usage

### Launch JobHunter

Starts:

- Docker Desktop
- JobHunter Docker container
- Search API (FastAPI)

---

### Run Auto Applier

Launches the Auto Applier inside a Terminal window using the project's virtual environment.

---

### Stop JobHunter

Gracefully shuts down:

- Search API
- Auto Applier
- Docker container
- Docker Desktop

---

## Customization

If your project lives in a different location, update the paths inside:

- `launch.sh`
- `run_applier.sh`
- `stop.sh`
- `JobHunter.applescript`

to match your local directory structure.

---

## Notes

The launcher is designed specifically for the JobHunter workflow and assumes:

- Docker Desktop is installed.
- Python virtual environments are already created.
- Required Docker containers already exist.
- The Search API uses Uvicorn.
- The Auto Applier entry point is `mac.py`.

---

## License

Part of the JobHunter project.