import pygame
import random
from miniBlub import MiniBlub

SCREEN_WIDTH = 800

class SirBlub:
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
        self.stoccata_active = False
        self.stoccata_charging = False
        self.stoccata_charge_start = 0
        self.stoccata_speed = 10
        self.stoccata_direction = "right"
        self.stoccata_start_time = 0
        self.stoccata_duration = 3000

        self.ability_cooldown = 2000
        self.last_ability_time = 0
        self.current_ability = None

        self.spawn_frame_index = 0
        self.spawn_frame_timer = 0
        self.spawn_frame_speed = 10
        self.spawning = False
        self.spawn_start_time = 0
        self.spawn_duration = 2000

        self.minions = []

        self.animations = {
            "idle_left": [pygame.image.load(f"images/blub/idle_left/frame_{i}.png").convert_alpha() for i in range(2)],
            "idle_right": [pygame.image.load(f"images/blub/idle_right/frame_{i}.png").convert_alpha() for i in range(2)],
            "melee_left": [pygame.image.load(f"images/blub/melee_left/frame_{i}.png").convert_alpha() for i in range(3)],
            "melee_right": [pygame.image.load(f"images/blub/melee_right/frame_{i}.png").convert_alpha() for i in range(3)],
            "stoccata_left": [None,
                              pygame.image.load("images/blub/stoccata_left/frame_1.png").convert_alpha(),
                              pygame.image.load("images/blub/stoccata_left/frame_2.png").convert_alpha()],
            "stoccata_right": [None,
                               pygame.image.load("images/blub/stoccata_right/frame_1.png").convert_alpha(),
                               pygame.image.load("images/blub/stoccata_right/frame_2.png").convert_alpha()],
            "spawn_left": [pygame.image.load(f"images/blub/spawn_left/frame_{i}.png").convert_alpha() for i in range(5)],
            "spawn_right": [pygame.image.load(f"images/blub/spawn_right/frame_{i}.png").convert_alpha() for i in range(5)],
        }

        self.image = self.animations[self.current_animation][self.frame_index]

    def update(self, bloop):
        current_time = pygame.time.get_ticks()
        self.direction = "left" if bloop.x < self.x else "right"

        # --- Handle Active Abilities ---
        # Stoccata Charging
        if self.stoccata_charging:
            self.attacking = False
            self.current_animation = f"stoccata_{self.stoccata_direction}"
            self.image = pygame.transform.scale(self.animations[self.current_animation][1], (self.width, self.height))
            if current_time - self.stoccata_charge_start >= 1000:
                self.stoccata_charging = False
                self.stoccata_active = True
                self.stoccata_start_time = current_time
                self.frame_index = 2
        # Stoccata Active
        elif self.stoccata_active:
            if current_time - self.stoccata_start_time >= self.stoccata_duration:
                self.stoccata_active = False
                self.current_ability = None
            else:
                self.attacking = False
                self.current_animation = f"stoccata_{self.stoccata_direction}"
                self.image = pygame.transform.scale(self.animations[self.current_animation][2], (self.width, self.height))
                direction = 1 if self.stoccata_direction == "right" else -1
                self.x += self.stoccata_speed * direction
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

                if self.get_rect().colliderect(bloop.get_rect()):
                    bloop.take_damage(15)
                    self.stoccata_active = False
                    self.current_ability = None
        
        # Spawning Minions
        elif self.spawning:
            self.attacking = False
            spawn_frames = self.animations[f"spawn_{self.direction}"]
            self.current_animation = f"spawn_{self.direction}"

            self.spawn_frame_timer += 1
            if self.spawn_frame_timer >= self.spawn_frame_speed:
                self.spawn_frame_timer = 0
                self.spawn_frame_index += 1
                if self.spawn_frame_index >= len(spawn_frames):
                    self.spawn_minions()
                    self.spawning = False
                    self.current_ability = None
                    self.frame_index = 0
                    self.frame_timer = 0
                else:
                    self.image = pygame.transform.scale(spawn_frames[self.spawn_frame_index], (self.width, self.height))

        # Melee Attack
        elif self.current_ability == "melee":
            if self.get_rect().colliderect(bloop.get_rect()):
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    bloop.take_damage(5)
                    self.last_attack_time = current_time
                    self.attacking = True
                    self.frame_index = 0
                    self.current_ability = None  # Attack completed, reset ability
                else:
                    # Still in cooldown, wait
                    self.attacking = False
            else:
                # Bloop is out of range, clear ability to let SirBlub do something else
                self.attacking = False
                self.current_ability = None


        # --- Choose a New Ability or Idle ---
        if self.current_ability is None:
            if current_time - self.last_ability_time >= self.ability_cooldown:
                self.last_ability_time = current_time
                self.current_ability = random.choice(["melee", "stoccata", "spawn"])
                
                if self.current_ability == "stoccata":
                    self.stoccata_charging = True
                    self.stoccata_charge_start = current_time
                    self.last_stoccata_time = current_time
                    self.stoccata_direction = self.direction
                    self.frame_index = 1
                elif self.current_ability == "spawn":
                    self.spawning = True
                    self.spawn_frame_index = 0
                    self.spawn_frame_timer = 0
                    self.image = pygame.transform.scale(self.animations[f"spawn_{self.direction}"][0], (self.width, self.height))
                    self.spawn_start_time = current_time
                
            # Animation for idle/running
            if self.attacking:
                self.current_animation = f"melee_{self.direction}"
            else:
                self.current_animation = f"idle_{self.direction}"
            
            # The melee animation is brief, so we need to handle it.
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
            elif not self.spawning and not self.stoccata_active and not self.stoccata_charging:
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
            raise Exception("Sir Blub is defeated!")

        # --- Update Minions ---
        for minion in self.minions:
            minion.update(bloop)

    def spawn_minions(self):
        for _ in range(random.randint(1, 3)):
            m = MiniBlub(self.x + random.randint(-30, 30), self.y + 32)
            self.minions.append(m)

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
        for minion in self.minions:
            minion.draw(screen)
        hp_ratio = self.current_hp / self.max_hp
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, (0, 100, 255), (self.x, self.y - 10, self.width * hp_ratio, 5))