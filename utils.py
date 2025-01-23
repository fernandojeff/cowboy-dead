import pygame
from config import BLACK, GRAY

def load_and_scale_image(image_path, width, height):
    """Carrega e redimensiona uma imagem."""
    image = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.scale(image, (width, height))

# Desenhar sprites com suporte a hover
class SpriteButton:
    def __init__(self, x, y, image_normal, image_hover, action=None):
        self.image_normal = image_normal  # Imagem padrão
        self.image_hover = image_hover  # Imagem para hover
        self.image = self.image_normal  # Inicialmente usa a imagem padrão
        self.rect = self.image.get_rect(topleft=(x, y))
        self.action = action

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()  # Obtém a posição atual do mouse

        # Trocar a imagem com base na posição do mouse
        if self.rect.collidepoint(mouse_pos):
            self.image = self.image_hover  # Usa a imagem de hover
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clique com o botão esquerdo
                if self.action:
                    self.action()  # Executa a ação associada
        else:
            self.image = self.image_normal  # Volta para a imagem padrão

# Função para desenhar um botão sem ser sprites
def draw_button(screen, text, x, y, width, height, active_color, inactive_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    color = active_color if x < mouse[0] < x + width and y < mouse[1] < y + height else inactive_color
    pygame.draw.rect(screen, color, (x, y, width, height))

    # Renderizar texto
    from config import FONT
    text_surface = FONT.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

    # Verificar clique
    if click[0] == 1 and action:
        pygame.time.delay(200)  # Evitar múltiplos cliques rápidos
        action()

# Modificar o método draw do grupo de sprites
class CustomGroup(pygame.sprite.Group):
    def draw(self, surface):
        for sprite in self.sprites():
            if hasattr(sprite, 'visivel') and not sprite.visivel:
                continue
            surface.blit(sprite.image, sprite.rect)

def transicao_fase(time, screen, duracao):
    largura, altura = screen.get_size()
    clock = pygame.time.Clock()
    tempo_inicio = time.time()
    overlay = pygame.Surface((largura, altura), pygame.SRCALPHA)
    while time.time() - tempo_inicio < duracao:
        tempo_passado = time.time() - tempo_inicio
        proporcao = tempo_passado / duracao
        
        raio_atual = int(max(largura, altura) * proporcao)
        
        pygame.draw.circle(overlay, (0, 0, 0, 255), (largura // 2, altura // 2), raio_atual)
        
        # Desenhar o conteúdo atual da tela
        screen.blit(screen, (0, 0))
        # Desenhar o overlay com o círculo
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

