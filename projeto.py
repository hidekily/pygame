import pygame
import sys
import random
import os
from datetime import datetime

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Turn-Based Battle Game")
clock = pygame.time.Clock()

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (50, 100, 200)
AMARELO = (255, 200, 0)
ROXO = (150, 50, 150)
CINZA = (100, 100, 100)

# Estados do jogo
MENU = 0
SELECAO = 1
BATALHA = 2
FIM = 3
estado = MENU

# Event Log
event_log = []

def log_event(message):
    """Registra eventos no log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    event_log.append(log_entry)
    print(log_entry)

def save_log():
    """Salva o log em arquivo txt"""
    try:
        with open("game_event_log.txt", "w", encoding="utf-8") as f:
            f.write("=== TURN-BASED BATTLE GAME - EVENT LOG ===\n\n")
            for entry in event_log:
                f.write(entry + "\n")
        log_event("Event log saved to file")
    except Exception as e:
        print(f"Error saving log: {e}")

# ===== CLASSE UNIT (Personagem) =====
class Unit:
    """
    Classe que representa uma unidade no jogo
    Atributos: nome, HP, ATK, DEF, EXP, Rank, profession (Warrior/Tanker)
    """
    def __init__(self, nome, profession, sprite_path=None):
        self.nome = nome
        self.profession = profession  # "Warrior" ou "Tanker"
        self.rank = 1
        self.exp = 0
        
        # Atributos baseados na profissão (conforme PDF - Table 1)
        if profession == "Warrior":
            self.hp_max = 100
            self.hp = 100
            self.atk = random.randint(5, 20)  # Range 5-20 para Warrior
            self.defense = random.randint(1, 10)  # Range 1-10 para Warrior
            self.cor = (200, 50, 50)  # Vermelho
        else:  # Tanker
            self.hp_max = 100
            self.hp = 100
            self.atk = random.randint(1, 10)  # Range 1-10 para Tanker
            self.defense = random.randint(5, 15)  # Range 5-15 para Tanker
            self.cor = (100, 70, 40)  # Marrom
        
        self.vivo = True
        
        # Carregar sprite
        self.sprite = None
        if sprite_path and os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path)
                self.sprite = pygame.transform.scale(self.sprite, (100, 100))
            except:
                self.sprite = None
        
        # Indicadores visuais
        self.hover = False
        self.sendo_atacado = False
        self.atacando = False
        self.tempo_efeito = 0
        
        log_event(f"Unit created: {nome} ({profession}) - HP:{self.hp} ATK:{self.atk} DEF:{self.defense}")
    
    def attack(self, target):
        """
        Realiza ataque conforme regras do PDF:
        Damage = attacker.ATK - target.DEF + (random between -5 to 10)
        """
        # Calcular dano
        random_modifier = random.randint(-5, 10)
        damage = self.atk - target.defense + random_modifier
        damage = max(0, damage)  # Dano não pode ser negativo
        
        # Aplicar dano
        target.hp -= damage
        if target.hp <= 0:
            target.hp = 0
            target.vivo = False
        
        # Ganhar EXP (conforme PDF)
        # Atacante ganha EXP baseado no dano causado
        self.gain_exp(damage)
        
        # Alvo ganha EXP baseado na DEF
        target_exp = target.defense
        
        # Bônus de EXP para o alvo (conforme PDF)
        if damage > 10:
            # Ganhou extra 20% EXP
            bonus = int(target_exp * 0.2)
            target_exp += bonus
            log_event(f"{target.nome} gained 20% bonus EXP (damage > 10)")
        elif damage <= 0:
            # Ganhou extra 50% EXP
            bonus = int(target_exp * 0.5)
            target_exp += bonus
            log_event(f"{target.nome} gained 50% bonus EXP (no damage taken)")
        
        target.gain_exp(target_exp)
        
        # Efeitos visuais
        self.atacando = True
        target.sendo_atacado = True
        self.tempo_efeito = pygame.time.get_ticks()
        target.tempo_efeito = pygame.time.get_ticks()
        
        # Log do ataque
        log_event(f"ATTACK: {self.nome} -> {target.nome} | Damage: {damage} | {target.nome} HP: {target.hp}/{target.hp_max}")
        
        if not target.vivo:
            log_event(f"{target.nome} has been defeated!")
        
        return damage
    
    def gain_exp(self, exp_gained):
        """
        Ganha experiência e verifica level up (conforme PDF)
        Level up quando EXP atinge 100
        """
        self.exp += exp_gained
        log_event(f"{self.nome} gained {exp_gained} EXP (Total: {self.exp})")
        
        # Verificar level up
        if self.exp >= 100:
            self.rank += 1
            self.exp -= 100
            log_event(f"LEVEL UP! {self.nome} is now Rank {self.rank}!")
    
    def desenhar(self, x, y, tamanho=100, mostrar_hover=False, e_turno_dele=False):
        """Desenha a unidade na tela"""
        # Limpar efeitos após 300ms (reduzido para menos lag)
        if pygame.time.get_ticks() - self.tempo_efeito > 300:
            self.atacando = False
            self.sendo_atacado = False
        
        rect = pygame.Rect(x, y, tamanho, tamanho)
        
        # Cor de fundo
        cor_fundo = self.cor if self.vivo else (50, 50, 50)
        
        # Efeito de turno dele (borda amarela pulsante)
        if e_turno_dele and self.vivo:
            pulso = abs((pygame.time.get_ticks() % 800) / 400 - 1) * 4 + 2
            pygame.draw.rect(screen, AMARELO, (x-5, y-5, tamanho+10, tamanho+10), int(pulso))
        
        # Efeito de hover
        if mostrar_hover and self.hover and self.vivo:
            pygame.draw.rect(screen, AMARELO, (x-3, y-3, tamanho+6, tamanho+6), 3)
        
        # Efeito de sendo atacado
        if self.sendo_atacado:
            pygame.draw.rect(screen, VERMELHO, (x-2, y-2, tamanho+4, tamanho+4), 5)
        
        # Efeito de atacando
        if self.atacando:
            pygame.draw.rect(screen, VERDE, (x-2, y-2, tamanho+4, tamanho+4), 5)
        
        # Desenhar sprite ou cor
        if self.sprite:
            screen.blit(self.sprite, (x, y))
        else:
            pygame.draw.rect(screen, cor_fundo, rect)
        
        pygame.draw.rect(screen, PRETO, rect, 3)
        
        # Nome à esquerda
        fonte = pygame.font.Font(None, 22)
        texto = fonte.render(self.nome[:12], True, BRANCO)
        screen.blit(texto, (x - texto.get_width() - 12, y + 10))
        
        # Profissão
        fonte_prof = pygame.font.Font(None, 18)
        texto_prof = fonte_prof.render(self.profession, True, CINZA)
        screen.blit(texto_prof, (x - texto_prof.get_width() - 12, y + 30))
        
        # Rank
        texto_rank = fonte_prof.render(f"Lv.{self.rank}", True, AMARELO)
        screen.blit(texto_rank, (x - texto_rank.get_width() - 12, y + 50))
        
        # Barra de vida à direita
        barra_x = x + tamanho + 12
        barra_y = y + 20
        barra_largura = 110
        barra_altura = 10
        
        pygame.draw.rect(screen, VERMELHO, (barra_x, barra_y, barra_largura, barra_altura))
        largura_vida = int((self.hp / self.hp_max) * barra_largura)
        pygame.draw.rect(screen, VERDE, (barra_x, barra_y, largura_vida, barra_altura))
        pygame.draw.rect(screen, PRETO, (barra_x, barra_y, barra_largura, barra_altura), 2)
        
        # HP texto
        hp_fonte = pygame.font.Font(None, 18)
        hp_texto = hp_fonte.render(f"HP: {self.hp}/{self.hp_max}", True, BRANCO)
        screen.blit(hp_texto, (barra_x, barra_y + 12))
        
        # Stats
        stats_y = barra_y + 30
        stats_fonte = pygame.font.Font(None, 16)
        stats = [
            f"ATK: {self.atk}",
            f"DEF: {self.defense}",
            f"EXP: {self.exp}/100"
        ]
        for i, stat in enumerate(stats):
            stat_surf = stats_fonte.render(stat, True, BRANCO)
            screen.blit(stat_surf, (barra_x, stats_y + i * 16))
        
        return rect

# ===== CRIAR 6 PERSONAGENS BASE =====
def criar_personagens_base():
    """Cria 6 opções de personagens (3 Warriors, 3 Tankers)"""
    return [
        ("Warrior", "Guerreiro", (200, 50, 50), "sprites/guerreiro.png"),
        ("Warrior", "Arqueiro", (50, 200, 50), "sprites/arqueiro.png"),
        ("Warrior", "Assassino", (150, 50, 150), "sprites/assassino.png"),
        ("Tanker", "Paladino", (200, 180, 50), "sprites/paladino.png"),
        ("Tanker", "Tanque", (100, 70, 40), "sprites/tanque.png"),
        ("Tanker", "Guardião", (80, 80, 120), "sprites/guardiao.png")
    ]

personagens_base = criar_personagens_base()
time_jogador = []
time_ai = []
selecionados = [False] * 6
mensagem = ""

# Sistema de turnos
ordem_turnos = []
indice_turno_atual = 0
personagem_atual = None

# ===== FUNÇÕES =====
def resetar():
    global time_jogador, time_ai, selecionados, mensagem, estado
    global ordem_turnos, indice_turno_atual, personagem_atual, event_log
    time_jogador = []
    time_ai = []
    selecionados = [False] * 6
    mensagem = ""
    estado = MENU
    ordem_turnos = []
    indice_turno_atual = 0
    personagem_atual = None
    event_log = []
    log_event("Game Reset")

def criar_ordem_turnos():
    """Cria ordem alternada: Jogador1, AI1, Jogador2, AI2, Jogador3, AI3"""
    global ordem_turnos
    ordem_turnos = []
    for i in range(3):
        ordem_turnos.append(("jogador", time_jogador[i]))
        ordem_turnos.append(("ai", time_ai[i]))
    log_event("Turn order created: Player1, AI1, Player2, AI2, Player3, AI3")

def proximo_turno():
    """Avança para o próximo personagem vivo"""
    global indice_turno_atual, personagem_atual
    
    tentativas = 0
    while tentativas < len(ordem_turnos):
        indice_turno_atual = (indice_turno_atual + 1) % len(ordem_turnos)
        time, unit = ordem_turnos[indice_turno_atual]
        
        if unit.vivo:
            personagem_atual = (time, unit)
            
            if time == "jogador":
                mensagem = f"Seu turno: {unit.nome}! Selecione um alvo"
                log_event(f"Player turn: {unit.nome}")
            else:
                mensagem = f"Turno AI: {unit.nome}"
                log_event(f"AI turn: {unit.nome}")
                pygame.time.wait(400)
                executar_turno_ai()
            return
        
        tentativas += 1

def executar_turno_ai():
    """AI escolhe alvo e ataca"""
    global mensagem
    
    time_atual, atacante = personagem_atual
    
    # AI seleciona alvo com menor HP
    alvos_vivos = [p for p in time_jogador if p.vivo]
    if not alvos_vivos:
        return
    
    alvo = min(alvos_vivos, key=lambda x: x.hp)  # Ataca o mais fraco
    dano = atacante.attack(alvo)
    mensagem = f"{atacante.nome} atacou {alvo.nome}! ({dano} de dano)"
    
    if not alvo.vivo:
        mensagem += f" - {alvo.nome} foi derrotado!"
    
    verificar_fim_batalha()
    
    if estado == BATALHA:
        pygame.time.wait(400)
        proximo_turno()

def verificar_fim_batalha():
    global estado, mensagem
    
    jogador_vivos = sum(1 for p in time_jogador if p.vivo)
    ai_vivos = sum(1 for p in time_ai if p.vivo)
    
    if jogador_vivos == 0:
        estado = FIM
        mensagem = "AI TEAM WINS!"
        log_event("GAME OVER: AI Team Victory")
        save_log()
    elif ai_vivos == 0:
        estado = FIM
        mensagem = "PLAYER TEAM WINS!"
        log_event("GAME OVER: Player Team Victory")
        save_log()

def botao(x, y, w, h, texto, cor):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    
    if rect.collidepoint(mouse):
        cor = tuple(min(c + 30, 255) for c in cor)
    
    pygame.draw.rect(screen, cor, rect)
    pygame.draw.rect(screen, BRANCO, rect, 2)
    
    fonte = pygame.font.Font(None, 28)
    texto_surf = fonte.render(texto, True, BRANCO)
    screen.blit(texto_surf, (x + w//2 - texto_surf.get_width()//2, y + h//2 - texto_surf.get_height()//2))
    
    return rect

# ===== LOOP PRINCIPAL =====
running = True
log_event("Game Started")

while running:
    screen.fill((20, 20, 40))
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_log()
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # MENU
            if estado == MENU:
                btn = pygame.Rect(500, 350, 200, 60)
                if btn.collidepoint(pos):
                    estado = SELECAO
                    log_event("Entered character selection")
            
            # SELEÇÃO
            elif estado == SELECAO:
                # Clicar nos personagens
                for i in range(6):
                    col = i % 3
                    row = i // 3
                    x = 200 + col * 280
                    y = 180 + row * 180
                    rect = pygame.Rect(x, y, 100, 100)
                    
                    if rect.collidepoint(pos):
                        if selecionados[i]:
                            selecionados[i] = False
                            profession, nome_base, cor, sprite = personagens_base[i]
                            time_jogador = [p for p in time_jogador if p.nome != nome_base]
                            log_event(f"Deselected: {nome_base}")
                        elif len(time_jogador) < 3:
                            selecionados[i] = True
                            profession, nome_base, cor, sprite = personagens_base[i]
                            nova_unit = Unit(nome_base, profession, sprite)
                            time_jogador.append(nova_unit)
                            log_event(f"Selected: {nome_base} ({profession})")
                
                # Botão iniciar
                if len(time_jogador) == 3:
                    btn = pygame.Rect(500, 580, 200, 50)
                    if btn.collidepoint(pos):
                        # AI cria time (conforme PDF: random profession + nome AI##)
                        log_event("AI Team Setup initiated")
                        for i in range(3):
                            profession_random = random.choice(["Warrior", "Tanker"])
                            nome_ai = f"AI{random.randint(10, 99)}"
                            unit_ai = Unit(nome_ai, profession_random)
                            time_ai.append(unit_ai)
                        
                        criar_ordem_turnos()
                        indice_turno_atual = -1
                        estado = BATALHA
                        log_event("Battle Started!")
                        proximo_turno()
            
            # BATALHA
            elif estado == BATALHA:
                if personagem_atual and personagem_atual[0] == "jogador":
                    # Jogador ataca
                    for i, p in enumerate(time_ai):
                        x = 800
                        y = 120 + i * 180
                        rect = pygame.Rect(x, y, 100, 100)
                        
                        if rect.collidepoint(pos) and p.vivo:
                            time_atual, atacante = personagem_atual
                            dano = atacante.attack(p)
                            mensagem = f"{atacante.nome} causou {dano} de dano em {p.nome}!"
                            
                            if not p.vivo:
                                mensagem += f" - {p.nome} derrotado!"
                            
                            verificar_fim_batalha()
                            
                            if estado == BATALHA:
                                pygame.time.wait(400)
                                proximo_turno()
                            break
            
            # FIM
            elif estado == FIM:
                btn1 = pygame.Rect(350, 420, 180, 50)
                btn2 = pygame.Rect(670, 420, 180, 50)
                
                if btn1.collidepoint(pos):
                    resetar()
                elif btn2.collidepoint(pos):
                    resetar()
                    estado = SELECAO
    
    # ===== DESENHAR =====
    
    # MENU
    if estado == MENU:
        fonte_titulo = pygame.font.Font(None, 80)
        titulo = fonte_titulo.render("TURN-BASED BATTLE", True, AMARELO)
        screen.blit(titulo, (600 - titulo.get_width()//2, 150))
        
        fonte_sub = pygame.font.Font(None, 28)
        sub = fonte_sub.render("ITGP2008 Assignment Project", True, BRANCO)
        screen.blit(sub, (600 - sub.get_width()//2, 240))
        
        botao(500, 350, 200, 60, "START GAME", VERDE)
        
        # Instruções
        fonte_inst = pygame.font.Font(None, 20)
        instrucoes = [
            "• Select 3 units for your team",
            "• Each unit: Warrior or Tanker class",
            "• Turn-based combat system",
            "• Gain EXP and level up units"
        ]
        for i, inst in enumerate(instrucoes):
            texto = fonte_inst.render(inst, True, BRANCO)
            screen.blit(texto, (600 - texto.get_width()//2, 470 + i * 28))
    
    # SELEÇÃO
    elif estado == SELECAO:
        fonte = pygame.font.Font(None, 44)
        titulo = fonte.render("SELECT YOUR TEAM (3 UNITS)", True, BRANCO)
        screen.blit(titulo, (600 - titulo.get_width()//2, 40))
        
        cor_contador = VERDE if len(time_jogador) == 3 else BRANCO
        contador = fonte.render(f"{len(time_jogador)}/3 Selected", True, cor_contador)
        screen.blit(contador, (600 - contador.get_width()//2, 100))
        
        # Desenhar 6 personagens (3x2 grid)
        for i in range(6):
            col = i % 3
            row = i // 3
            x = 200 + col * 280
            y = 180 + row * 180
            
            profession, nome, cor, sprite = personagens_base[i]
            
            # Card
            pygame.draw.rect(screen, cor, (x, y, 100, 100))
            pygame.draw.rect(screen, PRETO, (x, y, 100, 100), 3)
            
            # Hover
            rect = pygame.Rect(x, y, 100, 100)
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, AMARELO, (x-2, y-2, 104, 104), 3)
            
            # Selecionado
            if selecionados[i]:
                pygame.draw.rect(screen, AMARELO, (x-4, y-4, 108, 108), 5)
            
            # Nome
            fonte_nome = pygame.font.Font(None, 20)
            nome_surf = fonte_nome.render(nome, True, BRANCO)
            screen.blit(nome_surf, (x + 50 - nome_surf.get_width()//2, y + 35))
            
            # Profissão
            fonte_prof = pygame.font.Font(None, 16)
            prof_surf = fonte_prof.render(profession, True, CINZA)
            screen.blit(prof_surf, (x + 50 - prof_surf.get_width()//2, y + 55))
            
            # Stats
            fonte_stats = pygame.font.Font(None, 14)
            if profession == "Warrior":
                stats = "ATK:5-20 DEF:1-10"
            else:
                stats = "ATK:1-10 DEF:5-15"
            stats_surf = fonte_stats.render(stats, True, BRANCO)
            screen.blit(stats_surf, (x + 50 - stats_surf.get_width()//2, y + 75))
        
        if len(time_jogador) == 3:
            botao(500, 580, 200, 50, "START BATTLE", AZUL)
    
    # BATALHA
    elif estado == BATALHA:
        fonte_titulo = pygame.font.Font(None, 44)
        titulo = fonte_titulo.render("⚔️ BATTLE ⚔️", True, AMARELO)
        screen.blit(titulo, (600 - titulo.get_width()//2, 15))
        
        # Time Jogador (esquerda)
        fonte_time = pygame.font.Font(None, 28)
        texto_jog = fonte_time.render("YOUR TEAM", True, VERDE)
        screen.blit(texto_jog, (40, 80))
        
        pos_atacante = None
        for i, p in enumerate(time_jogador):
            x = 180
            y = 120 + i * 180
            
            e_turno_dele = personagem_atual and personagem_atual[0] == "jogador" and personagem_atual[1] == p
            p.desenhar(x, y, 100, False, e_turno_dele)
        
        # Time AI (direita)
        texto_ai = fonte_time.render("AI TEAM", True, VERMELHO)
        screen.blit(texto_ai, (970, 80))
        
        turno_jogador = personagem_atual and personagem_atual[0] == "jogador"
        
        for i, p in enumerate(time_ai):
            x = 800
            y = 120 + i * 180
            
            p.hover = False
            rect = pygame.Rect(x, y, 100, 100)
            if rect.collidepoint(mouse_pos) and turno_jogador and p.vivo:
                p.hover = True
            
            p.desenhar(x, y, 100, turno_jogador)
        
        # Mensagem
        fonte_msg = pygame.font.Font(None, 24)
        msg_surf = fonte_msg.render(mensagem[:70], True, BRANCO)
        msg_rect = msg_surf.get_rect(center=(600, 650))
        pygame.draw.rect(screen, PRETO, 
                        (msg_rect.x - 10, msg_rect.y - 5, 
                         msg_rect.width + 20, msg_rect.height + 10))
        pygame.draw.rect(screen, AMARELO, 
                        (msg_rect.x - 10, msg_rect.y - 5, 
                         msg_rect.width + 20, msg_rect.height + 10), 2)
        screen.blit(msg_surf, msg_rect)
        
        # Indicador de turno
        if personagem_atual:
            time_atual, pers_atual = personagem_atual
            cor_turno = VERDE if time_atual == "jogador" else VERMELHO
            turno_texto = f"TURN: {pers_atual.nome}"
            
            turno_surf = fonte_titulo.render(turno_texto, True, cor_turno)
            turno_rect = turno_surf.get_rect(center=(600, 60))
            
            pygame.draw.rect(screen, PRETO, 
                            (turno_rect.x - 12, turno_rect.y - 6, 
                             turno_rect.width + 24, turno_rect.height + 12))
            pygame.draw.rect(screen, cor_turno, 
                            (turno_rect.x - 12, turno_rect.y - 6, 
                             turno_rect.width + 24, turno_rect.height + 12), 3)
            screen.blit(turno_surf, turno_rect)
    
    # FIM
    elif estado == FIM:
        fonte_titulo = pygame.font.Font(None, 70)
        cor_fim = VERDE if "PLAYER" in mensagem else VERMELHO
        titulo = fonte_titulo.render(mensagem, True, cor_fim)
        screen.blit(titulo, (600 - titulo.get_width()//2, 220))
        
        fonte_stats = pygame.font.Font(None, 28)
        jogador_vivos = sum(1 for p in time_jogador if p.vivo)
        ai_vivos = sum(1 for p in time_ai if p.vivo)
        stats_texto = f"Final Score: Your Team {jogador_vivos} x {ai_vivos} AI Team"
        stats = fonte_stats.render(stats_texto, True, BRANCO)
        screen.blit(stats, (600 - stats.get_width()//2, 320))
        
        # Info sobre log
        log_info = fonte_stats.render("Event log saved to: game_event_log.txt", True, CINZA)
        screen.blit(log_info, (600 - log_info.get_width()//2, 360))
        
        botao(350, 420, 180, 50, "MAIN MENU", AZUL)
        botao(670, 420, 180, 50, "PLAY AGAIN", VERDE)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()