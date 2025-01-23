import pygame
import sys
from game import jogar
from config import SCREEN_WIDTH, SCREEN_HEIGHT, button_width, button_height, BLACK
from utils import SpriteButton, load_and_scale_image
from pytmx import load_pygame


def main_menu(screen):
    tmx_data = load_pygame("mapas/fases/primeira_fase.tmx")

    # Criar função para desenhar o cabeçalho
    def draw_header():
        header_image = pygame.image.load("images/menu/header.png").convert_alpha()
        header_image = pygame.transform.scale(header_image, (513, 151))
        screen.blit(header_image, (158, 10))

    # Carregar as imagens dos botões com hover
    #BOTAO JOGAR 
    jogar_img_normal = pygame.image.load("images/menu/jogar_normal.png").convert_alpha()
    jogar_img_hover = pygame.image.load("images/menu/jogar_hover.png").convert_alpha()
    
    #BOTAO SAIR
    sair_img_normal = pygame.image.load("images/menu/sair_normal.png").convert_alpha()
    sair_img_hover = pygame.image.load("images/menu/sair_hover.png").convert_alpha()

    # Criar botões com as imagens de hover
    btn_jogar = SpriteButton(315, 200, jogar_img_normal, jogar_img_hover, lambda: jogar(screen, tmx_data, 0))
    btn_sair = SpriteButton(330, 300, sair_img_normal, sair_img_hover, lambda: pygame.quit() or sys.exit())
    buttons = [btn_jogar, btn_sair]

    running = True
    while running:
        screen.fill((0, 0, 0))  # Fundo preto

        draw_header()  # Desenhar o cabeçalho

        for button in buttons:
            button.draw(screen)  # Desenhar os botões

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for button in buttons:
                button.handle_event(event)  # Lidar com eventos de hover e clique

        pygame.display.update()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cowboy Dead by Fernando")
    main_menu(screen)
