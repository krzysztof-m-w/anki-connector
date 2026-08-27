# Anki Connector

A small launcher that starts Anki, waits for AnkiConnect, and keeps Anki running in the background.

## Setup phases

1. **Automatic Anki installation**
   Install Anki automatically as part of the project setup, or ensure the `anki` command is available on `PATH`.

2. **Install AnkiConnect**
   AnkiConnect is required. Install the AnkiConnect add-on in Anki and restart Anki so the API is available at `http://127.0.0.1:8765`.

3. **Optional window control**
   Install `xdotool` if available. It is optional but recommended: the connector uses it to minimize Anki after startup. Window control may be limited on Wayland.

## Run

```bash
python3 main.py
```

Press `Ctrl+C` to stop the connector and close the Anki process it started.
