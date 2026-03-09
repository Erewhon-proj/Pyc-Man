# Pyc-Man

A Pac-Man clone built with Python and Pygame that features a complete game loop with progressive levels and dynamic scoring.

## What makes this different

This isn't just a basic Pac-Man clone. **We** designed it around the idea of replayability through a proper progression system. As you advance
through levels, the game gets harder but also rewards you with higher scores. This creates a natural high-score competition where skilled
players can distinguish themselves.

The difficulty scales intelligently - ghosts get faster, their AI becomes more aggressive, and your power-ups last shorter. But your
points increase proportionally, so taking risks at higher levels pays off.

## Features

* Classic Pac-Man gameplay with all 4 ghosts, each with unique AI behavior
* Progressive difficulty system that adjusts multiple parameters per level
* Dynamic scoring multiplier (up to 50% bonus at higher levels)
* High-score tracking system with persistent storage
* Complete game loop with pause functionality
* Ghost AI modes (SCATTER/CHASE) that evolve with difficulty

## How to play

Install dependencies:

```bash
pip install -r requirements.txt

```

Run the game:

```bash
python -m src.main

```

Controls:

* Arrow keys or WASD to move
* ESC to pause

## Gameplay mechanics

* Eat all pellets to advance to the next level
* Power pellets let you eat ghosts for points
* Each level increases difficulty but also score multiplier
* Extra life every 10,000 points
* Ghosts get released progressively earlier in higher levels

## Technical notes

Built with Python 3.13 and Pygame. The game uses a tile-based map system and implements the classic ghost AI behaviors from the original
Pac-Man.
