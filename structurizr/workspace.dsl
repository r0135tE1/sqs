workspace "Fun With Flags" "C4-Modell der Fun With Flags Architektur" {

    model {
        # ──────────────────────────────────────────
        # Personen / Akteure
        # ──────────────────────────────────────────
        player = person "Player" "A user who plays the flag guessing game in a web browser."

        # ──────────────────────────────────────────
        # Externe Systeme
        # ──────────────────────────────────────────
        publicApi = softwareSystem "Public API" "external Public API – provides flag data" {
            tags "External"
        }

        # ──────────────────────────────────────────
        # Software System
        # ──────────────────────────────────────────
        funWithFlags = softwareSystem "Fun With Flags" "web application for a flag quiz game" {

            frontend = container "Frontend" "provides UI for player - requests flags from backend - forwards player and game data" {

                appShell = component "App" "Application shell. Manages global authentication state, persists the JWT token in localStorage, and orchestrates modal visibility."

                gameBoard = component "GameBoard" "Core game component. Creates a game session, fetches flags by session ID, submits answers to the backend, receives server-side score updates, and persists the session score to the backend."

                loginModal = component "LoginModal" "Presentational modal with a username/password form." 

                signUpModal = component "SignUpModal" "Presentational modal with a registration form. Applies client-side validation (username format, password length/complexity) before emitting credentials"

                highscoresModal = component "HighscoresModal" "Fetches and displays the top-10 leaderboard from the backend when opened. Requires a valid JWT token."
            }

            backend = container "Backend" "handles API requests - handles game logic - manages persistence" "Python / FastAPI" "API" {

                appBootstrap = component "Application Bootstrap" "Initialises the FastAPI app, registers routers, configures CORS middleware, triggers FlagCache preload at startup, and exposes the /health endpoint."

                authRouter = component "Auth Router" "Handles user registration and login. Delegates password hashing and token creation to the Auth Service."

                gameRouter = component "Game Router" "Session-based game endpoints: POST /game/session creates a session, GET /game/flag returns the next flag with inline SVG, POST /game/answer validates the answer server-side and updates the session score."

                highscoresRouter = component "Highscores Router" "Protected endpoints. Returns the top-10 leaderboard (GET /highscores/), the authenticated user's own highscore (GET /highscores/me), and persists a session score (POST /highscores/). All require a valid JWT."

                authService = component "Auth Service" "Stateless utilities for bcrypt password hashing/verification and HS256 JWT creation/decoding."

                flagCache = component "Flag Cache" "Fetches all country metadata and SVG images from the Public API once at startup and stores them in memory. Flag data is never written to the database. Returns a random unseen flag for a given session."

                gameSessionStore = component "Game Session Store" "In-memory store for active game sessions. Tracks seen flags, current score, best score, and open questions per session. A background task removes sessions inactive for more than 12 hours."

                authDependency = component "Auth Dependency" "FastAPI dependency. Extracts the Bearer token from the Authorization header, decodes it via Auth Service, and returns the username or raises HTTP 401."

                databaseLayer = component "Database Layer" "Async SQLAlchemy engine, session factory, get_db() dependency, and ORM models (User, Highscore)."
            }

            persistence = container "Persistence" "Saves player credentials and highscores. Flag data is not stored here — it is held in-memory by the backend." {
                tags "Database"
            }
        }

        # ──────────────────────────────────────────
        # Beziehungen – System Context
        # ──────────────────────────────────────────
        player       -> funWithFlags "sign up & login, play the game, view highscores"
        funWithFlags -> publicApi    "fetch flags"

        # ──────────────────────────────────────────
        # Beziehungen – Container
        # ──────────────────────────────────────────
        player   -> frontend    "interacts with" "Internet / HTTP"
        frontend -> backend     "API calls" "REST / HTTP"
        backend  -> persistence "reads from / writes to" "SQL"
        backend  -> publicApi   "requests flag data" "REST / HTTP"

        # ──────────────────────────────────────────
        # Beziehungen – Komponenten Frontend
        # ──────────────────────────────────────────
        appShell -> gameBoard        "Renders and passes JWT token as prop"
        appShell -> loginModal       "Renders; receives submit event with credentials"
        appShell -> signUpModal      "Renders; receives submit event with credentials"
        appShell -> highscoresModal  "Renders; passes JWT token as prop"

        appShell       -> backend "POST /auth/register – register new user" "JSON / REST"
        appShell       -> backend "POST /auth/login – obtain JWT token" "JSON / REST"
        gameBoard      -> backend "POST /game/session – create session" "JSON / REST"
        gameBoard      -> backend "GET /game/flag – fetch next flag" "JSON / REST"
        gameBoard      -> backend "POST /game/answer – submit answer" "JSON / REST"
        gameBoard      -> backend "POST /highscores/ – save session score (Bearer token)" "JSON / REST"
        highscoresModal -> backend "GET /highscores/ – fetch top-10 leaderboard (Bearer token)" "JSON / REST"
        highscoresModal -> backend "GET /highscores/me – fetch own highscore (Bearer token)" "JSON / REST"

        appShell        -> authRouter       "POST /auth/register, POST /auth/login" "JSON / REST"
        gameBoard       -> gameRouter       "POST /game/session, GET /game/flag, POST /game/answer" "JSON / REST"
        gameBoard       -> highscoresRouter "POST /highscores/" "JSON / REST"
        highscoresModal -> highscoresRouter "GET /highscores/, GET /highscores/me" "JSON / REST"

        # ──────────────────────────────────────────
        # Beziehungen – Komponenten Backend
        # ──────────────────────────────────────────
        appBootstrap -> authRouter        "Registers router" ""
        appBootstrap -> gameRouter        "Registers router" ""
        appBootstrap -> highscoresRouter  "Registers router" ""
        appBootstrap -> flagCache         "Calls load() on startup" ""
        appBootstrap -> gameSessionStore  "Runs cleanup task every hour" ""

        authRouter       -> authService      "Hashes passwords and creates JWT tokens via" ""
        authRouter       -> databaseLayer    "Reads/writes User records via" "SQLAlchemy async"
        gameRouter       -> flagCache        "Retrieves random unseen flag from" ""
        gameRouter       -> gameSessionStore "Creates sessions, stores questions, validates answers via" ""
        highscoresRouter -> authDependency   "Validates Bearer token via" ""
        highscoresRouter -> databaseLayer    "Reads/writes Highscore and User records via" "SQLAlchemy async"
        highscoresRouter -> gameSessionStore "Reads best score for a session via" ""
        authDependency   -> authService      "Decodes JWT via" ""
        flagCache        -> publicApi        "Fetches all countries and SVG images on startup from" "REST / HTTP"
        databaseLayer    -> persistence      "Persists and queries data in" "SQL / asyncpg"

        # ──────────────────────────────────────────
        # Deployment
        # ──────────────────────────────────────────
        deploymentEnvironment "Production" {
            deploymentNode "Container" {
                frontendInstance    = containerInstance frontend
                backendInstance     = containerInstance backend
                persistenceInstance = containerInstance persistence
            }
            deploymentNode "External" {
                publicApiNode = infrastructureNode "Public API" {
                    tags "External"
                }
            }
            backendInstance -> publicApiNode "requests flag data" "REST / HTTP"
        }
    }

    views {
        # ──────────────────────────────────────────
        # 1. System Context (Kapitel 3 arc42)
        # ──────────────────────────────────────────
        systemContext funWithFlags "SystemContext" {
            title "System Context – Fun With Flags"
            include *
            autolayout lr
        }

        # ──────────────────────────────────────────
        # 2. Technical Context (Kapitel 3 arc42)
        # ──────────────────────────────────────────
        container funWithFlags "SystemContext-Technical" {
            title "Technical Context – Fun With Flags"
            include *
            autolayout lr
        }

        # ──────────────────────────────────────────
        # 3. Komponenten – Frontend
        # ──────────────────────────────────────────
        component frontend "Components_Frontend" {
            include *
            autolayout tb
            title "Component Diagram – Frontend (Vue 3)"
        }

        # ──────────────────────────────────────────
        # 4. Komponenten – Backend
        # ──────────────────────────────────────────
        component backend "Components_Backend" {
            include *
            autolayout tb
            title "Component Diagram – Backend (FastAPI)"
        }

        # ──────────────────────────────────────────
        # 5. Deployment (Kapitel 7 arc42)
        # ──────────────────────────────────────────
        deployment funWithFlags "Production" "DeploymentView" {
            title "Deployment – Fun With Flags"
            include *
            autolayout lr
        }

        # ──────────────────────────────────────────
        # Styles
        # ──────────────────────────────────────────
        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Browser" {
                shape WebBrowser
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "API" {
                shape Hexagon
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "External" {
                background #b2f2bb
                color #1e1e1e
            }
            element "Infrastructure Node" {
                background #b2f2bb
                color #1e1e1e
            }
        }
    }
}
