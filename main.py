import yaml

from anki_connector.anki_starter import AnkiStarter
from anki_connector.anki_connector import AnkiConnector
from action_handlers.story_handler import handle_story_action


if __name__ == "__main__":
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)

    anki_starter = AnkiStarter(config["anki_connect_url"])
    anki_starter.run_anki()

    anki_connector = AnkiConnector(config["anki_connect_url"])
    selected_deck = anki_connector.set_used_deck()
    print(f"Using collection: {selected_deck}")

    available_actions = ["story", "exit"]
    selected_action = None

    try:
        while selected_action != "exit":
            selected_action = input(f"Select action [{', '.join(available_actions)}]: ").strip().lower()
            if selected_action not in available_actions:
                print(f"Invalid action.")
                continue
            if selected_action == "story":
                handle_story_action(anki_connector)
               
    except KeyboardInterrupt:
        anki_starter.close()

