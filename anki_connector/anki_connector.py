import time

import requests


class AnkiConnector:
    def __init__(self, anki_connect_url: str):
        self.anki_connect_url = anki_connect_url
        self._used_deck = None

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

    def select_n_hardest_cards(self, n, exclusion_tags: list[str]):
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return []

        card_ids = self._invoke("findCards", query=f'deck:"{self.used_deck}"')
        if not card_ids:
            return []

        cards = self._invoke("cardsInfo", cards=card_ids)
        reviews_by_card = self._invoke("getReviewsOfCards", cards=card_ids)
        note_ids = list({card["note"] for card in cards})
        notes = self._invoke("notesInfo", notes=note_ids)
        excluded = set(exclusion_tags)
        notes_by_id = {note["noteId"]: note for note in notes}

        eligible_cards = [
            card
            for card in cards
            if not excluded.intersection(notes_by_id.get(card["note"], {}).get("tags", []))
        ]
        if not eligible_cards:
            return []

        today = int(time.time() // 86400)
        max_lapses = max(card.get("lapses", 0) for card in eligible_cards)
        review_stats = {}
        for card in eligible_cards:
            reviews = reviews_by_card.get(str(card["cardId"]), [])
            review_stats[card["cardId"]] = {
                "failures": sum(review.get("ease") == 1 for review in reviews),
                "time": sum(review.get("time", 0) for review in reviews),
            }
        max_failures = max(stats["failures"] for stats in review_stats.values())
        max_review_time = max(stats["time"] for stats in review_stats.values())
        max_overdue = max(
            max(0, today - card.get("due", today)) for card in eligible_cards
        )
        min_factor = min(card.get("factor", 0) for card in eligible_cards)
        max_factor = max(card.get("factor", 0) for card in eligible_cards)

        def difficulty(card):
            lapses = card.get("lapses", 0) / max_lapses if max_lapses else 0
            stats = review_stats[card["cardId"]]
            failures = stats["failures"] / max_failures if max_failures else 0
            review_time = (
                stats["time"] / max_review_time if max_review_time else 0
            )
            overdue = max(0, today - card.get("due", today))
            overdue_score = overdue / max_overdue if max_overdue else 0
            factor_range = max_factor - min_factor
            ease_score = (
                (max_factor - card.get("factor", max_factor)) / factor_range
                if factor_range
                else 0
            )
            return lapses + ease_score + failures + review_time + overdue_score

        eligible_cards.sort(key=difficulty, reverse=True)
        return eligible_cards[:n]

    def _invoke(self, action, **params):
        payload = {"action": action, "version": 6, "params": params}
        response = requests.post(self.anki_connect_url, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get("error") is not None:
            raise RuntimeError(result["error"])
        return result["result"]
