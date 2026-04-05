# Building Block View

## Level 1: Whitebox Overall System

![White Box Overall System](chapter5-7Pics/building_block_view/chap-5-level-1.svg)

| Building Block | Description |
|----------|-------------|
| **Player** | Signs up/Login into application. Plays the game. Accesses public endpoints provided by **Fun With Flags** |
| **Fun With Flags** | Includes the game, highscores and public endpoints |
| **Pulbic API** | Provides a public endpoint the application can access |


### Fun With Flags Web-App 
Implements the flag guessing game for the user and makes calls to the countries API*

### RESTCountries API
External service responding to calls, providing data about countries (i.e. names, flag pngs)*

---

## Level 2
![Level 2](chapter5-7Pics/building_block_view/buildingblock_level1.svg)

### Fun With Flags Frontend
Web View facing the user. Shows a random country's flag and asks the user to guess the country's name. Guessing correctly will increase a user's score. Requests and receives data from the Fun with Flags Backend REST API.

### Fun With Flags Backend
Responds to API calls from the Frontend. Reads/Writes data to the Fun With Flags Database. Requests and receives data from the Countries API.

### Fun With Flags DB
Relational Database storing user information i.e. name, login data and game scores.

### RESTCountries API
External service responding to backend calls, providing data about countries (i.e. names, flag pngs)

---

