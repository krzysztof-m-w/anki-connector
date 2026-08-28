from unittest.mock import MagicMock, patch

from action_handlers.story_handler import handle_story_action


def test_handle_story_action_adds_valid_tag_to_all_notes():
    connector = MagicMock()
    connector.select_n_hardest_cards.return_value = [
        {
            "note": 101,
            "fields": {
                "Przód": {"value": "twarz<br><img src=\"1.jpg\">"},
                "Tył": {"value": "das Gesicht"},
            },
        },
        {
            "note": 202,
            "fields": {
                "Przód": {"value": "haus<img src=\"2.jpg\"><br>"},
                "Tył": {"value": "das Haus"},
            },
        },
    ]

    with patch("builtins.input", side_effect=["yes"]), patch(
        "action_handlers.story_handler.time.strftime",
        return_value="2026-08-27_12-00-00",
    ):
        handle_story_action(connector)

    connector._invoke.assert_called_once_with(
        "addTags",
        notes=[101, 202],
        tags="used_in_story_2026-08-27_12-00-00",
    )
