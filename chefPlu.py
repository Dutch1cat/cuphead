import pygame
import random

SCREEN_WIDTH = 800

class ChefPlu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64

        self.max_hp = 400
        self.current_hp = 400

        self.attack_cooldown = 1000
        self.last_attack_time = 0
        self.attacking = False

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 10
        self.melee_hit_registered = False

        self.direction = "right"
        self.current_animation = "idle_right"

        self.stoccata_cooldown = 6000
        self.last_stoccata_time = 0
        self.fiammata_active = False
        self.fiammata_charging = False
        self.stoccata_charge_start = 0
        self.stoccata_speed = 10
        self.stoccata_direction = "right"
        self.stoccata_start_time = 0
        self.stoccata_duration = 3000

        self.fiammata_charging = False
        self.fiammata_active = False
        self.fiammata_charge_start = 0
        self.fiammata_start_time = 0
        self.fiammata_duration = 1500  # Durata dell'effetto attivo


        self.ability_cooldown = 2000
        self.last_ability_time = 0
        self.current_ability = None

        self.spawn_frame_index = 0
        self.spawn_frame_timer = 0
        self.spawn_frame_speed = 10
        self.spawning = False
        self.spawn_start_time = 0
        self.spawn_duration = 2000

        self.animations = {
            "idle_left": [pygame.image.load(f"images/plu/idle_left/frame_{i}.png").convert_alpha() for i in range(2)],
            "idle_right": [pygame.image.load(f"images/plu/idle_right/frame_{i}.png").convert_alpha() for i in range(2)],
            "fiammata_left": [
                              pygame.image.load("images/plu/fiammata_left/frame_1.png").convert_alpha(),
                              pygame.image.load("images/plu/fiammata_left/frame_2.png").convert_alpha()],
            "fiammata_right": [
                               pygame.image.load("images/plu/fiammata_right/frame_1.png").convert_alpha(),
                               pygame.image.load("images/plu/fiammata_right/frame_2.png").convert_alpha()],
            "sprint_left": [pygame.image.load(f"images/plu/sprint_left/frame_{i}.png").convert_alpha() for i in range(2)],
            "sprint_right": [pygame.image.load(f"images/plu/sprint_right/frame_{i}.png").convert_alpha() for i in range(2)],
            "salsa_drop": [
                           pygame.image.load("images/plu/salsa_drop/frame_1.png").convert_alpha(),
                           pygame.image.load("images/plu/salsa_drop/frame_2.png").convert_alpha()],
        }
        self.fiammata_hit_registered = False
        self.image = self.animations[self.current_animation][self.frame_index]

    def update(self, bloop):
        current_time = pygame.time.get_ticks()
        self.direction = "left" if bloop.x < self.x else "right"

        # --- Handle Active Abilities ---
        # --- Fiammata Charging ---
        if self.fiammata_charging:
            self.attacking = False
            self.current_animation = f"fiammata_{self.direction}"
            self.image = pygame.transform.scale(self.animations[self.current_animation][1], (self.width, self.height))
            if current_time - self.fiammata_charge_start >= 1000:
                self.fiammata_charging = False
                self.fiammata_active = True
                self.fiammata_start_time = current_time
                self.frame_index = 2

        # --- Fiammata Active ---
        elif self.fiammata_active:
            if current_time - self.fiammata_start_time >= self.fiammata_duration:
                self.fiammata_active = False
                self.current_ability = None
            else:
                self.attacking = False
                self.current_animation = f"fiammata_{self.direction}"
                self.image = pygame.transform.scale(self.animations[self.current_animation][1], (self.width, self.height))

                flame_width = 256
                flame_height = self.height
                offset = 64 if self.direction == "right" else -flame_width
                flame_rect = pygame.Rect(self.x + offset, self.y, flame_width, flame_height)

                if flame_rect.colliderect(bloop.get_rect()) and not self.fiammata_hit_registered:
                    bloop.take_damage(12)
                    self.fiammata_hit_registered = True



    

        elif self.current_ability == "melee":
            if self.get_rect().colliderect(bloop.get_rect()):
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    bloop.take_damage(5)
                    self.last_attack_time = current_time
                    self.attacking = True
                    self.frame_index = 0
                    self.current_ability = None
                else:
                    self.attacking = False
            else:
                self.attacking = False
                self.current_ability = None

        # --- Choose a New Ability or Idle ---
        if self.current_ability is None:
            if current_time - self.last_ability_time >= self.ability_cooldown:
                self.last_ability_time = current_time
                self.current_ability = random.choice(["fiammata"])
                
                if self.current_ability == "fiammata":
                    self.fiammata_charging = True
                    self.fiammata_charge_start = current_time
                    self.frame_index = 1
                    self.fiammata_hit_registered = False

        
                
            
            if self.attacking and self.current_animation == f"melee_{self.direction}":
                frames = self.animations[self.current_animation]
                self.frame_timer += 1
                if self.frame_timer >= self.frame_speed:
                    self.frame_timer = 0
                    self.frame_index += 1
                    if self.frame_index >= len(frames):
                        self.frame_index = 0
                        self.attacking = False
                    self.image = pygame.transform.scale(frames[self.frame_index], (self.width, self.height))
            elif not self.spawning and not self.fiammata_active and not self.fiammata_charging:
                self.update_animation()

        # --- Handle Damage from Bloop ---
        if bloop.melee_active and self.get_rect().colliderect(bloop.get_melee_rect()):
            if not self.melee_hit_registered:
                self.take_damage(4)
                self.melee_hit_registered = True
        else:
            self.melee_hit_registered = False

        for p in bloop.projectiles:
            if p["active"]:
                proj_rect = pygame.Rect(p["x"], p["y"], 64, 64)
                if self.get_rect().colliderect(proj_rect):
                    self.take_damage(p["damage"])
                    p["active"] = False

        if self.current_hp <= 0:
            raise Exception("Chef Plu è stato sconfitto!")

    def update_animation(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            frames = self.animations[self.current_animation]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = pygame.transform.scale(frames[self.frame_index], (self.width, self.height))

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        hp_ratio = self.current_hp / self.max_hp
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, (0, 100, 255), (self.x, self.y - 10, self.width * hp_ratio, 5))
        if self.fiammata_active:
            flame_width = 256
            flame_height = self.height/1.5
            offset = 20 if self.direction == "right" else -flame_width
            flame_rect = pygame.Rect(self.x + offset, self.y, flame_width, flame_height)
            pygame.draw.rect(screen, (255, 100, 0), flame_rect)