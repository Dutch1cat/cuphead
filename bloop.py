import pygame
import os

# === Configurazione iniziale ===
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# === Classe Bloop ===
class Bloop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ground_y = y
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 1
        self.jump_strength = -20
        self.direction = "right"
        self.state = "idle"
        self.previous_state = "idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 13
        self.frame_delays = {
            "idle": 10,
            "run": 8,
            "jump": 8
        }
        self.jump_count = 0
        self.max_jumps = 2
        self.jump_pressed = False
        self.animations = self.load_animations()
        self.projectiles = []
        self.ranged_cooldown = 1500  # in millisecondi
        self.last_ranged_attack = 0
        self.melee_cooldown = 750  # ms
        self.melee_duration = 250  # ms
        self.last_melee_attack = 0
        self.melee_active = False
        self.melee_start_time = 0
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.dead = False
        self.die_sprite = None
        self.die_y = self.y
        self.die_speed = -2



    def load_animations(self):
        animations = {}
        target_size = (64, 64)  # nuova dimensione
        # === Attacchi ===
        attack_path = "images/bloop/attacks"
        melee_img = pygame.image.load(os.path.join(attack_path, "melee.png")).convert_alpha()
        melee_img = pygame.transform.scale(melee_img, (64, 64))
        animations["melee"] = [melee_img]

        long_img = pygame.image.load(os.path.join(attack_path, "long.png")).convert_alpha()
        animations["long"] = [long_img]  # già 64x64, non serve ridimensionare

        for state in ["idle", "run", "jump"]:
            for direction in ["left", "right"]:
                path = f"images/bloop/{state}_{direction}"
                frames = []
                for i in range(10):  # supporta fino a 10 frame
                    file = f"frame_{i}.png"
                    full_path = os.path.join(path, file)
                    if os.path.exists(full_path):
                        image = pygame.image.load(full_path).convert_alpha()
                        image = pygame.transform.scale(image, target_size)
                        frames.append(image)
                animations[f"{state}_{direction}"] = frames
        return animations

    def update(self, keys):
        self.previous_state = self.state

        # === Movimento orizzontale ===
        self.vel_x = 0
        if keys[pygame.K_LEFT] and not self.dead:
            self.vel_x = -5
            self.direction = "left"
        elif keys[pygame.K_RIGHT] and not self.dead:
            self.vel_x = 5
            self.direction = "right"

        # === Salto (solo se a terra) ===
        if keys[pygame.K_SPACE]:
            if not self.jump_pressed and self.jump_count < self.max_jumps and not self.dead:
                self.vel_y = self.jump_strength
                self.state = "jump"
                self.frame_index = 0
                self.jump_count += 1
                self.jump_pressed = True
        else:
            self.jump_pressed = False
        if keys[pygame.K_2] and not self.dead:
            self.ranged_attack()
        if keys[pygame.K_1] and not self.dead:
            self.melee_attack()


        # === Gestione durata attacco melee ===
        if self.melee_active:
            if pygame.time.get_ticks() - self.melee_start_time >= self.melee_duration:
                self.melee_active = False
                self.state = "idle"

        # === Fisica verticale ===
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.x += self.vel_x
        # === Limiti movimento ===
        self.x = max(0, min(self.x, WIDTH - 64))  # limita a sinistra/destra
        self.y = max(0, min(self.y, HEIGHT - 64))

        # === Collisione con il suolo ===
        if self.y >= self.ground_y:
            self.jump_count = 0
            self.y = self.ground_y
            self.vel_y = 0
            if self.state == "jump":
                self.state = "idle"

        # === Gestione stato ===
        if self.state != "jump":  # salto ha priorità
            if self.vel_x != 0:
                self.state = "run"
            else:
                self.state = "idle"

        # === Reset frame se cambia stato ===
        if self.state != self.previous_state:
            self.frame_index = 0
            self.frame_timer = 0

        # === Animazione ===
        self.frame_timer += 1
        current_delay = self.frame_delays.get(self.state, 10)
        if self.frame_timer >= current_delay:
            self.frame_timer = 0
            frames = self.animations.get(f"{self.state}_{self.direction}", [])
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)
        for p in self.projectiles:
            p["x"] += p["vel"]
        if self.current_hp <= 0 and not self.dead:
            self.dead = True
            self.state = "die"
            self.frame_index = 0
            self.frame_timer = 0
            self.vel_x = 0
            self.vel_y = 0
            die_path = f"images/bloop/die_{self.direction}"
            frame_1_path = os.path.join(die_path, "frame_1.png")
            if os.path.exists(frame_1_path):
                self.die_sprite = pygame.image.load(frame_1_path).convert_alpha()
                self.die_sprite = pygame.transform.scale(self.die_sprite, (64, 64))
            self.die_y = self.y

        if self.dead:
            self.y = self.ground_y  # blocca a terra
            self.vel_x = 0
            self.vel_y = 0
            self.die_y += self.die_speed
            if self.die_y <= 200:
                raise Exception("bloop is defeated!")

    def melee_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_melee_attack >= self.melee_cooldown:
            self.state = "melee"
            self.frame_index = 0
            self.melee_active = True
            self.melee_start_time = current_time
            self.last_melee_attack = current_time

    def ranged_attack(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ranged_attack >= self.ranged_cooldown:
            self.state = "long"
            self.frame_index = 0
            direction = 1 if self.direction == "right" else -1
            projectile = {
                "x": self.x + 32,
                "y": self.y + 32,
                "vel": 10 * direction,
                "damage": 8,
                "image": self.animations["long"][0],
                "active": True
            }
            self.projectiles.append(projectile)
            self.last_ranged_attack = current_time

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)

    def get_melee_rect(self):
        offset = 64 if self.direction == "right" else -64
        return pygame.Rect(self.x + offset, self.y, 64, 64)

    def get_projectile_rects(self):
        return [pygame.Rect(p["x"], p["y"], 64, 64) for p in self.projectiles]
    def get_rect(self):
        return pygame.Rect(self.x, self.y, 64, 64)
    def draw(self, surface):
        frames = self.animations.get(f"{self.state}_{self.direction}", [])
        for p in self.projectiles:
            if p["active"]:
                surface.blit(p["image"], (p["x"], p["y"]))
        if self.melee_active:
            offset = 64 if self.direction == "right" else -64
            surface.blit(self.animations["melee"][0], (self.x + offset, self.y))
        if self.dead:
            die_frame_0_path = f"images/bloop/die_{self.direction}/frame_0.png"
            if os.path.exists(die_frame_0_path):
                die_img = pygame.image.load(die_frame_0_path).convert_alpha()
                die_img = pygame.transform.scale(die_img, (64, 64))
                surface.blit(die_img, (self.x, self.y))
            if self.die_sprite:
                surface.blit(self.die_sprite, (self.x, self.die_y))
        elif frames:
            index = self.frame_index % len(frames)
            surface.blit(frames[index], (self.x, self.y))
        

        
