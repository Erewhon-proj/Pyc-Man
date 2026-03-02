"""Module for handling high scores logic and screens."""
# pylint: disable=duplicate-code

import json
import os
import sys
from typing import Dict, List, Union

import pygame

from src.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW

SCORE_FILE = "highscores.json"
MAX_SCORES = 10


def load_high_scores() -> List[Dict[str, Union[str, int]]]:
    """Load scores from json file or if it does not exist return empty list.
    Supports backward compatibility with older saves that only stored integers."""
    if not os.path.exists(SCORE_FILE):
        return []

    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as file:
            scores = json.load(file)

            processed_scores: List[Dict[str, Union[str, int]]] = []
            for s in scores:
                if isinstance(s, int):
                    # Handle legacy integer scores
                    processed_scores.append({"name": "---", "score": s})
                elif isinstance(s, dict):
                    processed_scores.append({
                        "name": str(s.get("name", "---")),
                        "score": int(s.get("score", 0))
                    })

            return sorted(processed_scores, key=lambda x: int(x["score"]), reverse=True)[
                :MAX_SCORES
            ]
    except (json.JSONDecodeError, IOError):
        return []


def input_name_screen(
    screen: pygame.Surface, clock: pygame.time.Clock, score: int
) -> str:
    """Screen to input a 3-letter name for the high score."""
    font_title = pygame.font.Font(None, 60)
    font_input = pygame.font.Font(None, 80)

    name = ""

    while True:
        screen.fill(BLACK)

        # Display title
        title_text = font_title.render(f"NEW HIGH SCORE: {score}", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Display prompt
        prompt_text = font_title.render("ENTER 3 INITIALS:", True, WHITE)
        prompt_rect = prompt_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        )
        screen.blit(prompt_text, prompt_rect)

        # Display typed letters
        name_text = font_input.render(name + "_" * (3 - len(name)), True, YELLOW)
        name_rect = name_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        )
        screen.blit(name_text, name_rect)

        # Display Enter instruction when ready
        instruction_text = font_title.render("PRESS ENTER TO SAVE", True, WHITE)
        instruction_rect = instruction_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        )
        if len(name) == 3:
            screen.blit(instruction_text, instruction_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) == 3:
                    return name
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 3 and event.unicode.isalpha():
                    name += event.unicode.upper()

        pygame.display.flip()
        clock.tick(FPS)

def save_high_score(
    screen: pygame.Surface, clock: pygame.time.Clock, new_score: int
) -> None:
    """Check if score is high enough, get player name, add new score, sort list, save top ten"""
    if new_score <= 0:
        return  # Does not save useless plays

    scores = load_high_scores()

    # Check if the score actually qualifies for the top 10 list
    if len(scores) < MAX_SCORES or new_score > int(scores[-1]["score"]):
        name = input_name_screen(screen, clock, new_score)
        scores.append({"name": name, "score": new_score})

        # Sort from max to min and save top 10
        scores = sorted(scores, key=lambda x: itn(x["score"]), reverse=True)[:MAX_SCORES]

        try:
            with open(SCORE_FILE, "w", encoding="utf-8") as file:
                json.dump(scores, file)
        except IOError as e:
            print(f"Error on high scores saving: {e}")

def _draw_scores(
        screen: pygame.Surface, font_score: pygame.font.Font, scores: List[Dict]
) -> None:
    """Helper function to draw the scores list to the screen."""
    if not scores:
        empty_text = font_score.render("No high score yet!", True, WHITE)
        empty_rect = empty_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        screen.blit(empty_text, empty_rect)
    else:
        for i, score_data in enumerate(scores):
            name = score_data.get("name", "---")
            score = score_data.get("score", 0)

            # Format to align numbers properly
            score_str = f"{i + 1:2}.      {name}      {score}"
            text_surface = font_score.render(score_str, True, WHITE)
            rect = text_surface.get_rect(
                center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 4) + 20 + (i * 40))
            )
            screen.blit(text_surface, rect)

def show_high_scores_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Show top 10 high scores screen"""
    font_title = pygame.font.Font(None, 80)
    font_score = pygame.font.Font(None, 40)
    font_back = pygame.font.Font(None, 50)

    title_text = font_title.render("TOP 10 SCORES", True, YELLOW)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))

    scores = load_high_scores()

    while True:
        screen.fill(BLACK)

        # Back button
        back_text = font_back.render("BACK TO MENU", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return  # goes back to menu

        # Hover effect for back button
        mouse_pos = pygame.mouse.get_pos()
        back_color = YELLOW if back_rect.collidepoint(mouse_pos) else WHITE

        screen.blit(title_text, title_rect)
        screen.blit(font_back.render("BACK TO MENU", True, back_color), back_rect)

        # Show scores
        _draw_scores(screen, font_score, scores)

        pygame.display.flip()
        clock.tick(FPS)
