# Runtime View

## Fetch Flag

![Runtime View Start](chapter5-7Pics/runtime_view/runtime-fetch-flag.svg)

The player starts the game or has guessed a country correctly by its flag. The Frontend
requests a new flag image from the Backend. All flags are queried from the Persistence component and are cached in the Backend. The Backend forwards flag name and image to the Frontend displaying the flag to the Player.

Once The application starts, it requests all flags from the pulic API and stores them in the Persistence component. This is done every hour to ensure that the information is up to date.

## Guess Country - Correct Guess

We assume that the flags are already cached in the backend.

![Runtime View Guess - Correct](chapter5-7Pics/runtime_view/runtime-correct-guess.svg)

The Player guesses a country. The Frontend validates the guess and adjusts the highscore. Afterwards a new flag is requested to start a new round.

## Guess Country - Incorrect Guess

![Runtime View Guess - Incorrect](chapter5-7Pics/runtime_view/runtime-incorrect-guess.svg)

The Player guesses a country. The Frontend evaluates the guess to be incorrect. The current highscore is forwarded to the Backend to be persisted.
The highscore is then shown to the Player.

## Sign Up

![Runtime View Sign Up](chapter5-7Pics/runtime_view/runtime-sign-up.svg)

The user requests sign up by entering corresponding data. The Frontend forwards the data to the Backend. The backend checks if the user already exists. If no user exists, a new one will be created (Persistence) and the Player will be notified.

If the user already exists, the Player will be notified respectively and no new user will stored in the Persistence component.

## Login

![Runtime View Login](chapter5-7Pics/runtime_view/runtime-login.svg)

The user enters login data. The Frontend forwards the data to the Backend. The Backend queries the Persistence Component for the credentials. The backend validates the data provided by the Player and the data in the Persistence component. If the data matches, a token is returned which authenticates the Player.
