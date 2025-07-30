import sys
import time
from Iris import text, style

def create_load(texto, tipo='pontilhado', cor=text.WHITE, tempo_total=3.0):
    """
    Cria uma animação de loading personalizada com controle de tempo.
    
    Parâmetros:
    - texto: str - Texto a ser exibido antes da animação
    - tipo: str - Tipo de animação ('pontilhado', 'barra', 'girando', 'rolagem', 'progresso')
    - cor: str - Cor da animação (usar constantes do colorama.Fore)
    - tempo_total: float - Tempo total que o loading deve durar (em segundos)
    """

    print(cor, end='')
    
    try:
        if tipo == 'pontilhado':
            intervalo = tempo_total / 5
            for i in range(1, 6):
                dots = '.' * i
                sys.stdout.write(f'\r{texto}{dots}   ')
                sys.stdout.flush()
                time.sleep(intervalo)
                
        elif tipo == 'barra':
            largura = 20
            intervalo = tempo_total / largura
            for i in range(largura + 1):
                percent = i / largura * 100
                barra = '[' + '■' * i + ' ' * (largura - i) + ']'
                sys.stdout.write(f'\r{texto} {barra} {percent:.0f}%')
                sys.stdout.flush()
                time.sleep(intervalo)
                
        elif tipo == 'girando':
            sequencia = ['|', '/', '-', '\\']
            repeticoes = max(1, int(tempo_total / 0.4))
            intervalo = tempo_total / (repeticoes * len(sequencia))
            for _ in range(repeticoes):
                for char in sequencia:
                    sys.stdout.write(f'\r{texto} {char}')
                    sys.stdout.flush()
                    time.sleep(intervalo)
                    
        elif tipo == 'rolagem':
            ciclos = max(1, int(tempo_total / 0.8))
            intervalo = tempo_total / (ciclos * 4)
            for _ in range(ciclos):
                for i in range(4):
                    offset = i % 4
                    anim = '.' * offset + '■' + '.' * (3 - offset)
                    sys.stdout.write(f'\r{texto} {anim}')
                    sys.stdout.flush()
                    time.sleep(intervalo)
                
        elif tipo == 'progresso':
            intervalo = tempo_total / 100
            for i in range(101):
                sys.stdout.write(f'\r{texto} [{i:3}%]')
                sys.stdout.flush()
                time.sleep(intervalo)
                
        else:
            print(f"Tipo de loading '{tipo}' não reconhecido.")
            
    except KeyboardInterrupt:
        pass
    finally:
        print(style.RESET_ALL + '\r' + ' ' * 50 + '\r', end='')
        
        
if __name__ == '__main__':
    print(create_load("Analisando", 'pontilhado', text.GREEN, 3))
    print(create_load("Analisando", 'barra', text.GREEN, 3))
    print(create_load("Analisando", 'girando', text.GREEN, 3))
    print(create_load("Analisando", 'rolagem', text.GREEN, 3))
    print(create_load("Analisando", 'progresso', text.GREEN, 3))
        