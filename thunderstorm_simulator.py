import pygame
import random
import time
import numpy as np
from scipy.signal import butter, lfilter
import sounddevice as sd
import threading

# Inicialização do pygame
pygame.init()

# Configurações de tela
screen_width, screen_height = 1080, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simulador de Raios e Chuva")
is_fullscreen = False
clock = pygame.time.Clock()

# Carregamento de sons de trovão
thunder_sounds = [pygame.mixer.Sound(f"sounds/thunder_{i}.wav") for i in range(1, 11)]

# Volumes iniciais
volumes = {"thunder": 0.5, "rain": 0.5, "drops": 0.5}

# Controle do modal
modal_open = False

# Variáveis para controle de relâmpagos e intensidade
flash_active = False
flash_end_time = 0
menu_button_clicked = False
intensity_levels = {
    "Low": [random.randint(30, 60), random.randint(30, 60)],
    "Medium": [random.randint(20, 40), random.randint(20, 40)],
    "High": [random.randint(10, 20), random.randint(10, 20)]
}
current_intensity = "High"
thunder_intervals = intensity_levels[current_intensity]

# Alternar tela cheia
def toggle_fullscreen():
    global is_fullscreen, screen
    if is_fullscreen:
        screen = pygame.display.set_mode((screen_width, screen_height))
    else:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    is_fullscreen = not is_fullscreen

# Modal e menus
def draw_menu():
    font = pygame.font.Font(None, 36)
    text = font.render(f"Intensity: {current_intensity}", True, (255, 255, 255))
    button_rect = pygame.Rect(screen_width - 255, 10, 240, 50)
    pygame.draw.rect(screen, (50, 50, 50), button_rect)
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
    screen.blit(text, (screen_width - 250, 20))
    return button_rect

def draw_modal():
    modal_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
    pygame.draw.rect(screen, (30, 30, 30), modal_rect)
    pygame.draw.rect(screen, (255, 255, 255), modal_rect, 2)

    font = pygame.font.Font(None, 36)
    texts = ["Thunder", "Rain", "Drops"]

    for i, text in enumerate(texts):
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (modal_rect.x + 50, modal_rect.y + 50 + i * 100))

        slider_x = modal_rect.x + 200
        slider_y = modal_rect.y + 50 + i * 100 + 10
        slider_width = 300
        slider_height = 10

        pygame.draw.rect(screen, (50, 50, 50), (slider_x, slider_y, slider_width, slider_height))

        handle_x = slider_x + int(volumes[text.lower()] * slider_width)
        handle_y = slider_y - 5
        handle_width = 10
        handle_height = 20

        pygame.draw.rect(screen, (255, 255, 255), (handle_x, handle_y, handle_width, handle_height))

def handle_modal_event(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_x, mouse_y = event.pos
        modal_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)

        if modal_rect.collidepoint(mouse_x, mouse_y):
            for i, key in enumerate(["thunder", "rain", "drops"]):
                slider_x = modal_rect.x + 200
                slider_y = modal_rect.y + 50 + i * 100 + 10
                slider_width = 300
                slider_height = 10

                if slider_y - 5 <= mouse_y <= slider_y + slider_height + 5 and slider_x <= mouse_x <= slider_x + slider_width:
                    volumes[key] = (mouse_x - slider_x) / slider_width

# Funções de geração de chuva e som
def filtro_passa_baixa(dados, cutoff, fs, ordem=8):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(ordem, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, dados)

def gerar_ruido_chuva(tamanho, taxa_amostragem=48100, intensidade=2.0):
    ruido = np.random.normal(0, 0.20 * intensidade, tamanho)
    chuva_suave = filtro_passa_baixa(ruido, cutoff=1800, fs=taxa_amostragem)
    return np.clip(chuva_suave, -1.0, 1.0)

