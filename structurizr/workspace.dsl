workspace "Fun With Flags" "C4-Modell der Fun With Flags Architektur" {

    model {
        # ──────────────────────────────────────────
        # Personen / Akteure
        # ──────────────────────────────────────────
        player        = person "Player"        "plays the game"

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

            frontend    = container "Frontend"    "provides UI for player - requests flags from backend - forwards player and game data"
            backend     = container "Backend"     "handles API requests - handles game logic - manages persistence"
            persistence = container "Persistence" "Saves player and game data - saves flag data" {
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
                frontendInstance = containerInstance frontend
            
                backendInstance = containerInstance backend
            
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
        # 3. Deployment (Kapitel 7 arc42)
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
