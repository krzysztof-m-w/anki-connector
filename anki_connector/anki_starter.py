import subprocess
import shutil
import time

import requests


class AnkiStarter:
    def __init__(self, anki_connect_url: str):
        self._anki_connect_url = anki_connect_url
        self._anki_process = None

    @staticmethod
    def is_anki_connect_available(anki_connect_url: str, timeout=2):
        payload = {"action": "version", "version": 6}

        try:
            response = requests.post(anki_connect_url, json=payload, timeout=timeout)
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
            if self.is_anki_connect_available(self._anki_connect_url):
                self._minimize_window(self._anki_process.pid)
                return
            if self._anki_process.poll() is not None:
                break
            time.sleep(0.5)

        self.close()
        raise RuntimeError("AnkiConnect is not available. Please ensure Anki is running and AnkiConnect is installed.")

    @staticmethod
    def _minimize_window(process_id=None):
        xdotool = shutil.which("xdotool")
        if not xdotool:
            return

        search_terms = []
        if process_id is not None:
            search_terms.append(["--pid", str(process_id)])
        search_terms.extend([["--class", "Anki"], ["--name", "Anki"]])

        for _ in range(20):
            for search_term in search_terms:
                result = subprocess.run(
                    [xdotool, "search", *search_term],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                window_ids = result.stdout.split()
                if window_ids:
                    for window_id in window_ids:
                        subprocess.run(
                            [xdotool, "windowminimize", window_id],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    return
            time.sleep(0.25)

    def close(self):
        if self._anki_process is not None and self._anki_process.poll() is None:
            self._anki_process.terminate()
            self._anki_process.wait()
        self._anki_process = None

    def __del__(self):
        self.close()



