from modules.GUI.ui_components import (
    init_page_config,
    init_session_state,
)

init_page_config()  ### Must be called before any other st. function
from modules.GUI.home import Home


class App:
    def __init__(self):
        init_session_state()
        self.run()

    def run(self):
        Home()


if __name__ == "__main__":
    App()
