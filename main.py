from modules.config import page_config
from modules.GUI.home import Home
from modules.GUI.ui_components import (
    display_sidebar,
    init_page_config,
    init_session_state,
)

init_page_config(page_config)


class App:
    def __init__(self):
        init_session_state()

        self.run()

    def run(self):
        Home()


if __name__ == "__main__":
    App()
