import threading
import keyboard
import time
from os import system, name
from Iris import text, style, bg

class MenuHorizontal:
    """
    A class for creating an interactive horizontal selection menu in the terminal.
    
    Allows the user to navigate options using the left/right arrow keys and make a selection with Enter.
    Supports customizable colors for normal and selected items. Also allows a callback function to be triggered on selection.

    Attributes:
        itens (list[str]): A list of options to display.
        cor_normal (str): ANSI escape code for the default color/style of unselected items.
        cor_selecionado (str): ANSI escape code for the selected item.
        ao_selecionar (Callable[[int, str], None]): Optional function called when an item is selected (index, text).
        index (int): Current index of the selected item.
        pressed_key (str | None): Stores the last key pressed by the user.
        executando (bool): Controls the loop for the menu execution.
        _saida (str | None): Stores the selected item after execution.
    """

    def __init__(self, itens, cor_normal=text.BLACK, cor_selecionado=text.CYAN + style.BOLD, ao_selecionar=None):
        """
        Initializes the horizontal menu with the given items and appearance settings.

        Args:
            itens (list[str]): The list of options to be displayed.
            cor_normal (str): ANSI code for the default (unselected) color. Defaults to black.
            cor_selecionado (str): ANSI code for the selected item color/style. Defaults to bright cyan.
            ao_selecionar (Callable[[int, str], None], optional): A function to call when an item is selected. Defaults to None.
        """
        self.itens = itens
        self.index = 0
        self.cor_normal = cor_normal
        self.cor_selecionado = cor_selecionado
        self.ao_selecionar = ao_selecionar
        self.pressed_key = None
        self.executando = True
        self._saida = None

    def limpar_tela(self):
        """
        Clears the terminal screen, using 'cls' on Windows and 'clear' on Unix-based systems.
        """
        system('cls' if name == 'nt' else 'clear')

    def desenhar(self):
        """
        Renders the horizontal menu in the terminal, highlighting the currently selected item.
        """
        self.limpar_tela()
        texto = ""

        for i, item in enumerate(self.itens):
            if i == self.index:
                texto += f"{self.cor_selecionado}{item}{style.RESET_ALL} "
            else:
                texto += f"{self.cor_normal}{item}{style.RESET_ALL} "

            if i < len(self.itens) - 1:
                texto += "- "

        print(texto.strip())

    def _escutar_teclas(self):
        """
        Internal method running in a separate thread that listens for keyboard input.
        Captures key press events (left, right, enter, esc) and stores the last key pressed.
        """
        while self.executando:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.pressed_key = event.name

    def executar(self):
        """
        Starts the menu execution loop. Handles rendering and user input for navigation and selection.
        Runs until the user presses 'Enter' or 'Esc'.

        Behavior:
        - Left/right arrows navigate through items.
        - Enter selects the item and calls the `ao_selecionar` callback (if any).
        - Esc exits without selecting.
        """
        thread = threading.Thread(target=self._escutar_teclas, daemon=True)
        thread.start()

        self.desenhar()

        while self.executando:
            if self.pressed_key:
                tecla = self.pressed_key
                self.pressed_key = None

                if tecla == 'left':
                    self.index = (self.index - 1) % len(self.itens)
                elif tecla == 'right':
                    self.index = (self.index + 1) % len(self.itens)
                elif tecla == 'enter':
                    self._saida = self.itens[self.index]
                    if self.ao_selecionar:
                        self.ao_selecionar(self.index, self._saida)
                    self.executando = False
                elif tecla == 'esc':
                    self._saida = None
                    self.executando = False

                self.desenhar()

            time.sleep(0.1)

    def saida(self):
        """
        Returns the selected item after the menu has been executed.

        Returns:
            str | None: The selected item text, or None if no selection was made.
        """
        return self._saida


if __name__ == '__main__':
    # Example usage of the MenuHorizontal class
    menu = MenuHorizontal(
        itens=["SIM", "TALVEZ", "NÃO"],
        cor_normal=text.WHITE
    )

    menu.executar()

    escolha = menu.saida()
    print(f"\nValor retornado: {escolha}")
