import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# --- Variáveis de Câmera (Avião/Ponto de Vista) ---
camera_pos = [0.0, 1.0, 5.0]  # Posição inicial (x, y, z)
camera_yaw = -90.0          # Rotação horizontal (graus)
camera_pitch = 0.0          # Rotação vertical (graus)
move_speed = 0.1
rotate_speed = 1.0

# Armazenamento do estado das teclas
keys_down = {}

# --- Configurações da Janela ---
window_width = 1024
window_height = 768
window_title = "Simulador de Voo 3D Básico (Edifícios Amarelos)"

# --- Definição dos Edifícios ---
# Lista de tuplas (x, z, largura, profundidade, altura) para edifícios
# O 'y' (altura) começa em 0
buildings = [
    (0, 0, 1.5, 1.5, 3.0),
    (5, -3, 2.0, 1.0, 5.0),
    (-4, 4, 1.0, 3.0, 2.0),
    (8, 6, 1.0, 1.0, 6.0),
    (-6, -7, 4.0, 1.0, 4.0),
]

# --- Funções de Desenho ---

def draw_cube(x, y, z, width, depth, height):
    """Desenha um cubo no centro (x, y, z) com as dimensões especificadas."""
    
    # O centro do cubo é (x, y + height/2, z) para que a base esteja em y=0
    
    half_w, half_d = width / 2.0, depth / 2.0
    
    glPushMatrix()
    glTranslatef(x, y + height / 2.0, z) # Move para a posição e sobe metade da altura
    
    glColor3f(1.0, 1.0, 0.0)  # Cor Amarela
    
    # Desenhar as faces do cubo
    glBegin(GL_QUADS)
    
    # Frente (Face +Z)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-half_w, -height/2, half_d)
    glVertex3f( half_w, -height/2, half_d)
    glVertex3f( half_w, height/2, half_d)
    glVertex3f(-half_w, height/2, half_d)
    
    # Trás (Face -Z)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-half_w, -height/2, -half_d)
    glVertex3f(-half_w, height/2, -half_d)
    glVertex3f( half_w, height/2, -half_d)
    glVertex3f( half_w, -height/2, -half_d)
    
    # Cima (Face +Y)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-half_w, height/2, -half_d)
    glVertex3f(-half_w, height/2, half_d)
    glVertex3f( half_w, height/2, half_d)
    glVertex3f( half_w, height/2, -half_d)
    
    # Baixo (Face -Y) (Chão, não visível)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-half_w, -height/2, -half_d)
    glVertex3f( half_w, -height/2, -half_d)
    glVertex3f( half_w, -height/2, half_d)
    glVertex3f(-half_w, -height/2, half_d)
    
    # Direita (Face +X)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( half_w, -height/2, half_d)
    glVertex3f( half_w, -height/2, -half_d)
    glVertex3f( half_w, height/2, -half_d)
    glVertex3f( half_w, height/2, half_d)
    
    # Esquerda (Face -X)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-half_w, -height/2, half_d)
    glVertex3f(-half_w, height/2, half_d)
    glVertex3f(-half_w, height/2, -half_d)
    glVertex3f(-half_w, -height/2, -half_d)
    
    glEnd()
    glPopMatrix()


def draw_ground():
    """Desenha um plano grande para simular o chão."""
    glColor3f(0.2, 0.4, 0.2)  # Cor Verde Escuro
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0) # Normal para a iluminação
    size = 100.0
    glVertex3f(-size, 0.0, -size)
    glVertex3f( size, 0.0, -size)
    glVertex3f( size, 0.0, size)
    glVertex3f(-size, 0.0, size)
    glEnd()

# --- Funções OpenGL ---

def init_gl():
    """Configuração inicial do OpenGL."""
    glClearColor(0.53, 0.81, 0.98, 1.0) # Cor de céu azul claro
    glEnable(GL_DEPTH_TEST) # Ativa o teste de profundidade (para objetos em 3D)
    
    # Configuração de Iluminação
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Fonte de luz (Direcional, como o Sol)
    light_position = [1.0, 1.0, 1.0, 0.0]  # O último 0.0 indica uma luz direcional
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    
    # Cor da luz
    ambient_light = [0.2, 0.2, 0.2, 1.0]
    diffuse_light = [0.8, 0.8, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)

    # Configuração da cor do material (para o glColor funcionar)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


