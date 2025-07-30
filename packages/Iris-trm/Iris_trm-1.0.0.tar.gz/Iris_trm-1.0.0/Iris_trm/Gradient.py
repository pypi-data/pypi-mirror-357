def gradient_horizontal(text: str, start_color: tuple, end_color: tuple):
    """
    Aplica um gradiente horizontal de cor em cada linha do texto fornecido.

    O gradiente é feito da esquerda para a direita, indo da cor inicial (`start_color`)
    para a cor final (`end_color`) ao longo dos caracteres de cada linha.

    Parâmetros:
        text (str): O texto que será colorido. Pode conter múltiplas linhas separadas por '\n'.
        start_color (tuple): Uma tupla (R, G, B) representando a cor inicial (à esquerda).
        end_color (tuple): Uma tupla (R, G, B) representando a cor final (à direita).

    Retorna:
        str: O texto com códigos ANSI aplicando o gradiente horizontal.
             Pode ser impresso diretamente no terminal que suporte cores RGB.

    Exemplo de uso:
        print(gradient_horizontal("Exemplo de texto", (255, 0, 0), (0, 0, 255)))
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    colored_lines = []
    
    for line in lines:
        if not line:
            colored_lines.append("")
            continue
            
        start_r, start_g, start_b = start_color
        end_r, end_g, end_b = end_color
        length = len(line)
        gradient_line = []
        
        for i, char in enumerate(line):
            ratio = i / (length - 1) if length > 1 else 0
            r = int(start_r + (end_r - start_r) * ratio)
            g = int(start_g + (end_g - start_g) * ratio)
            b = int(start_b + (end_b - start_b) * ratio)
            gradient_line.append(f"\033[38;2;{r};{g};{b}m{char}")
        
        colored_lines.append(''.join(gradient_line) + '\033[0m')
    
    return '\n'.join(colored_lines)

def gradient_vertical(text: str, start_color: tuple, end_color: tuple):
    """
    Aplica um gradiente vertical de cor no texto fornecido.

    O gradiente é feito de cima para baixo, indo da cor inicial (`start_color`)
    na primeira linha até a cor final (`end_color`) na última linha.

    Parâmetros:
        text (str): O texto que será colorido. Pode conter múltiplas linhas.
        start_color (tuple): Tupla (R, G, B) representando a cor inicial (no topo).
        end_color (tuple): Tupla (R, G, B) representando a cor final (embaixo).

    Retorna:
        str: O texto com códigos ANSI aplicando o gradiente vertical.
             Ideal para ser usado em terminais que suportem cores RGB.

    Exemplo de uso:
        print(gradient_vertical("Linha 1\nLinha 2\nLinha 3", (0, 255, 0), (0, 0, 255)))
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    if not lines:
        return ""
    
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    colored_lines = []
    total_lines = len(lines)
    
    for line_num, line in enumerate(lines):
        ratio = line_num / (total_lines - 1) if total_lines > 1 else 0
        r = int(start_r + (end_r - start_r) * ratio)
        g = int(start_g + (end_g - start_g) * ratio)
        b = int(start_b + (end_b - start_b) * ratio)
        colored_line = f"\033[38;2;{r};{g};{b}m{line}\033[0m"
        colored_lines.append(colored_line)
    
    return '\n'.join(colored_lines)

def gradient_radial(text: str, center_color: tuple, edge_color: tuple):
    """
    Aplica um gradiente radial de cor no texto, partindo do centro e indo para as bordas.

    Cada caractere do texto é colorido de acordo com a distância em relação ao centro do texto.
    Quanto mais próximo do centro, mais próximo da `center_color`; quanto mais longe, mais próximo da `edge_color`.

    Parâmetros:
        text (str): Texto que será colorido. Pode conter várias linhas.
        center_color (tuple): Cor (R, G, B) do centro do texto.
        edge_color (tuple): Cor (R, G, B) das extremidades (bordas).

    Retorna:
        str: O texto com um gradiente radial, aplicando códigos ANSI para colorir.
             Requer terminal com suporte a cores RGB ANSI.

    Exemplo de uso:
        print(gradient_radial("Texto\nRadial", (255, 255, 255), (0, 0, 0)))
    """
    if not text:
        return ""
    
    lines = text.split('\n')
    if not lines:
        return ""
    
    center_r, center_g, center_b = center_color
    edge_r, edge_g, edge_b = edge_color
    colored_lines = []
    
    max_line_length = max(len(line) for line in lines)
    center_x = max_line_length / 2
    center_y = len(lines) / 2
    max_distance = ((center_x)**2 + (center_y)**2)**0.5
    
    for y, line in enumerate(lines):
        colored_line = []
        for x, char in enumerate(line):
            distance = ((x - center_x)**2 + (y - center_y)**2)**0.5
            ratio = min(distance / max_distance, 1) if max_distance > 0 else 0

            r = int(center_r + (edge_r - center_r) * ratio)
            g = int(center_g + (edge_g - center_g) * ratio)
            b = int(center_b + (edge_b - center_b) * ratio)
            colored_line.append(f"\033[38;2;{r};{g};{b}m{char}")
        
        colored_lines.append(''.join(colored_line) + '\033[0m')
    
    return '\n'.join(colored_lines)
