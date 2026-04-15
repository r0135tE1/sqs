workspace "Fun With Flags" "C4-Modell der Fun With Flags Architektur" {

    model {
        # ──────────────────────────────────────────
        # Personen / Akteure
        # ──────────────────────────────────────────
        player        = person "Player"        "plays the game"

        # ──────────────────────────────────────────
        # Externe Systeme
        # ──────────────────────────────────────────
        publicApi = softwareSystem "Public API" "External Public API – provides flag data" {
            tags "External"
        }

        # ──────────────────────────────────────────
        # Software System
        # ──────────────────────────────────────────
        funWithFlags = softwareSystem "Fun With Flags" "web application for a flag quiz game" {

            frontend    = container "Frontend"    "Stellt die Benutzeroberfläche bereit" "Web / HTTP"
            backend     = container "Backend"     "Verarbeitet Geschäftslogik und API-Anfragen" "REST API"
            persistence = container "Persistence" "Speichert Nutzer, Scores und Spieldaten" "Database" {
                tags "Database"
            }
        }

        # ──────────────────────────────────────────
        # Beziehungen – System Context (business.svg)
        # ──────────────────────────────────────────
        player        -> funWithFlags "sign up & login, play the game, view highscores"
        funWithFlags  -> publicApi    "fetch flags"

        # ──────────────────────────────────────────
        # Beziehungen – Container (technical.svg / buildingblock_level1.svg)
        # ──────────────────────────────────────────
        player        -> frontend    "interacts with" "Internet / HTTP"
        frontend      -> backend     "API calls" "REST / HTTP"
        backend       -> persistence "reads from / writes to" "SQL"
        backend       -> publicApi   "requests flag data" "REST / HTTP"

        # ──────────────────────────────────────────
        # Deployment (deployment.svg)
        # ──────────────────────────────────────────
        deploymentEnvironment "Production" {
            deploymentNode "Container" {
                deploymentNode "Frontend Host" {
                    containerInstance frontend
                }
                deploymentNode "Backend Host" {
                    containerInstance backend
                }
                deploymentNode "Database Host" {
                    containerInstance persistence
                }
            }
            deploymentNode "External" {
                infrastructureNode "Public API" {
                    tags "External"
                }
            }
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
        # 2. Container (Kapitel 5 Level 1 arc42)
        # ──────────────────────────────────────────
        container funWithFlags "Containers" {
            title "Container – Fun With Flags"
            include *
            autolayout lr
        }

        # ──────────────────────────────────────────
        # 3. Deployment (Kapitel 7 arc42)
        # ──────────────────────────────────────────
        deployment funWithFlags "Production" "DeploymentView" {
            title "Deployment – Fun With Flags"
            include *
            autolayout lr
        }

        # ──────────────────────────────────────────
        # 4. Dynamic Views / Laufzeitsichten (Kapitel 6 arc42)
        # ──────────────────────────────────────────
        dynamic funWithFlags "Runtime_SignUp" "Laufzeitsicht: Sign Up" {
            title "Runtime – Sign Up"
            player -> frontend    "Fills sign up form"
            frontend -> backend   "Request sign up"
            backend -> persistence "Check for existing user"
            persistence -> backend "User does not exist"
            backend -> persistence "Create user"
            backend -> frontend   "Successful user creation"
            frontend -> player    "Display successful sign up"
            autolayout lr
        }

        dynamic funWithFlags "Runtime_Login" "Laufzeitsicht: Login" {
            title "Runtime – Login"
            player -> frontend    "Fills in login data"
            frontend -> backend   "Request sign in"
            backend -> persistence "Check credentials"
            persistence -> backend "return token"
            backend -> frontend   "Successful authentication"
            frontend -> player    "Display successful login"
            autolayout lr
        }

        dynamic funWithFlags "Runtime_FetchFlag" "Laufzeitsicht: Fetch Flag" {
            title "Runtime – Fetch Flag"
            player -> frontend    "Start game"
            frontend -> backend   "Get flag"
            backend -> publicApi  "Query flags"
            publicApi -> backend  "Return flags"
            backend -> frontend   "Return random flag"
            frontend -> player    "Display flag"
            autolayout lr
        }

        dynamic funWithFlags "Runtime_CorrectGuess" "Laufzeitsicht: Correct Guess" {
            title "Runtime – Correct Guess"
            player -> frontend    "Guess country"
            frontend -> backend   "Validate guess"
            backend -> persistence "Adjust highscore"
            backend -> publicApi  "Get new flag"
            publicApi -> backend  "Return flag"
            backend -> frontend   "Display flag"
            autolayout lr
        }

        dynamic funWithFlags "Runtime_IncorrectGuess" "Laufzeitsicht: Incorrect Guess" {
            title "Runtime – Incorrect Guess"
            player -> frontend    "Guess country"
            frontend -> backend   "Validate guess"
            backend -> persistence "Save highscore"
            backend -> frontend   "Return highscore"
            frontend -> player    "Show highscore"
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
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
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