def reshape(width, height):
    """Chamado quando a janela é redimensionada."""
    global window_width, window_height
    window_width = width
    window_height = height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Define a perspectiva (FOV de 60 graus, proporção da janela, plano near/far)
    gluPerspective(60.0, width / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()


def display():
    """Função de desenho principal."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # --- Configuração da Câmera (View) ---
    
    # Rotação da câmera para Pitch (vertical) e Yaw (horizontal)
    glRotatef(camera_pitch, 1.0, 0.0, 0.0) # Aplica Pitch
    glRotatef(camera_yaw, 0.0, 1.0, 0.0)   # Aplica Yaw
    
    # Translação para a posição da câmera (inversa, pois é o mundo que se move)
    glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
    
    # --- Desenho da Cena ---
    
    # 1. Desenha o chão
    draw_ground()
    
    # 2. Desenha os edifícios amarelos
    for x, z, w, d, h in buildings:
        draw_cube(x, 0, z, w, d, h)
        
    glutSwapBuffers()

# --- Lógica de Movimento ---

def update_movement(dt):
    """
    Calcula e aplica o movimento da câmera com base nas teclas pressionadas.
    O movimento é relativo à direção da câmera.
    """
    global camera_pos, camera_yaw, camera_pitch
    
    # Converte yaw/pitch para radianos
    yaw_rad = math.radians(camera_yaw)
    pitch_rad = math.radians(camera_pitch)
    
    # Vetor de direção 'forward' (para frente)
    forward_x = math.cos(yaw_rad) * math.cos(pitch_rad)
    forward_y = math.sin(pitch_rad)
    forward_z = math.sin(yaw_rad) * math.cos(pitch_rad)
    
    # Vetor 'right' (para a direita) - Sem pitch para movimento lateral no plano XZ
    right_x = math.cos(yaw_rad - math.pi / 2.0)
    right_z = math.sin(yaw_rad - math.pi / 2.0)

    # Vetor 'up' para subir/descer (fixo no eixo Y)
    up_y = 1.0

    # Aplica o movimento
    dist = move_speed * dt # Distância a percorrer
    
    # Movimento para frente/trás (W/S)
    if keys_down.get('w'):
        camera_pos[0] += forward_x * dist
        camera_pos[2] += forward_z * dist
        # camera_pos[1] += forward_y * dist # Descomente para voar para cima/baixo
    if keys_down.get('s'):
        camera_pos[0] -= forward_x * dist
        camera_pos[2] -= forward_z * dist
        # camera_pos[1] -= forward_y * dist # Descomente para voar para cima/baixo

    # Movimento lateral (A/D)
    if keys_down.get('a'):
        camera_pos[0] += right_x * dist
        camera_pos[2] += right_z * dist
    if keys_down.get('d'):
        camera_pos[0] -= right_x * dist
        camera_pos[2] -= right_z * dist
        
    # Subir/Descer fixo (Espaço/Ctrl)
    if keys_down.get(' '): # Espaço
        camera_pos[1] += up_y * dist
    if keys_down.get('ctrl'): # Ctrl
        camera_pos[1] -= up_y * dist

    # Rotação (setas)
    rot = rotate_speed * dt
    if keys_down.get('left'):
        camera_yaw += rot
    if keys_down.get('right'):
        camera_yaw -= rot
    if keys_down.get('up'):
        camera_pitch -= rot
    if keys_down.get('down'):
        camera_pitch += rot
        
    # Limita o pitch para não virar de ponta-cabeça
    camera_pitch = max(-89.0, min(89.0, camera_pitch))

    # Limita a altura mínima para não passar pelo chão (y > 0)
    camera_pos[1] = max(0.1, camera_pos[1])
    
    glutPostRedisplay() # Redesenha a cena


# --- Funções de Input (Teclado) ---

# Para controlar o tempo entre frames e o movimento
last_time = 0

def timer_func(value):
    """Função de timer para animação e movimento contínuo."""
    global last_time
    current_time = glutGet(GLUT_ELAPSED_TIME)
    # dt (delta time) em segundos
    dt = (current_time - last_time) / 1000.0
    last_time = current_time
    
    # Chama a função de movimento
    update_movement(dt)

    # Agenda o próximo timer
    glutTimerFunc(16, timer_func, 0) # 16ms é aproximadamente 60 FPS


def keyboard_down(key, x, y):
    """Trata o pressionar de teclas normais."""
    key = key.decode("utf-8").lower() # Converte para string e minúsculas
    if key == 'w':
        keys_down['w'] = True
    elif key == 's':
        keys_down['s'] = True
    elif key == 'a':
        keys_down['a'] = True
    elif key == 'd':
        keys_down['d'] = True
    elif key == ' ': # Espaço para subir
        keys_down[' '] = True
    elif key == 'c' or key == 'ctrl': # 'C' ou Ctrl para descer
        keys_down['ctrl'] = True
    elif key == '\x1b': # ESC
        sys.exit()


def keyboard_up(key, x, y):
    """Trata o soltar de teclas normais."""
    key = key.decode("utf-8").lower()
    if key == 'w':
        keys_down['w'] = False
    elif key == 's':
        keys_down['s'] = False
    elif key == 'a':
        keys_down['a'] = False
    elif key == 'd':
        keys_down['d'] = False
    elif key == ' ':
        keys_down[' '] = False
    elif key == 'c' or key == 'ctrl':
        keys_down['ctrl'] = False

def special_down(key, x, y):
    """Trata o pressionar de teclas especiais (setas)."""
    if key == GLUT_KEY_LEFT:
        keys_down['left'] = True
    elif key == GLUT_KEY_RIGHT:
        keys_down['right'] = True
    elif key == GLUT_KEY_UP:
        keys_down['up'] = True
    elif key == GLUT_KEY_DOWN:
        keys_down['down'] = True

def special_up(key, x, y):
    """Trata o soltar de teclas especiais (setas)."""
    if key == GLUT_KEY_LEFT:
        keys_down['left'] = False
    elif key == GLUT_KEY_RIGHT:
        keys_down['right'] = False
    elif key == GLUT_KEY_UP:
        keys_down['up'] = False
    elif key == GLUT_KEY_DOWN:
        keys_down['down'] = False


# --- Função Principal ---
def _exitfunc():
     while True:
         a=0


if __name__ == '__main__':
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"hello ")

    init_gl()
    
    # Registra os callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    
    # Inicializa o timer para o loop de movimento
    last_time = glutGet(GLUT_ELAPSED_TIME)
    glutTimerFunc(16, timer_func, 0)

    print("--- Controles ---")
    print("W/S: Mover para frente/trás")
    print("A/D: Mover para os lados (strafe)")
    print("ESPAÇO/C: Subir/Descer")
    print("SETAS: Olhar para cima/baixo/esquerda/direita")
    print("ESC: Sair")

    glutMainLoop()
