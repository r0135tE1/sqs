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

            frontend = container "Frontend" "provides UI for player - requests flags from backend - forwards player and game data" "Vue 3 / TypeScript" {

                appShell = component "App" "Application shell. Manages global authentication state, persists the JWT token in localStorage, orchestrates modal visibility, and renders auth failures as inline form messages."

                gameBoard = component "GameBoard" "Presentational game view. Renders the flag, answer buttons, score / highscore, result strips, and loading / error states; forwards user interactions and delegates the full game lifecycle to the useGame composable."

                authModal = component "AuthModal" "Combined login / sign-up modal. Toggles between modes and applies client-side validation (username format, password length/complexity) in sign-up mode before emitting credentials."

                highscoresModal = component "HighscoresModal" "Fetches and displays the top-10 leaderboard from the backend when opened. Requires a valid JWT token."

                saveScorePrompt = component "SaveScorePrompt" "Presentational prompt shown to anonymous players after a wrong answer, inviting them to sign up or log in to save their score. Emits navigation events; holds no auth logic."

                baseModal = component "BaseModal" "Reusable, accessible modal shell (role=dialog, focus trap, Escape to close): backdrop, optional header, and a content slot. Used by the other modals."

                notificationStack = component "NotificationStack" "Renders the active toast notifications."

                errorBoundary = component "ErrorBoundary" "Catches render errors in the component tree and shows a fallback UI with a retry action."

                useGame = component "useGame" "Composable owning the game lifecycle: session creation, flag loading, answer checking, scoring, personal-best, and save-score logic. Surfaces API failures as toasts and keeps GameBoard purely presentational."

                apiClient = component "API Client" "Central fetch wrapper (apiFetch). Builds requests, attaches the Bearer token, encodes/parses JSON, and raises typed ApiError / NetworkError failures (mapped to user messages by a shared helper)."

                useNotifications = component "useNotifications" "Composable holding the shared notification state: add, auto-dismiss, manual dismiss, and dedupe by type+message."
            }

            backend = container "Backend" "handles API requests - handles game logic - manages persistence" "Python / FastAPI" "API" {

                appBootstrap = component "Application Bootstrap" "Initialises the app, registers routers, configures CORS, and triggers FlagCache preload at startup."

                authRouter = component "Auth Router" "Handles user registration and login."

                gameRouter = component "Game Router" "Manages game sessions: creates sessions, serves flags, and validates answers."

                highscoresRouter = component "Highscores Router" "Protected endpoints for leaderboard and score persistence. Requires valid JWT."

                authService = component "Auth Service" "Password hashing/verification and JWT creation/decoding."

                flagCache = component "Flag Cache" "Loads country metadata and SVG images from the Public API at startup. Serves random unseen flags per session."

                gameSessionStore = component "Game Session Store" "In-memory store for active game sessions. Tracks flags, scores, and open questions. Cleans up inactive sessions."

                authDependency = component "Auth Dependency" "Validates the Bearer token and returns the authenticated username."

                databaseLayer = component "Database Layer" "SQLAlchemy engine, session factory, and ORM models (User, Highscore)."

                userRepository = component "User Repository" "DB queries for User records: lookup and creation."

                highscoreRepository = component "Highscore Repository" "DB queries for Highscore records: top-10, upsert, and lookup by user."

                userService = component "User Service" "Registration and authentication logic."

                highscoreService = component "Highscore Service" "Highscore business logic: leaderboard retrieval, user score lookup, and score persistence."

                appConfig = component "Config" "Pydantic Settings for database URL, JWT secret, CORS origins, and API URL."
            }

            persistence = container "Persistence" "Saves player credentials and highscores." {
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
        # App shell wiring (render + events)
        appShell -> errorBoundary     "Wraps the UI to catch and surface render errors"
        appShell -> gameBoard         "Renders; passes JWT token as prop; reacts to open-login / open-signup / session-expired / new-highscore events"
        appShell -> authModal         "Renders; receives submit event with credentials"
        appShell -> highscoresModal   "Renders; passes JWT token as prop"
        appShell -> notificationStack "Renders the active toast notifications"
        appShell -> apiClient         "Registers and logs in the user via; shows auth failures as inline form messages"
        appShell -> useNotifications  "Shows authentication feedback via"

        # GameBoard delegates all game logic to the useGame composable
        gameBoard -> useGame          "Delegates the full game lifecycle to"
        gameBoard -> saveScorePrompt  "Renders; forwards signup / login events to the app"

        useGame   -> apiClient        "Creates session, fetches flags, submits answers, and saves the score via"
        useGame   -> useNotifications "Surfaces API failures as error / warning toasts via"

        saveScorePrompt -> baseModal  "Built on the reusable modal shell"
        authModal       -> baseModal  "Built on the reusable modal shell"

        highscoresModal -> apiClient  "Fetches the leaderboard and the player's own score via; renders loading / error / empty states"
        highscoresModal -> baseModal  "Built on the reusable modal shell"

        notificationStack -> useNotifications "Reads the active notifications from"

        # Frontend → Backend: all HTTP goes through the API Client
        apiClient -> backend          "REST API calls (auth, game, highscores)" "JSON / REST"

        apiClient -> authRouter       "POST /auth/register, POST /auth/login" "JSON / REST"
        apiClient -> gameRouter       "POST /game/session, GET /game/flag, POST /game/answer" "JSON / REST"
        apiClient -> highscoresRouter "GET /highscores/, GET /highscores/me, POST /highscores/ (Bearer)" "JSON / REST"

        # ──────────────────────────────────────────
        # Beziehungen – Komponenten Backend
        # ──────────────────────────────────────────
        appBootstrap -> authRouter        "Registers router" ""
        appBootstrap -> gameRouter        "Registers router" ""
        appBootstrap -> highscoresRouter  "Registers router" ""
        appBootstrap -> flagCache         "Calls load() on startup" ""
        appBootstrap -> gameSessionStore  "Runs cleanup task every hour" ""

        authRouter       -> authService      "Creates JWT token via" ""
        authRouter       -> userService      "Delegates registration and authentication to" ""
        gameRouter       -> flagCache        "Retrieves random unseen flag from" ""
        gameRouter       -> gameSessionStore "Creates sessions, stores questions, validates answers via" ""
        highscoresRouter -> authDependency   "Validates Bearer token via" ""
        highscoresRouter -> highscoreService "Delegates highscore operations to" ""
        highscoresRouter -> gameSessionStore "Reads best score for a session via" ""
        authDependency   -> authService      "Decodes JWT via" ""
        flagCache        -> publicApi        "Fetches all countries and SVG images on startup from" "REST / HTTP"
        databaseLayer    -> persistence      "Persists and queries data in" "SQL / asyncpg"
        userService      -> authService      "Hashes and verifies passwords via" ""
        userService      -> userRepository   "Reads/writes User records via" ""
        userRepository   -> databaseLayer    "Executes queries via" "SQLAlchemy async"
        highscoreService -> userRepository   "Looks up user by username via" ""
        highscoreService -> highscoreRepository "Reads/writes Highscore records via" ""
        highscoreRepository -> databaseLayer "Executes queries via" "SQLAlchemy async"
        appBootstrap     -> appConfig        "Reads configuration from" ""

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
