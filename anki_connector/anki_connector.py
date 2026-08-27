import requests


class AnkiConnector:
    def __init__(self, anki_connect_url: str):
        self.anki_connect_url = anki_connect_url
        self._used_deck = None

    def _get_all_collections(self):
        payload = {"action": "deckNames", "version": 6}
        response = requests.post(self.anki_connect_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("error") is not None:
            raise RuntimeError(result["error"])

        return result["result"]

    def set_used_deck(self):
        if self._used_deck is not None:
            return self._used_deck

        collections = self._get_all_collections()
        if not collections:
            raise RuntimeError("No collections are available in Anki.")

        for index, collection in enumerate(collections, start=1):
            print(f"{index}. {collection}")

        while True:
            raw_choice = input(f"Select collection to use [1-{len(collections)}]: ").strip()
            try:
                choice = int(raw_choice)
            except ValueError:
                print("Please enter a number from the list.")
                continue

            if 1 <= choice <= len(collections):
                self._used_deck = collections[choice - 1]
                return self._used_deck

            print(f"Please select a number between 1 and {len(collections)}.")

    @property
    def used_deck(self):
        if self._used_deck is None:
            raise RuntimeError("used_deck is not set")
        return self._used_deck

    @used_deck.setter
    def used_deck(self, value):
        if self._used_deck is not None:
            raise RuntimeError("used_deck is already set")
        self._used_deck = value
