from unittest.mock import patch

from anki_connector.anki_connector import AnkiConnector


def test_set_used_deck_prompts_for_valid_choice():
    connector = AnkiConnector("http://127.0.0.1:8765")

    with patch.object(
        connector,
        "_get_all_collections",
        return_value=["Default", "My Deck", "Another Deck"],
    ), patch("builtins.input", side_effect=["2"]):
        connector.set_used_deck()

    assert connector.used_deck == "My Deck"
