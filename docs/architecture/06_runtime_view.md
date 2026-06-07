# Runtime View

## Fetch Flag

![Runtime View Start](chapter5-7Pics/runtime_view/runtime-fetch-flag.svg)

On application startup, the Backend fetches all country data and flag images from the public API and stores them exclusively in-memory (`FlagCache`). The cache is loaded once at startup and serves all flag requests for the lifetime of the process.

The player starts a game by creating a session. The Frontend then requests the next flag. The Backend picks a random unseen country from the in-memory `FlagCache` and returns the flag SVG inline along with four answer options and a `question_id`. The correct answer is stored server-side and never sent to the client.

## Guess Country - Correct Guess

We assume that the flags are already cached in the backend.

![Runtime View Guess - Correct](chapter5-7Pics/runtime_view/runtime-correct-guess.svg)

The Player guesses a country. The Frontend submits the answer to the Backend. The Backend validates the answer server-side, increments the session score by 1, and returns it to the Frontend. The Frontend then requests a new flag to start the next round.

## Guess Country - Incorrect Guess

![Runtime View Guess - Incorrect](chapter5-7Pics/runtime_view/runtime-incorrect-guess.svg)

The Player guesses a country. The Frontend submits the answer to the Backend. The Backend validates the answer server-side, resets the session score to 0, and returns it to the Frontend. The correct answer is shown to the Player. The score is only persisted to the database when the user explicitly saves it via `POST /highscores/` with their `session_id`.

## Sign Up and Login

![Runtime View Sign Up](chapter5-7Pics/runtime_view/runtime-sign-up.svg)

The Player requests sign up by entering corresponding data. The Frontend forwards the data to the Backend. The Backend checks if the user already exists. If no user exists, a new one will be created and the Player will be notified.

If the user already exists, the Player will be notified respectively and no new user will be stored in the Persistence component.

After a successful sign up, the Frontend automatically triggers a login with the same credentials. The Backend validates the credentials, creates a JWT token and returns it to the Frontend. From this point on, the Player is authenticated and the token is used for all protected requests (e.g. saving a highscore).
