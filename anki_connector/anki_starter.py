import subprocess
import time

import requests


ANKI_CONNECT_URL = "http://127.0.0.1:8765"


class AnkiStarter:
    def __init__(self):
        self._anki_process = None

    @staticmethod
    def is_anki_connect_available(timeout=2):
        payload = {"action": "version", "version": 6}

        try:
            response = requests.post(ANKI_CONNECT_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get("error") is None
        except (requests.RequestException, ValueError):
            return False

    def run_anki(self, startup_timeout=15):
        if self._anki_process is None or self._anki_process.poll() is not None:
            self._anki_process = subprocess.Popen(
                ["anki"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        deadline = time.monotonic() + startup_timeout
        while time.monotonic() < deadline:
            if self.is_anki_connect_available():
                return
            if self._anki_process.poll() is not None:
                break
            time.sleep(0.5)

        self.close()
        raise RuntimeError("AnkiConnect is not available. Please ensure Anki is running and AnkiConnect is installed.")

    def close(self):
        if self._anki_process is not None and self._anki_process.poll() is None:
            self._anki_process.terminate()
            self._anki_process.wait()
        self._anki_process = None

    def __del__(self):
        self.close()



