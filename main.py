import time
import yaml

from anki_connector.anki_starter import AnkiStarter
from anki_connector.anki_connector import AnkiConnector

if __name__ == "__main__":
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    anki_starter = AnkiStarter(config["anki_connect_url"])
    anki_starter.run_anki()

    anki_connector = AnkiConnector(config["anki_connect_url"])
    selected_deck = anki_connector.set_used_deck()
    print(f"Using collection: {selected_deck}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        anki_starter.close()

