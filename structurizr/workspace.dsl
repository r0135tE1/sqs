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

                appShell = component "App" "App shell: holds global auth state, persists the JWT in localStorage, orchestrates modals."

                gameBoard = component "GameBoard" "Presentational game view: flag, answer buttons, score, loading/error states. Logic via useGame."

                authModal = component "AuthModal" "Login / sign-up modal with client-side validation; emits credentials."

                highscoresModal = component "HighscoresModal" "Fetches and shows the top-10 leaderboard (requires JWT)."

                saveScorePrompt = component "SaveScorePrompt" "Prompt for anonymous players after a wrong answer (sign up / log in). Presentational only."

                baseModal = component "BaseModal" "Reusable, accessible modal shell (dialog, focus trap, Escape)."

                notificationStack = component "NotificationStack" "Renders the active toast notifications."

                errorBoundary = component "ErrorBoundary" "Catches render errors and shows a fallback with retry."

                useGame = component "useGame" "Composable owning the game lifecycle: session, flags, answer checking, scoring, save-score."

                apiClient = component "API Client" "Central fetch wrapper: builds requests, attaches the Bearer token, parses JSON, raises typed errors."

                useNotifications = component "useNotifications" "Composable with shared notification state: add, auto-dismiss, dedupe."
            }

            backend = container "Backend" "handles API requests - handles game logic - manages persistence" "Python / FastAPI" "API" {

                appBootstrap = component "Application Bootstrap" "Initialises the app, registers routers, configures CORS, preloads FlagCache."

                authRouter = component "Auth Router" "Handles user registration and login."

                gameRouter = component "Game Router" "Manages game sessions: creates sessions, serves flags, validates answers."

                highscoresRouter = component "Highscores Router" "Protected leaderboard & score endpoints (requires JWT)."

                authService = component "Auth Service" "Password hashing/verification and JWT creation/decoding."

                flagCache = component "Flag Cache" "Loads country data & SVGs from the Public API at startup; serves random unseen flags."

                gameSessionStore = component "Game Session Store" "In-memory store for active sessions: flags, scores, open questions; cleans up."

                authDependency = component "Auth Dependency" "Validates the Bearer token, returns the authenticated user."

                databaseLayer = component "Database Layer" "SQLAlchemy engine, session factory, and ORM models (User, Highscore)."

                userRepository = component "User Repository" "DB queries for User records: lookup and creation."

                highscoreRepository = component "Highscore Repository" "DB queries for Highscore records: top-10, upsert, lookup."

                userService = component "User Service" "Registration and authentication logic."

                highscoreService = component "Highscore Service" "Highscore logic: leaderboard, user score lookup, persistence."

                appConfig = component "Config" "Pydantic settings: DB URL, JWT secret, CORS origins, API URL."
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
        appShell -> errorBoundary     "wraps to catch render errors"
        appShell -> gameBoard         "renders, passes JWT, auth/highscore events"
        appShell -> authModal         "renders, receives credentials"
        appShell -> highscoresModal   "renders, passes JWT"
        appShell -> notificationStack "renders"
        appShell -> apiClient         "register / login"
        appShell -> useNotifications  "shows auth feedback"

        # GameBoard delegates all game logic to the useGame composable
        gameBoard -> useGame          "delegates game lifecycle"
        gameBoard -> saveScorePrompt  "renders, forwards signup / login"

        useGame   -> apiClient        "session, flags, answers, save score"
        useGame   -> useNotifications "surfaces failures as toasts"

        saveScorePrompt -> baseModal  "built on"
        authModal       -> baseModal  "built on"

        highscoresModal -> apiClient  "fetches leaderboard & own score"
        highscoresModal -> baseModal  "built on"

        notificationStack -> useNotifications "reads notifications"

        # Frontend → Backend: all HTTP goes through the API Client
        apiClient -> authRouter       "POST /auth/register, POST /auth/login" "JSON / REST"
        apiClient -> gameRouter       "POST /game/session, GET /game/flag, POST /game/answer" "JSON / REST"
        apiClient -> highscoresRouter "GET /highscores/, GET /highscores/me, POST /highscores/ (Bearer)" "JSON / REST"

        # ──────────────────────────────────────────
        # Beziehungen – Komponenten Backend
        # ──────────────────────────────────────────
        appBootstrap -> authRouter        "registers" ""
        appBootstrap -> gameRouter        "registers" ""
        appBootstrap -> highscoresRouter  "registers" ""
        appBootstrap -> flagCache         "preloads on startup" ""
        appBootstrap -> gameSessionStore  "hourly cleanup" ""

        authRouter       -> authService      "creates JWT" ""
        authRouter       -> userService      "register / authenticate" ""
        gameRouter       -> flagCache        "gets random flag" ""
        gameRouter       -> gameSessionStore "sessions, questions, answers" ""
        highscoresRouter -> authDependency   "validates token" ""
        highscoresRouter -> highscoreService "highscore ops" ""
        highscoresRouter -> gameSessionStore "reads best score" ""
        authDependency   -> authService      "decodes JWT" ""
        flagCache        -> publicApi        "fetches countries & SVGs" "REST / HTTP"
        databaseLayer    -> persistence      "persists / queries" "SQL / asyncpg"
        userService      -> authService      "hashes / verifies passwords" ""
        userService      -> userRepository   "reads/writes users" ""
        userRepository   -> databaseLayer    "queries" "SQLAlchemy async"
        highscoreService -> userRepository   "looks up user" ""
        highscoreService -> highscoreRepository "reads/writes highscores" ""
        highscoreRepository -> databaseLayer "queries" "SQLAlchemy async"
        appBootstrap     -> appConfig        "reads config" ""

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
