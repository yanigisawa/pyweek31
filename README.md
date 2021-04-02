# pyweek31

## PIT Stop

This is an entry for PyWeek 31.

### Dependencies

Code runs on PyGame using PyMunk for physics rendering.

I use `pipenv` for installation and management of the virtualenv:

```
pipenv shell
pipenv install
python ./run_game.py
```

I've tested the code using Python 3.7. I've also included a `requirements.txt` file so the following should also work:

```
python -m venv pit_stop
source ./pit_stop/bin/activate
python -m pip install -r requirements.txt
```

## Controls

WASD or arrow keys for movement.

`W` or `Up` increase your velocity (0-10)

`S` or `Down` decrease your velocity (0-10)

`Spacebar` to come to a complete stop

`R` will reset the game and start the red car in a new random location

`Esc` will quit the game

## Gameplay

The goal of the game is to perform a [PIT Manuever](https://en.wikipedia.org/wiki/PIT_maneuver) on the red car. Move your cop car close to the rear quarter
of the red card and attempt to spin the car to an angle of at least 45 degress in either direction. You win by getting greater than 45 degress, and lose if it is anything less.

## Known Issues

My code for calculating the relative velocity between the cars is very buggy. You can see this at various lower speeds just after the collision. My code is attempting to adjust for player movements and recalculate the relative velocity between the player and enemy car. However the results can sometimes be seen that the cars will "crawl" across the screen as if they are still moving.

## Attributions

### pygame_functions

Documentation at www.github.com/stevepaget/pygame_functions

### Sounds

`musicmasta1` from: https://freesound.org/people/musicmasta1/sounds/131385/

`MarlonHj` - https://freesound.org/people/MarlonHJ/sounds/242739/

### Artwork

https://opengameart.org/content/police-cars

https://opengameart.org/content/car-racer

https://opengameart.org/content/free-urban-textures-ground-grass-road-cobbles-snow?page=1

https://opengameart.org/content/play-pause-mute-and-unmute-buttons
