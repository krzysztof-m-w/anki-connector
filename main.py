import time

from anki_connector.anki_starter import AnkiStarter

if __name__ == "__main__":
    anki_starter = AnkiStarter()
    anki_starter.run_anki()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        anki_starter.close()