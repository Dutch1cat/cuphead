import pygame
import random
import os
# MiniBlub is no longer needed as minions are replaced by salsa_drop
# from miniBlub import MiniBlub

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600 # Added for consistency, especially for salsa drop

class ChefPlu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64

        self.max_hp = 300
        self.current_hp = 300

        self.attack_cooldown = 1000 # General cooldown for melee attacks
        self.last_attack_time = 0
        self.attacking = False # Flag for brief melee attack animation feedback

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 10
        self.melee_hit_registered = False # To prevent multiple hits from one melee attack

        self.direction = "right"
        self.current_animation = "idle_right"

        self.ability_cooldown = 2000 # Cooldown before Chef Plu can choose a new ability
        self.last_ability_time = 0
        self.current_ability = None # Stores the currently active ability (e.g., "fiammata", "salsa_drop", "sprint", "melee")

        # --- Fiammata Ability Variables ---
        self.fiammata_charging = False
        self.fiammata_active = False
        self.fiammata_charge_start_time = 0
        self.fiammata_charge_time = 700  # Milliseconds to charge before laser fires
        self.fiammata_duration = 700 # Milliseconds the laser stays active
        self.fiammata_damage = 15
        self.laser_rect = pygame.Rect(0, 0, 0, 0) # Placeholder for the laser's collision rectangle

        # --- Salsa Drop Ability Variables ---
        self.salsa_drop_charging = False
        self.salsa_drop_active = False
        self.salsa_drop_charge_start_time = 0
        self.salsa_drop_charge_time = 1000 # Milliseconds to charge before salsa drops
        self.salsa_drop_spawn_delay = 200 # Delay between individual salsa drops
        self.last_salsa_spawn_time = 0
        self.salsa_projectiles = [] # List to hold active salsa projectiles
        self.salsa_gravity = 0.5
        self.salsa_initial_speed = 3
        self.salsa_damage = 5
        self.salsa_count = 4 # Number of salsa projectiles to drop
        self.salsa_spawned_count = 0 # NEW: Tracks how many salsa have been spawned in the current ability instance

        # --- Sprint Ability Variables ---
        self.sprint_active = False
        self.sprint_start_time = 0
        self.sprint_duration = 3000 # Milliseconds Chef Plu sprints
        self.sprint_speed = 3 # Speed at which Chef Plu moves during sprint
        self.sprint_damage = 15 # Damage dealt if Bloop is hit during sprint

        # Load all animations
        self.animations = self.load_animations()
        self.image = self.animations[self.current_animation][self.frame_index]

    def load_animations(self):
        animations = {}
        target_size = (64, 64)

        # Idle (2 frames)
        for direction in ["left", "right"]:
            path = f"images/plu/idle_{direction}"
            frames = []
            for i in range(2):
                file = f"frame_{i}.png"
                full_path = pygame.image.load(os.path.join(path, file)).convert_alpha()
                frames.append(pygame.transform.scale(full_path, target_size))
            animations[f"idle_{direction}"] = frames
        
        # Sprint (2 frames)
        for direction in ["left", "right"]:
            path = f"images/plu/sprint_{direction}"
            frames = []
            for i in range(2):
                file = f"frame_{i}.png"
                full_path = pygame.image.load(os.path.join(path, file)).convert_alpha()
                frames.append(pygame.transform.scale(full_path, target_size))
            animations[f"sprint_{direction}"] = frames

        # Fiammata (charge and active, 1 frame each)
        for direction in ["left", "right"]:
            path = f"images/plu/fiammata_{direction}"
            charge_img = pygame.image.load(os.path.join(path, "frame_1.png")).convert_alpha()
            charge_img = pygame.transform.scale(charge_img, target_size)
            active_img = pygame.image.load(os.path.join(path, "frame_2.png")).convert_alpha()
            active_img = pygame.transform.scale(active_img, target_size)
            animations[f"fiammata_charge_{direction}"] = [charge_img]
            animations[f"fiammata_active_{direction}"] = [active_img]

        # Salsa Drop (charge and active, 1 frame each)
        path = "images/plu/salsa_drop"
        salsa_charge_img = pygame.image.load(os.path.join(path, "frame_1.png")).convert_alpha()
        salsa_charge_img = pygame.transform.scale(salsa_charge_img, target_size)
        salsa_active_img = pygame.image.load(os.path.join(path, "frame_2.png")).convert_alpha()
        salsa_active_img = pygame.transform.scale(salsa_active_img, target_size)
        animations["salsa_drop_charge"] = [salsa_charge_img]
        animations["salsa_drop_active"] = [salsa_active_img]

        # Salsa Projectile (single image)
        salsa_proj_img = pygame.image.load("images/plu/salsa.png").convert_alpha()
        salsa_proj_img = pygame.transform.scale(salsa_proj_img, (32, 32)) # Smaller size for projectiles
        animations["salsa_projectile"] = [salsa_proj_img]

        return animations

    def update(self, bloop):
        current_time = pygame.time.get_ticks()
        # Determine direction based on Bloop's position
        self.direction = "left" if bloop.x < self.x else "right"

        # --- Handle Currently Active Abilities ---
        if self.fiammata_charging:
            # Set animation for charging
            self.current_animation = f"fiammata_charge_{self.direction}"
            self.image = self.animations[self.current_animation][0]
            if current_time - self.fiammata_charge_start_time >= self.fiammata_charge_time:
                self.fiammata_charging = False
                self.fiammata_active = True
                self.fiammata_start_time = current_time # Start timer for active phase

                # Define laser collision rectangle based on direction
                laser_height = 20 # Thickness of the laser
                if self.direction == "right":
                    # Laser extends from Plu's right side to the end of the screen
                    self.laser_rect = pygame.Rect(self.x + self.width, self.y + self.height // 2 - laser_height // 2,
                                                  SCREEN_WIDTH - (self.x + self.width), laser_height)
                else: # left
                    # Laser extends from the left edge of the screen to Plu's left side
                    self.laser_rect = pygame.Rect(0, self.y + self.height // 2 - laser_height // 2,
                                                  self.x, laser_height)
                
                # Check for collision with Bloop immediately when laser activates
                if self.laser_rect.colliderect(bloop.get_rect()):
                    bloop.take_damage(self.fiammata_damage)

        elif self.fiammata_active:
            # Set animation for active laser
            self.current_animation = f"fiammata_active_{self.direction}"
            self.image = self.animations[self.current_animation][0]
            if current_time - self.fiammata_start_time >= self.fiammata_duration:
                # End fiammata ability
                self.fiammata_active = False
                self.current_ability = None
                self.laser_rect = pygame.Rect(0, 0, 0, 0) # Reset laser rect

        elif self.salsa_drop_charging:
            # Set animation for charging salsa drop
            self.current_animation = "salsa_drop_charge"
            self.image = self.animations[self.current_animation][0]
            if current_time - self.salsa_drop_charge_start_time >= self.salsa_drop_charge_time:
                self.salsa_drop_charging = False
                self.salsa_drop_active = True
                self.last_salsa_spawn_time = current_time # Initialize spawn timer
                # No need to reset salsa_spawned_count here, it's reset when choosing the ability

        elif self.salsa_drop_active:
            # Set animation for active salsa drop
            self.current_animation = "salsa_drop_active"
            self.image = self.animations[self.current_animation][0]

            # Continuously spawn salsa during active phase until salsa_count is reached
            if self.salsa_spawned_count < self.salsa_count and \
               current_time - self.last_salsa_spawn_time >= self.salsa_drop_spawn_delay:
                salsa_x = random.randint(0, SCREEN_WIDTH - 32) # Salsa is 32x32
                self.salsa_projectiles.append({
                    "x": salsa_x,
                    "y": -32, # Start above screen
                    "vel_y": self.salsa_initial_speed,
                    "image": self.animations["salsa_projectile"][0],
                    "active": True
                })
                self.last_salsa_spawn_time = current_time
                self.salsa_spawned_count += 1 # Increment counter for spawned salsa
            
            # Update and check collision for each salsa projectile
            for salsa in self.salsa_projectiles:
                if salsa["active"]:
                    salsa["vel_y"] += self.salsa_gravity
                    salsa["y"] += salsa["vel_y"]
                    # Create rect for collision check
                    salsa_rect = pygame.Rect(salsa["x"], salsa["y"], 32, 32)
                    if bloop.get_rect().colliderect(salsa_rect):
                        bloop.take_damage(self.salsa_damage)
                        salsa["active"] = False # Deactivate salsa after hitting

                    # Remove salsa if it goes off screen
                    if salsa["y"] > SCREEN_HEIGHT:
                        salsa["active"] = False
            
            # Filter out inactive salsa projectiles
            self.salsa_projectiles = [s for s in self.salsa_projectiles if s["active"]]

            # NEW: End salsa_drop ability if all salsa have been spawned AND all are inactive
            if self.salsa_spawned_count >= self.salsa_count and not self.salsa_projectiles:
                 self.salsa_drop_active = False
                 self.current_ability = None

        elif self.sprint_active:
            # Use sprint animation
            self.current_animation = f"sprint_{self.direction}"
            self.update_animation() # Animate Chef Plu walking

            # Move Chef Plu towards Bloop
            if self.direction == "right":
                self.x += self.sprint_speed
            else:
                self.x -= self.sprint_speed
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width)) # Keep within screen bounds

            # Check collision with Bloop during sprint
            if self.get_rect().colliderect(bloop.get_rect()):
                bloop.take_damage(self.sprint_damage)
                self.sprint_active = False # End sprint on hit
                self.current_ability = None
                self.attacking = True # Brief attacking state for visual feedback
                self.last_attack_time = current_time # Reset melee cooldown if it overlaps

            # End sprint after its duration, even if no hit occurred
            if current_time - self.sprint_start_time >= self.sprint_duration:
                self.sprint_active = False
                self.current_ability = None
                self.attacking = False # Ensure attacking flag is reset

        # --- Melee Attack ---
        # This occurs only if current_ability is set to "melee"
        elif self.current_ability == "melee":
            # Melee animation uses idle frames
            self.current_animation = f"idle_{self.direction}"
            self.update_animation() # Continue idle animation while in melee state

            if self.get_rect().colliderect(bloop.get_rect()) and current_time - self.last_attack_time >= self.attack_cooldown:
                # Perform the melee hit
                bloop.take_damage(5) # Melee damage
                self.last_attack_time = current_time
                self.attacking = True # Set briefly for feedback
                self.current_ability = None  # Melee attack completed, reset ability
            else:
                self.attacking = False # Not currently in the hitting part of melee
                # If Bloop is out of range or cooldown, clear ability to allow new choice
                if not self.get_rect().colliderect(bloop.get_rect()) and \
                   current_time - self.last_ability_time > self.ability_cooldown:
                    self.current_ability = None # Reset if Bloop moves away or no attack happened

        # --- Choose a New Ability or Idle State ---
        # This block runs ONLY if no specific ability (fiammata, salsa_drop, sprint, melee) is currently active.
        if self.current_ability is None:
            if current_time - self.last_ability_time >= self.ability_cooldown:
                self.last_ability_time = current_time
                # Randomly choose a new ability
                self.current_ability = random.choice(["melee", "fiammata", "salsa_drop", "sprint"])
                
                # Initialize variables for the chosen ability
                if self.current_ability == "fiammata":
                    self.fiammata_charging = True
                    self.fiammata_charge_start_time = current_time
                elif self.current_ability == "salsa_drop":
                    self.salsa_drop_charging = True
                    self.salsa_drop_charge_start_time = current_time
                    self.salsa_projectiles = []
                    self.salsa_spawned_count = 0 # NEW: Reset count when ability starts
                elif self.current_ability == "sprint":
                    self.sprint_active = True
                    self.sprint_start_time = current_time
                elif self.current_ability == "melee":
                    self.attacking = True # This flags a melee attempt

            # Update idle animation if no ability is chosen or active
            # This ensures Chef Plu is animating even when not performing a special ability
            if not self.fiammata_charging and not self.fiammata_active and \
               not self.salsa_drop_charging and not self.salsa_drop_active and \
               not self.sprint_active and not (self.current_ability == "melee" and self.attacking):
                self.current_animation = f"idle_{self.direction}"
                self.update_animation() # Only update idle if truly idling/moving without special ability

        # --- Handle Damage from Bloop ---
        # This section is independent of Chef Plu's abilities
        if bloop.melee_active and self.get_rect().colliderect(bloop.get_melee_rect()):
            if not self.melee_hit_registered:
                self.take_damage(4) # Damage from Bloop's melee
                self.melee_hit_registered = True
        else:
            self.melee_hit_registered = False

        for p in bloop.projectiles:
            if p["active"]:
                proj_rect = pygame.Rect(p["x"], p["y"], 64, 64)
                if self.get_rect().colliderect(proj_rect):
                    self.take_damage(p["damage"])
                    p["active"] = False

        # --- Check for Defeat ---
        if self.current_hp <= 0:
            raise Exception("Chef Plu is defeated!")

        # MiniBlubs (minions) and their update loop have been removed.
        # If you later decide to re-introduce a similar concept, you'd add a new list
        # and update loop here.

    def update_animation(self):
        # Generic animation update logic for states like idle and sprint
        self.frame_timer += 1
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            frames = self.animations[self.current_animation]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = pygame.transform.scale(frames[self.frame_index], (self.width, self.height))

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)

    def get_rect(self):
        # Returns the current bounding box for Chef Plu
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw Chef Plu's current image
        screen.blit(self.image, (self.x, self.y))
        
        # Draw Fiammata Laser if active
        if self.fiammata_active:
            # Draw a red rectangle for the laser visual
            pygame.draw.rect(screen, (255, 0, 0), self.laser_rect)

        # Draw Salsa Projectiles
        for salsa in self.salsa_projectiles:
            if salsa["active"]:
                screen.blit(salsa["image"], (salsa["x"], salsa["y"]))
        
        # Draw Health Bar
        hp_ratio = self.current_hp / self.max_hp
        # Background of health bar
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y - 10, self.width, 5))
        # Foreground (current HP) of health bar
        pygame.draw.rect(screen, (0, 100, 255), (self.x, self.y - 10, self.width * hp_ratio, 5))

