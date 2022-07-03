# Devman Spaceship

A console game featuring a spaceship firing at various garbage on the Earth's orbit. It's written as an educational project for an async Python course on [dvmn.org](https://dvmn.org/)

## Getting Started

The project runs on Python 3.10 and doesn't use any side libraries.

To launch the game, run `main.py` from the project directory:

```
python3 main.py
```

If you want to see garbage in debug mode (i.e. program will draw their frame borders), uncomment the following line in `main.py`:
```
# coroutines.append(show_obstacles(canvas, obstacles))  # for debug
```