#def adicionar_pingos(chuva, taxa_amostragem=40100, intensidade_escala=0.2, num_base=2):
#    tamanho = len(chuva)
#    num_pingos = num_base + np.random.randint(1, 2)
#    posicoes = np.random.randint(0, tamanho, num_pingos)
#    intensidades = np.random.uniform(0.3, 0.5, num_pingos) * intensidade_escala
#    duracoes = np.random.randint(50, 80, num_pingos)

    for p, i, d in zip(posicoes, intensidades, duracoes):
        fim = min(p + d, tamanho)
        janela = np.hanning(fim - p)
        chuva[p:fim] += i * janela

        frequencia_base = np.random.uniform(2, 4)
        modulação = np.random.uniform(0.6, 1.2)
        componente_harmonica = i * np.sin(2 * np.pi * np.linspace(0, modulação, fim - p) * frequencia_base)
        chuva[p:fim] += componente_harmonica * janela

        salpicos = np.random.uniform(-0.005, 0.005, fim - p) * janela + 0.3 
        chuva[p:fim] += salpicos - 0.2

    return np.clip(chuva, -1.0, 1.0)

def gerar_chuva(tamanho, taxa_amostragem=44100, intensidade_escala=1.0, num_base=3):
    chuva_base = gerar_ruido_chuva(tamanho, taxa_amostragem, intensidade_escala)
   # chuva_com_pingos = adicionar_pingos(chuva_base, taxa_amostragem, intensidade_escala, num_base)
    return chuva_base

def tocar_chuva():
    taxa_amostragem = 44100
    bloco_tempo = 1.0
    bloco_tamanho = int(taxa_amostragem * bloco_tempo)

    def callback(outdata, frames, time, status):
        bloco = gerar_chuva(bloco_tamanho, taxa_amostragem)
        outdata[:] = bloco.reshape(-1, 1) * volumes["rain"]

    threading.Thread(target=lambda: sd.OutputStream(
        channels=1,
        samplerate=taxa_amostragem,
        blocksize=bloco_tamanho,
        callback=callback,
        latency="high").start(), daemon=True).start()

# Continuação no próximo bloco...
# Controle do loop principal e lógica de eventos
def desenhar_botao_modal():
    circle_pos = (screen_width - 300, 40)
    circle_radius = 20
    pygame.draw.circle(screen, (50, 50, 200), circle_pos, circle_radius)
    return pygame.Rect(circle_pos[0] - circle_radius, circle_pos[1] - circle_radius, circle_radius * 2, circle_radius * 2)

running = True
next_thunder_time = time.time() + random.choice(thunder_intervals)
tocar_chuva()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            toggle_fullscreen()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Interação com modal
            if modal_open:
                handle_modal_event(event)
                modal_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
                if not modal_rect.collidepoint(mouse_pos):
                    modal_open = False
            else:
                # Abrir o modal ao clicar no botão
                if desenhar_botao_modal().collidepoint(mouse_pos):
                    modal_open = True

                # Detectar clique inicial no botão de intensidade
                if draw_menu().collidepoint(mouse_pos):
                    menu_button_clicked = True

        if event.type == pygame.MOUSEBUTTONUP:
            menu_button_clicked = False

    # Lógica de alternância de intensidade (somente no clique inicial)
    if menu_button_clicked and not modal_open:
        menu_button_clicked = False  # Resetar estado após alternância
        keys = list(intensity_levels.keys())
        current_index = keys.index(current_intensity)
        current_intensity = keys[(current_index + 1) % len(keys)]
        thunder_intervals = intensity_levels[current_intensity]

    # Atualização da tela
    screen.fill((0, 0, 0))

    # Relâmpago ativo
    if flash_active and time.time() < flash_end_time:
        screen.fill((255, 255, 255))
    elif flash_active:
        flash_active = False

    # Botão do modal
    desenhar_botao_modal()
    draw_menu()

    # Modal
    if modal_open:
        draw_modal()

    # Relâmpago e trovão
    if time.time() > next_thunder_time:
        pygame.mixer.Sound.play(random.choice(thunder_sounds))
        flash_active = True
        flash_end_time = time.time() + 0.1  # Relâmpago dura 0.1 segundos
        next_thunder_time = time.time() + random.choice(thunder_intervals)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
