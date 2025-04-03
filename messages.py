import os

class Messages:
    GRADIENT = "Gradient"
    LOGOS = "Logos"
    SET = "Set"
    GAME = "Game"
    HEIGHT = "Height"
    WIDTH = "Width"
    HPOS = "Pos. X"
    VPOS = "Pos. Y"
    OVERLAY_LINK = "Overlay"
    CONTROL_LINK = "Control"
    RESET_LINKS = "Reset"
    LOCAL = "Local"
    VISITOR = "Visitor"
    LOADING = "Loading..."
    INVALID_OVERLAY_CONTROL_TOKEN = "Invalid overlay control token"
    OVERLAY_CONFIGURATION_REQUIRED = "Overlay control URL not provided"
    USERNAME = "Username"
    PASSWORD = "Password"
    WRONG_USER_NAME = "Wrong username or password"
    LOGOUT = "Logout"
    USE_PREDEFINED_OVERLAYS = "Use predefined overlays",
    OVERLAY_DEPRECATED = "Outdated overlay version, please use a new one"
    LOGIN = "Log in"

    messages = {
        "es": {
            GRADIENT : "Gradiente",
            LOGOS:"Logos",
            SET:"Set",
            GAME:"Juego",
            HEIGHT:"Altura",
            WIDTH:"Ancho",
            HPOS:"Pos. X",
            VPOS:"Pos. Y",
            OVERLAY_LINK:"Overlay",
            CONTROL_LINK:"Control",
            RESET_LINKS:"Reset",
            LOCAL:"Local",
            VISITOR:"Visitante",
            LOADING:"Cargando...",
            INVALID_OVERLAY_CONTROL_TOKEN:"Token de control inválido",
            OVERLAY_CONFIGURATION_REQUIRED:"La URL de control es necesaria",
            USERNAME:"Usuario",
            PASSWORD:"Contraseña",
            WRONG_USER_NAME:"Usuario o contraseña incorrectos",
            LOGOUT: "Desconectar",
            USE_PREDEFINED_OVERLAYS: "Usar overlays predefinidos",
            OVERLAY_DEPRECATED: "Overlay no soportado, cambiar a uno actual",
            LOGIN:"Entrar"
          }
        }

    def get(message:str) -> str:
        local_messages = Messages.messages.get(os.environ.get('SCOREBOARD_LANGUAGE', ''), {})
        return local_messages.get(message, message)

