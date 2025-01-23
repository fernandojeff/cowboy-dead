import pygame
import sys
import pytmx
import random
import time
from config import WHITE, SCREEN_WIDTH, SCREEN_HEIGHT
from utils import CustomGroup, transicao_fase
from pytmx import load_pygame, TiledTileLayer

# Inicialize o mixer do Pygame
pygame.mixer.init()

# Carregue a trilha sonora
pygame.mixer.music.load('images/outros/JourneyOfThePrairieKingOverworld.mp3')

# Reproduza a trilha sonora em loop
pygame.mixer.music.play(-1)

def parar_musica():
    pygame.mixer.music.stop()

def musica_derrota():
    # Parar a música atual
    pygame.mixer.music.stop()

    # Carregar a nova música
    pygame.mixer.music.load('images/outros/game_over.mp3')

    # Reproduzir a nova música
    pygame.mixer.music.play(-1)

def musica_venceu():
     # Parar a música atual
    pygame.mixer.music.stop()

    # Carregar a nova música
    pygame.mixer.music.load('images/outros/win_sound.mp3')

    # Reproduzir a nova música
    pygame.mixer.music.play(-1)

# Criando grupos de sprites para colisão
grupo_cactus = pygame.sprite.Group()

class Jogador(pygame.sprite.Sprite):
    def __init__(self, x, y, spritesheets, bala_image):
        super().__init__()
        self.spritesheets = spritesheets
        self.animations = self.load_animations()
        self.current_animation = 'idle_down'
        self.current_frame = 0
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.invulneravel = False
        self.tempo_invulneravel = 0
        self.tempo_piscar = 0
        self.visivel = True
        
        #Balas
        self.bala_image = bala_image
        self.balas = pygame.sprite.Group()  # Grupo de balas disparadas
        self.shoot_cooldown = 250  # Tempo de recarga em milissegundos
        self.last_shot_time = 0  # Tempo do último tiro

        # Variáveis para ajustar a área de colisão
        collision_offset_left = 40
        collision_offset_top = 40
        collision_offset_right = 0
        collision_offset_bottom = 0
        
        self.collision_rect = pygame.Rect(
            self.rect.left + collision_offset_left,
            self.rect.top + collision_offset_top,
            self.rect.width - (collision_offset_left + collision_offset_right),
            self.rect.height - (collision_offset_top + collision_offset_bottom)
        )        
        
        self.velocidade = 300
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150  # Tempo em milissegundos para trocar de frame
        self.vidas = 5 #Vidas do jofador
    
    def atirar(self, direction):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            bala = Bala(self.rect.centerx, self.rect.centery, direction, self.bala_image)
            self.balas.add(bala)
            self.last_shot_time = now

    def load_animations(self):
        animations = {
            'idle_down': self.load_frames(self.spritesheets['idle_down'], 4),
            'idle_up': self.load_frames(self.spritesheets['idle_up'], 4),
            'idle_left': self.load_frames(self.spritesheets['idle_left'], 4),
            'idle_right': self.load_frames(self.spritesheets['idle_right'], 4),
            'walk_down': self.load_frames(self.spritesheets['walk_down'], 4),
            'walk_up': self.load_frames(self.spritesheets['walk_up'], 4),
            'walk_left': self.load_frames(self.spritesheets['walk_left'], 4),
            'walk_right': self.load_frames(self.spritesheets['walk_right'], 4),
            'attack_down': self.load_frames(self.spritesheets['attack_down'], 5),
            'attack_up': self.load_frames(self.spritesheets['attack_up'], 5),
            'attack_left': self.load_frames(self.spritesheets['attack_left'], 5),
            'attack_right': self.load_frames(self.spritesheets['attack_right'], 5),
            'attack_up_left': self.load_frames(self.spritesheets['attack_up_left'], 5),
            'attack_up_right': self.load_frames(self.spritesheets['attack_up_right'], 5),
            'attack_down_left': self.load_frames(self.spritesheets['attack_down_left'], 5),
            'attack_down_right': self.load_frames(self.spritesheets['attack_down_right'], 5),
            'dead': self.load_frames(self.spritesheets['dead'], 6),
        }
        return animations

    def load_frames(self, spritesheet, num_frames):
        frames = []
        frame_width = spritesheet.get_width() // num_frames
        frame_height = spritesheet.get_height()
        for i in range(num_frames):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (96, 96))  # Redimensionar para 96x96 pixels
            frames.append(frame)
        return frames

    def update(self, teclas, delta_time):
        pos_inicial = self.rect.topleft

        #Teclas de movimentação
        if teclas[pygame.K_w]:
            self.rect.y -= int(self.velocidade * delta_time)
            self.current_animation = 'walk_up'
        elif teclas[pygame.K_s]:
            self.rect.y += int(self.velocidade * delta_time)
            self.current_animation = 'walk_down'
        elif teclas[pygame.K_a]:
            self.rect.x -= int(self.velocidade * delta_time)
            self.current_animation = 'walk_left'
        elif teclas[pygame.K_d]:
            self.rect.x += int(self.velocidade * delta_time)
            self.current_animation = 'walk_right'
        else:
            if 'walk' in self.current_animation:
                self.current_animation = self.current_animation.replace('walk', 'idle')

         # Detectar teclas de ataque
        if teclas[pygame.K_UP] and teclas[pygame.K_LEFT]:
            self.current_animation = 'attack_up_left'
            self.atirar('up_left')
        elif teclas[pygame.K_UP] and teclas[pygame.K_RIGHT]:
            self.current_animation = 'attack_up_right'
            self.atirar('up_right')
        elif teclas[pygame.K_DOWN] and teclas[pygame.K_LEFT]:
            self.current_animation = 'attack_down_left'
            self.atirar('down_left')
        elif teclas[pygame.K_DOWN] and teclas[pygame.K_RIGHT]:
            self.current_animation = 'attack_down_right'
            self.atirar('down_right')
        elif teclas[pygame.K_UP]:
            self.current_animation = 'attack_up'
            self.atirar('up')
        elif teclas[pygame.K_DOWN]:
            self.current_animation = 'attack_down'
            self.atirar('down')
        elif teclas[pygame.K_LEFT]:
            self.current_animation = 'attack_left'
            self.atirar('left')
        elif teclas[pygame.K_RIGHT]:
            self.current_animation = 'attack_right'
            self.atirar('right')

        self.collision_rect.topleft = (self.rect.left + 27, self.rect.top + 18)  # Atualizar a posição do collision_rect

        if pygame.sprite.spritecollide(self, grupo_cactus, False, collided=lambda x, y: x.collision_rect.colliderect(y.rect)):
            self.rect.topleft = pos_inicial

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.current_frame]
            self.rect.size = self.image.get_size()  # Atualizar o tamanho do rect para corresponder à nova imagem
            self.rect.topleft = pos_inicial  # Manter a posição inicial do rect
        
        # Atualizar invulnerabilidade
        if self.invulneravel:
            self.tempo_invulneravel -= delta_time
            self.tempo_piscar -= delta_time
            if self.tempo_piscar <= 0:
                self.tempo_piscar = 0.1  # Alternar visibilidade a cada 0.1 segundos
                self.visivel = not self.visivel
            if self.tempo_invulneravel <= 0:
                self.invulneravel = False
                self.visivel = True
                
    def tomar_dano(self):
        if not self.invulneravel:
            self.vidas -= 1
            self.invulneravel = True
            self.tempo_invulneravel = 2  # 2 segundos de invulnerabilidade
            self.tempo_piscar = 0.1  # Iniciar o piscar

