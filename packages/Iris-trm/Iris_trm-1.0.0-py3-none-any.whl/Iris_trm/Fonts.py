from pyfiglet import figlet_format
from Iris import text

def escolher_fonte(text: str = "", font: str = ""):
    '''
    Muda a fonte do texto.
    
    Parâmetros:
    - texto: str - Texto que vai ser personalizado
    - font: str - Fonte que vai ser usada
    
    Para encontrar fontes utilizaveis: `http://www.figlet.org/examples.html`
    '''
    
    if not text:
        return text.RED + "Insira um texto" + text.RESET
    
    if not font:
        return text.RED + "Insira uma fonta válida" + text.RESET
    
    return figlet_format(text=text, font=font)

if __name__ == '__main__':
    texto = "Teste"
    print(escolher_fonte(texto, 'big'))