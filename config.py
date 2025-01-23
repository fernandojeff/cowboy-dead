import pygame

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700

#Tamanho dos botoes
button_width = SCREEN_WIDTH // 4
button_height = SCREEN_HEIGHT // 10

# Configurações de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Inicializar fonte
pygame.init()
FONT = pygame.font.Font(None, 50)