class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, jogador, spritesheet, num_frames=2, frame_size=(32, 32)):
        super().__init__()
        self.frames = self.load_frames(spritesheet, num_frames, frame_size)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.jogador = jogador
        self.velocidade = 150  # Velocidade do inimigo
        self.animation_time = 0.1  # Tempo entre frames
        self.time_since_last_frame = 0

    def load_frames(self, spritesheet, num_frames, frame_size):
        frames = []
        frame_width = spritesheet.get_width() // num_frames
        frame_height = spritesheet.get_height()
        for i in range(num_frames):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, frame_size)  # Redimensionar o frame
            frames.append(frame)
        return frames

    def update(self, delta_time, inimigos):
        # Atualizar animação
        self.time_since_last_frame += delta_time
        if self.time_since_last_frame >= self.animation_time:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # Mover o inimigo em direção ao jogador
        direction_x = self.jogador.rect.x - self.rect.x
        direction_y = self.jogador.rect.y - self.rect.y
        distance = (direction_x**2 + direction_y**2)**0.5
        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        self.rect.x += int(direction_x * self.velocidade * delta_time)
        self.rect.y += int(direction_y * self.velocidade * delta_time)
        
        # Verificar colisão com o jogador
        if self.rect.colliderect(self.jogador.rect):
            self.jogador.tomar_dano()  # Chamar o método tomar_dano do jogador
            for inimigos in inimigos: #Deleta todos os inimigos
                inimigos.kill()
            self.jogador.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Mover o jogador para o centro
                        
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image):
        super().__init__()
        self.image = pygame.transform.scale(image, (16, 16))  # Redimensionar a imagem da bala
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.velocidade = 500  # Velocidade da bala

    def update(self, delta_time, inimigos):
        if self.direction == 'up':
            self.rect.y -= int(self.velocidade * delta_time)
        elif self.direction == 'down':
            self.rect.y += int(self.velocidade * delta_time)
        elif self.direction == 'left':
            self.rect.x -= int(self.velocidade * delta_time)
        elif self.direction == 'right':
            self.rect.x += int(self.velocidade * delta_time)
        elif self.direction == 'up_left':
            self.rect.y -= int(self.velocidade * delta_time * 0.7071)
            self.rect.x -= int(self.velocidade * delta_time * 0.7071)
        elif self.direction == 'up_right':
            self.rect.y -= int(self.velocidade * delta_time * 0.7071)
            self.rect.x += int(self.velocidade * delta_time * 0.7071)
        elif self.direction == 'down_left':
            self.rect.y += int(self.velocidade * delta_time * 0.7071)
            self.rect.x -= int(self.velocidade * delta_time * 0.7071)
        elif self.direction == 'down_right':
            self.rect.y += int(self.velocidade * delta_time * 0.7071)
            self.rect.x += int(self.velocidade * delta_time * 0.7071)

        # Verificar colisão com inimigos
        inimigo_colidido = pygame.sprite.spritecollideany(self, inimigos)
        if inimigo_colidido:
            inimigo_colidido.kill()
            self.kill()

        # Remover a bala se sair da tela
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

