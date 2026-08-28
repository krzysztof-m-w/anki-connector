from unittest.mock import patch

from anki_connector.anki_connector import AnkiConnector
from main import strip_html_from_text


def test_set_used_deck_prompts_for_valid_choice():
    connector = AnkiConnector("http://127.0.0.1:8765")

    with patch.object(
        connector,
        "_get_all_collections",
        return_value=["Default", "My Deck", "Another Deck"],
    ), patch("builtins.input", side_effect=["2"]):
        connector.set_used_deck()

    assert connector.used_deck == "My Deck"


def test_select_n_hardest_cards_excludes_tags_and_ranks_difficulty():
    connector = AnkiConnector("http://127.0.0.1:8765")
    connector.used_deck = "My Deck"
    cards = [
        {"cardId": 1, "note": 11, "lapses": 1, "factor": 2200, "due": 1},
        {"cardId": 2, "note": 12, "lapses": 4, "factor": 1600, "due": 1},
        {"cardId": 3, "note": 13, "lapses": 8, "factor": 1300, "due": 1},
    ]

    with patch.object(
        connector,
        "_invoke",
        side_effect=[
            [1, 2, 3],
            cards,
            {
                "1": [{"ease": 3, "time": 1000}],
                "2": [{"ease": 1, "time": 5000}],
                "3": [{"ease": 1, "time": 10000}],
            },
            [
                {"noteId": 11, "tags": []},
                {"noteId": 12, "tags": ["exclude"]},
                {"noteId": 13, "tags": []},
            ],
        ],
    ) as invoke:
        selected = connector.select_n_hardest_cards(2, ["exclude"])

    assert [card["cardId"] for card in selected] == [3, 1]
    assert invoke.call_args_list[0].args == ("findCards",)


def test_strip_html_from_text_removes_image_tags_and_br_tags():
    assert strip_html_from_text('twarz<br><img src="16581476231134244510212291238504.jpg">') == 'twarz'
    assert strip_html_from_text('odnosić się(do czegoś)<img src="img3353599855883410958.jpg"><br>') == 'odnosić się(do czegoś)'
