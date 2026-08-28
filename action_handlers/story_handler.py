import random
import re
import time

from anki_connector.anki_connector import AnkiConnector

def strip_html_from_text(value):
    if not isinstance(value, str):
        return value

    value = re.sub(r"<br\s*/?>", "", value, flags=re.IGNORECASE)
    value = re.sub(r"<img\b[^>]*>", "", value, flags=re.IGNORECASE)
    value = re.sub(r"<.*?>", "", value)
    return value.strip()


def handle_story_action(anki_connector: AnkiConnector, exclude_n_days: int = 7):
    tags_to_exclude = [f"action_story_{time.strftime('%Y-%m-%d', time.localtime(time.time() - i * 86400))}" for i in range(exclude_n_days)]
    hardest_cards = anki_connector.select_n_hardest_cards(20, tags_to_exclude)
    hardest_selected_cards = random.sample(hardest_cards, min(5, len(hardest_cards))) if hardest_cards else []
    formatted_cards = "\n".join(
        [
            f"Front: {strip_html_from_text(card['fields']['Przód']['value'])}, Back: {strip_html_from_text(card['fields']['Tył']['value'])}"
            for card in hardest_selected_cards
        ]
    )
    prompt = "Prepare a short story in the target language that will include phrases from the following" \
    "set of flashcards. The language is the one from the back side of the flashcards." \
    "Some of the cards may contain additional exemplary sentences placed after the learned phrase." \
    "**DO NOT** include the exemplary sentences in the story. You can use the sentences as the guideline for " \
    "the context in which the phrase is used (e.g when it has multiple meanings), but try to invent your own, new " \
    "and original story. **ONLY IF** there is no distinct phrase but a single sentence on both sides of the card, " \
    "you may assume that the sentence is the target phrase and should be used in the story."
    prompt += f"\n\n{formatted_cards}\n\n"
    prompt += "The story should be engaging and contextually relevant to the phrases provided."
    print("=" * 80)
    print(prompt)
    print("=" * 80)

    response = None
    while response not in ["yes", "no"]:
        response = input("Do you want to tag the cards as used? (yes/no): ").strip().lower()

    if response == "yes":
        timestamp = time.strftime("%Y-%m-%d", time.localtime())
        note_ids = [card["note"] for card in hardest_selected_cards]
        tag = "action_story_" + timestamp
        if note_ids:
            anki_connector._invoke(
                "addTags",
                notes=note_ids,
                tags=tag,
            )
        print(f"Cards have been tagged as '{tag}'.")