def desenhar_mapa(screen, tmx_data):
    if tmx_data is None:
        print("Erro: tmx_data não foi carregado corretamente.")
        return
    
    # Dimensões do mapa original
    largura_mapa = tmx_data.width * tmx_data.tilewidth
    altura_mapa = tmx_data.height * tmx_data.tileheight

    # Calcular fatores de escala
    escala_x = SCREEN_WIDTH / largura_mapa
    escala_y = SCREEN_HEIGHT / altura_mapa

    # Renderizar mapa redimensionado em uma superfície auxiliar
    map_surface = pygame.Surface((largura_mapa, altura_mapa))
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    pos_x = x * tmx_data.tilewidth
                    pos_y = y * tmx_data.tileheight
                    map_surface.blit(tile, (pos_x, pos_y))
        elif isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "cacttos":
                for obj in layer:
                    # Criar objetos de colisão com redimensionamento correto
                    sprite = pygame.sprite.Sprite()
                    sprite.image = pygame.Surface(
                        (obj.width * escala_x, obj.height * escala_y)
                    )
                    sprite.image.fill((255, 0, 0))  # Cor visível para debug
                    sprite.rect = sprite.image.get_rect(
                        topleft=(obj.x * escala_x, obj.y * escala_y)
                    )
                    grupo_cactus.add(sprite)  # Adicionar ao grupo de colisão

    # Redimensionar a superfície do mapa para caber na tela
    map_surface_scaled = pygame.transform.scale(map_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Desenhar o mapa redimensionado na tela
    screen.blit(map_surface_scaled, (0, 0))

    # Redimensionar a superfície do mapa para caber na tela
    map_surface_scaled = pygame.transform.scale(map_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Desenhar o mapa redimensionado na tela
    screen.blit(map_surface_scaled, (0, 0))

def carregar_proxima_fase(fase_atual, inimigos, screen, time, running):
    fases = [
        'mapas/fases/primeira_fase.tmx',
        'mapas/fases/segunda_fase.tmx',
        'mapas/fases/terceira_fase.tmx'
    ]
    tmx_data = None  
    inimigo_spritesheet = None 

    if fase_atual < len(fases) - 1:
        transicao_fase(time, screen, 1.5)  

        fase_atual += 1
        tmx_data = load_pygame(fases[fase_atual])
        inimigo_spritesheet = carregar_spritesheet_inimigo(fase_atual)
        for inimigos in inimigos:  # Deleta todos os inimigos
            inimigos.kill()

        # Animação de transição de entrada
        # transicao_fase(time, screen, 1.5)

        return tmx_data, fase_atual, inimigo_spritesheet, running
    else:
        musica_venceu()
        print("Você completou todas as fases!")

        # Carregar a imagem de vitória
        victory_image = pygame.image.load('images/menu/win.png')

        # Fazer o efeito de fade-in
        for alpha in range(0, 256):
            victory_image.set_alpha(alpha)
            screen.fill((0, 0, 0))  # Preencher a tela com preto
            screen.blit(victory_image, (0, 0))
            pygame.display.update()
            pygame.time.delay(10)  # Tempo de delay para controlar a velocidade do fade-in

        running = False

        # Esperar por um evento de tecla ou clique do mouse para voltar ao menu
        esperando = True
        while esperando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    esperando = False

        parar_musica()
        return None, fase_atual, None, running
        
def carregar_spritesheet_inimigo(fase_atual):
    spritesheets = [
        'images/inimigos/inimigo1.png',
        'images/inimigos/inimigo2.png',
        'images/inimigos/inimigo3.png'
    ]
    if fase_atual < len(spritesheets):
        return pygame.image.load(spritesheets[fase_atual]).convert_alpha()
    else:
        return pygame.image.load(spritesheets[0]).convert_alpha()  # Default

def jogar(screen, tmx_data, fase_atual=0):
    # Criar o relógio para controle de delta time
    clock = pygame.time.Clock()

    # Carregar a imagem da bala
    bala_image = pygame.image.load('images/outros/tiro.png').convert_alpha()

    # Criar o jogador
    spritesheets = {
        # IDLE
        'idle_down': pygame.image.load('images/cowboy_spriteshit/idle/idle_down.png').convert_alpha(),
        'idle_up': pygame.image.load('images/cowboy_spriteshit/idle/idle_up.png').convert_alpha(),
        'idle_left': pygame.image.load('images/cowboy_spriteshit/idle/idle_down.png').convert_alpha(),
        'idle_right': pygame.image.load('images/cowboy_spriteshit/idle/idle_right.png').convert_alpha(),

        # WALK
        'walk_down': pygame.image.load('images/cowboy_spriteshit/walk/walk_down.png').convert_alpha(),
        'walk_up': pygame.image.load('images/cowboy_spriteshit/walk/walk_up.png').convert_alpha(),
        'walk_left': pygame.image.load('images/cowboy_spriteshit/walk/walk_left.png').convert_alpha(),
        'walk_right': pygame.image.load('images/cowboy_spriteshit/walk/walk_right.png').convert_alpha(),

        # ATTACK
        'attack_down': pygame.image.load('images/cowboy_spriteshit/attack/attack_down.png').convert_alpha(),
        'attack_up': pygame.image.load('images/cowboy_spriteshit/attack/attack_up.png').convert_alpha(),
        'attack_left': pygame.image.load('images/cowboy_spriteshit/attack/attack_left.png').convert_alpha(),
        'attack_right': pygame.image.load('images/cowboy_spriteshit/attack/attack_right.png').convert_alpha(),
        'attack_up_left': pygame.image.load('images/cowboy_spriteshit/attack/attack_up.png').convert_alpha(),  # Corrigido
        'attack_up_right': pygame.image.load('images/cowboy_spriteshit/attack/attack_up.png').convert_alpha(),  # Corrigido
        'attack_down_left': pygame.image.load('images/cowboy_spriteshit/attack/attack_down.png').convert_alpha(),  # Corrigido
        'attack_down_right': pygame.image.load('images/cowboy_spriteshit/attack/attack_down.png').convert_alpha(),  # Corrigido

        # MORTE 
        'dead': pygame.image.load('images/cowboy_spriteshit/death/dead.png').convert_alpha(),
    }

    jogador = Jogador(320, 320, spritesheets, bala_image)  # Posição inicial do jogador
    grupo_jogador = pygame.sprite.Group(jogador)

    inimigo_spritesheet = carregar_spritesheet_inimigo(fase_atual)
    inimigos = CustomGroup()

    # Posições iniciais dos inimigos
    posicoes_iniciais = [
        (-50 + random.randint(-20, 20), 350),  # Esquerda 
        (850 + random.randint(-20, 20), 350),  # Direita
        (SCREEN_WIDTH // 2 + random.randint(-20, 20), -50),  # Meio da tela em cima
        (SCREEN_WIDTH // 2 + random.randint(-20, 20), SCREEN_HEIGHT + 50)  # Meio da tela embaixo
    ]

    all_sprites = CustomGroup()
    all_sprites.add(jogador)

    # Função para criar inimigos
    def criar_inimigos(tempo_restante):
        if len(inimigos) <= 50:  # Limite de 50 inimigos na tela
            num_inimigos = random.randint(1, 2) + int((60 - tempo_restante) // 10)
            num_inimigos = min(num_inimigos, len(posicoes_iniciais))  
            posicoes_selecionadas = random.sample(posicoes_iniciais, num_inimigos)
            for pos in posicoes_selecionadas:
                inimigo = Inimigo(pos[0], pos[1], jogador, inimigo_spritesheet, frame_size=(48, 48))
                inimigos.add(inimigo)
                all_sprites.add(inimigo)

    # Criar inimigos iniciais
    criar_inimigos(60)
    
    desenhar_mapa(screen, tmx_data)  # Renderizar o mapa inicialmente

    inimigo_timer = 5
    inimigo_intervalo = 2  # Intervalo de tempo para gerar novos inimigos

    tempo_total = 60  # Tempo total da fase em segundos
    tempo_inicio = time.time()
     
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # DELTATIME 60FPS
        inimigo_timer += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                parar_musica()

        # Atualizar jogador
        teclas = pygame.key.get_pressed()
        jogador.update(teclas, delta_time)
        inimigos.update(delta_time, inimigos)
        
        # Atualizar balas e verificar colisões
        jogador.balas.update(delta_time, inimigos)

        #Calcular o tempo restante
        tempo_restante = tempo_total - (time.time() - tempo_inicio)

        # Gerar novos inimigos a cada intervalo de tempo
        if inimigo_timer >= inimigo_intervalo:
            criar_inimigos(tempo_restante)
            inimigo_timer = 0

        # Verificar se o tempo da fase acabou
        if tempo_restante <= 0:
            tmx_data, fase_atual, inimigo_spritesheet, running = carregar_proxima_fase(fase_atual, inimigos, screen, time, running)
            tempo_inicio = time.time()  # Reiniciar o tempo para a nova fase
            jogador.vidas = 5 #Vidas do jogador

        # Redesenhar o mapa e os elementos
        screen.fill((0, 0, 0))  #Fundo preto
        desenhar_mapa(screen, tmx_data)
        all_sprites.draw(screen)
        jogador.balas.draw(screen)  # Desenhar balas

        # Mostrar contador de vidas na tela
        font = pygame.font.Font(None, 36)
        
        # Sombra do texto de vidas
        vidas_shadow = font.render(f'Vidas: {jogador.vidas}', True, (0, 0, 0))
        screen.blit(vidas_shadow, (12, 12))
        
        # Texto de vidas
        vidas_text = font.render(f'Vidas: {jogador.vidas}', True, (255, 255, 255))
        screen.blit(vidas_text, (10, 10))
        
        # Mostrar o tempo restante na tela
        # Sombra do texto de tempo
        tempo_shadow = font.render(f'Tempo: {int(tempo_restante)}', True, (0, 0, 0))
        screen.blit(tempo_shadow, (SCREEN_WIDTH - 148, 12))
        
        # Texto de tempo
        tempo_text = font.render(f'Tempo: {int(tempo_restante)}', True, (255, 255, 255))
        screen.blit(tempo_text, (SCREEN_WIDTH - 150, 10))

         # Verificar se o jogador perdeu todas as vidas
        if jogador.vidas <= 0:
            musica_derrota()
            print("Game Over")

            # Carregar a imagem de vitória
            imagem_derotta = pygame.image.load('images/menu/fim_jogo.png')

            # Fazer o efeito de fade-in
            for alpha in range(0, 256):
                imagem_derotta.set_alpha(alpha)
                screen.fill((0, 0, 0))  # Preencher a tela com preto
                screen.blit(imagem_derotta, (0, 0))
                pygame.display.update()
                pygame.time.delay(10)  # Tempo de delay para controlar a velocidade do fade-in

            running = False
            parar_musica()

        #Mostrar FPS no console
        #print(clock.get_fps())

        # Atualizar a tela
        pygame.display.flip()
