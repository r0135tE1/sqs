# Building Block View

## Level 1: Overall System

![White Box Overall System](chapter5-7Pics/building_block_view/chap-5-level-1.svg)

| Building Block | Description |
|----------|-------------|
| **Player** | Signs up/Login into application. Plays the game. Accesses public endpoints provided by **Fun With Flags** |
| **Fun With Flags** | Includes the game, highscores and public endpoints |
| **Pulbic API** | Provides a public endpoint the application can access. In our case it's *restcountiers.com* |

## Level 2: Fun With Flags Whitebox

![Level 2](chapter5-7Pics/building_block_view/chap-5-level-2.svg)

| Building Block | Description |
| ---------- | ------------- |
| **Frontend** | Web View facing the user. Shows a random country's flag and asks the user to guess the country's name. Guessing correctly will increase a user's score. Requests and receives data from the Fun with Flags Backend REST API. |
| **Backend** | Responds to API calls from the Frontend. Reads/Writes data to the Persistence Component. Requests data from the Public API |
| **Persistence** | Stores user information and high scores |

