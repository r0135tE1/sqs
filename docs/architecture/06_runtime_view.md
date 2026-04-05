# Runtime View

## Fetch Flag 
![Runtime View Start](chapter5-7Pics/runtime_view/runtimeviewstart.drawio.svg)

The user starts the game or the user has just guessed a country correctly. The frontend 
requests a new flag image from the FWF backend, which delegates the request to the external RESTCountries API. The flag image as well as the corresponding country's name is returned to the backend which forwards it to the frontend. The new random flag is displayed to the user.
## Guess Country - Correct Guess 
![Runtime View Guess - Correct](chapter5-7Pics/runtime_view/runtimeviewguesscorrect.drawio.svg)

The user guesses a country by typing text. The guess is evaluated in memory in the FWF frontend. The correct guess is validated, the user's score incremented and a success notification is sent to the user.
## Guess Country - Incorrect Guess 
![Runtime View Guess - Incorrect](chapter5-7Pics/runtime_view/runtimeviewguessincorrect.drawio.svg)

The user guesses a country by typing text. The guess is evaluated in memory in the FWF frontend.
The incorrect guess is identified, the guessing game is ended and the user's score is shown on screen. 
## Sign Up

![Runtime View Sign Up](chapter5-7Pics/runtime_view/runtime-sign-up.svg)

The user requests sign up by entering corresponding data. The Frontend forwards the data to the Backend, writing the user's data to the Persistence component. The backend checks if the user already exists. If no user exists, a new user will be created and the Player will be notified.

If the user already exists, the Player will be notified respectively and no new user will be registered.

## Login

![Runtime View Login](chapter5-7Pics/runtime_view/runtime-login.svg)

The user enters login data. The Frontend forwards the data to the Backend. The Backend queries the Persistence Component for the credentials. The backend validates the data provided by the Player and the data in the Persistence component. If the data matches, a token is returned which authenticates the Player.