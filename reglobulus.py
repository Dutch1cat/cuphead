import pygame
import random
import os

# Assuming SirBlub.py exists in the same directory for spawning
from sirBlub import SirBlub

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600 # Consistent with main.py for projectile bounds


# --- Helper Classes for ReGlobulus's Abilities ---

class FireLine:
    """Manages a single line of fire left by ReGlobulus's teleport."""
    def __init__(self, x, y, start_time, duration, width, height, damage):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start_time = start_time
        self.duration = duration # in milliseconds
        self.damage = damage
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, current_time):
        """Returns True if active, False otherwise."""
        return current_time - self.start_time < self.duration

    def get_rect(self):
        return self.rect

    def draw(self, screen):
        # Draw a simple orange/red rectangle for the fire line
        # In a real game, this would be an animation
        pygame.draw.rect(screen, (255, 165, 0), self.rect) # Orange
        # Optional: Add a subtle red outline or flicker effect
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2) # Red border


class SlimeBall:
    """Manages a single slime ball projectile for the slime_combo ability."""
    def __init__(self, x, y, image, damage, target_ground_y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (32, 32)) # Slime balls are 32x32
        self.damage = damage
        self.vel_y = 0
        self.gravity = 0.5 # Slime balls fall with gravity
        self.active = True
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.target_ground_y = target_ground_y # The Y position where it stops falling

    def update(self):
        if not self.active:
            return

        self.vel_y += self.gravity
        self.y += self.vel_y
        self.rect.topleft = (self.x, self.y)

        # Deactivate if it hits the ground or goes off screen
        if self.y >= self.target_ground_y:
            self.y = self.target_ground_y
            self.vel_y = 0
            self.active = False # Slime ball "splats" on the ground and becomes inactive

    def get_rect(self):
        return self.rect

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect)


# --- ReGlobulus Class ---

class ReGlobulus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64

        self.initial_max_hp = 200
        self.max_hp = self.initial_max_hp
        self.current_hp = self.initial_max_hp

        self.attack_cooldown = 1000 # General cooldown for melee/ability selection
        self.last_attack_time = 0
        self.attacking = False # For melee visual feedback

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_speed = 10 # Default animation speed
        self.melee_hit_registered = False # To prevent multiple melee hits per single attack

        self.direction = "right"
        self.current_animation = "idle_right"

        self.ability_cooldown = 2000 # Cooldown between choosing new abilities
        self.last_ability_time = 0
        self.current_ability = None # Stores the currently active ability (e.g., "teleport", "slime_combo", "melee", "spawn")

        # --- Phase and Transformation Variables ---
        self.phase = 1 # Boss starts in Phase 1
        self.damage_multiplier = 1.0 # Multiplier for outgoing damage
        self.transformation_active = False # Flag for transformation sequence
        self.transformation_start_time = 0
        self.transformation_duration = 1500 # Duration of transformation animation in ms (adjust based on actual animation)
        self.spawn_sir_blub_used = False # Flag to ensure 'spawn Sir Blub' ability is used only once
        self.spawned_sir_blub = None # Reference to the spawned SirBlub instance

        # --- Teleport Ability Variables ---
        self.teleport_charging = False
        self.teleport_active = False # Flag when teleport has just happened and fire line is active
        self.teleport_charge_start_time = 0
        self.teleport_charge_time = 700 # Time to charge before teleporting
        self.teleport_target_x = 0 # Bloop's X position at the start of charge
        self.fire_lines = [] # List of active FireLine objects
        self.fire_line_duration = 3000 # Fire line active for 3 seconds
        self.fire_line_damage = 0.5 # Damage per tick if Bloop stands on it

        # --- Slime Combo Ability Variables ---
        self.slime_combo_charging = False
        self.slime_combo_active = False
        self.slime_combo_charge_start_time = 0
        self.slime_combo_charge_time = 1000 # Time to charge before launching slime balls
        self.slime_balls = [] # List of active SlimeBall objects
        self.slime_ball_count = 8 # Number of slime balls to launch
        self.slime_ball_spawn_delay = 100 # Delay between individual slime ball launches
        self.last_slime_ball_spawn_time = 0
        self.slime_balls_launched_count = 0 # How many slime balls have been launched this combo

        self.animations = self.load_animations()
        self.image = self.animations[self.current_animation][self.frame_index]

    def load_animations(self):
        animations = {}
        target_size = (64, 64)

        # Idle (5 frames)
        for direction in ["left", "right"]:
            path = f"images/globulus/idle_{direction}"
            frames = []
            for i in range(5):
                file = f"frame_{i}.png"
                full_path = os.path.join(path, file)
                if os.path.exists(full_path):
                    image = pygame.image.load(full_path).convert_alpha()
                    frames.append(pygame.transform.scale(image, target_size))
                else:
                    print(f"Warning: Missing idle animation frame: {full_path}")
            animations[f"idle_{direction}"] = frames
        
        # Teleport (charge and active)
        for direction in ["left", "right"]:
            path = f"images/globulus/teleport_{direction}"
            # frame_1: charging
            charge_img = pygame.image.load(os.path.join(path, "frame_1.png")).convert_alpha()
            charge_img = pygame.transform.scale(charge_img, target_size)
            animations[f"teleport_charge_{direction}"] = [charge_img]
            # frame_2: after teleport (can be same as idle for visual continuity if no specific active frame)
            active_img = pygame.image.load(os.path.join(path, "frame_2.png")).convert_alpha()
            active_img = pygame.transform.scale(active_img, target_size)
            animations[f"teleport_active_{direction}"] = [active_img]

        # Slime Combo (charge)
        for direction in ["left", "right"]:
            path = f"images/globulus/slime_combo_{direction}"
            charge_img = pygame.image.load(os.path.join(path, "frame_1.png")).convert_alpha()
            charge_img = pygame.transform.scale(charge_img, target_size)
            animations[f"slime_combo_charge_{direction}"] = [charge_img]
        
        # Slime Ball Projectile
        slime_ball_img = pygame.image.load("images/globulus/attacks/slime_ball.png").convert_alpha()
        animations["slime_ball_projectile"] = [slime_ball_img] # Stored as a list for consistency

        # Transformation Animation (assuming multiple frames)
        transform_path = "images/globulus/transform"
        transform_frames = []
        # Assuming 5 frames for transformation (adjust range as needed)
        for i in range(5): 
            file = f"frame_{i}.png"
            full_path = os.path.join(transform_path, file)
            if os.path.exists(full_path):
                image = pygame.image.load(full_path).convert_alpha()
                transform_frames.append(pygame.transform.scale(image, target_size))
            else:
                print(f"Warning: Missing transform animation frame: {full_path}")
        animations["transform"] = transform_frames

        return animations

    def update(self, bloop):
        current_time = pygame.time.get_ticks()
        self.direction = "left" if bloop.x < self.x else "right"

        # --- Handle Transformation (Highest Priority State) ---
        if self.transformation_active:
            self.current_animation = "transform"
            # Update transformation animation
            self.frame_timer += 1
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations["transform"])
            self.image = pygame.transform.scale(self.animations[self.current_animation][self.frame_index], (self.width, self.height))

            if current_time - self.transformation_start_time >= self.transformation_duration:
                # Transformation ends, enter Phase 2
                self.transformation_active = False
                self.phase = 2
                self.max_hp = int(self.initial_max_hp * 1.5) # Increase max HP for Phase 2
                self.current_hp = self.max_hp # Full HP for Phase 2
                self.damage_multiplier = 1.5 # Increase damage for Phase 2
                self.current_ability = None # Allow choosing new ability
                self.last_ability_time = current_time # Reset ability cooldown for new phase
                self.frame_index = 0
                self.frame_timer = 0
            return # Exit update, as other actions are paused during transformation

        # --- Handle Active Abilities ---
        elif self.teleport_charging:
            self.current_animation = f"teleport_charge_{self.direction}"
            self.image = self.animations[self.current_animation][0]
            if current_time - self.teleport_charge_start_time >= self.teleport_charge_time:
                # Teleport!
                self.teleport_charging = False
                self.teleport_active = True
                
                # Record the target X (Bloop's X at charge start)
                original_x = self.x 
                self.x = self.teleport_target_x # Move ReGlobulus to Bloop's previous position
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.width)) # Clamp to screen

                # Create fire line at original position
                self.fire_lines.append(FireLine(original_x, self.y, current_time, self.fire_line_duration, self.width, self.height, self.fire_line_damage))
                
                self.current_ability = None # Teleport action completed, allow new ability selection
                self.frame_index = 0 # Reset animation for next state

        elif self.slime_combo_charging:
            self.current_animation = f"slime_combo_charge_{self.direction}"
            self.image = self.animations[self.current_animation][0]
            if current_time - self.slime_combo_charge_start_time >= self.slime_combo_charge_time:
                self.slime_combo_charging = False
                self.slime_combo_active = True
                self.last_slime_ball_spawn_time = current_time # Start spawning timer
                self.slime_balls_launched_count = 0 # Reset count for this combo

        elif self.slime_combo_active:
            # ReGlobulus stays in idle animation during slime_combo
            self.current_animation = f"idle_{self.direction}"
            self.update_animation() # Keep animating idle

            # Spawn slime balls
            if self.slime_balls_launched_count < self.slime_ball_count and \
               current_time - self.last_slime_ball_spawn_time >= self.slime_ball_spawn_delay:
                
                s_ball = SlimeBall(random.randint(0, SCREEN_WIDTH - 32), # Random X from sky
                                   -32, # Start above screen
                                   self.animations["slime_ball_projectile"][0], # Slime ball image
                                   int(10 * self.damage_multiplier), # Damage for slime ball
                                   SCREEN_HEIGHT - 32) # Ground Y for slime balls (assuming Bloop's ground_y roughly)
                self.slime_balls.append(s_ball)
                self.last_slime_ball_spawn_time = current_time
                self.slime_balls_launched_count += 1
            
            # Update and check collisions for slime balls
            for s_ball in self.slime_balls:
                s_ball.update()
                if s_ball.active and s_ball.get_rect().colliderect(bloop.get_rect()):
                    bloop.take_damage(s_ball.damage)
                    s_ball.active = False
            
            # Remove inactive slime balls
            self.slime_balls = [s for s in self.slime_balls if s.active]

            # End slime combo if all spawned and all active ones are gone
            if self.slime_balls_launched_count >= self.slime_ball_count and not self.slime_balls:
                self.slime_combo_active = False
                self.current_ability = None
                self.frame_index = 0 # Reset animation index

        # Melee Attack
        elif self.current_ability == "melee":
            # ReGlobulus stays in idle animation
            self.current_animation = f"idle_{self.direction}"
            self.update_animation() # Keep animating idle

            if self.get_rect().colliderect(bloop.get_rect()):
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    bloop.take_damage(int(5 * self.damage_multiplier)) # Apply damage multiplier
                    
                    # Push Bloop
                    push_amount = 20 # How far to push Bloop
                    bloop_push_direction = 1 if self.direction == "right" else -1
                    bloop.x += push_amount * bloop_push_direction
                    bloop.x = max(0, min(bloop.x, SCREEN_WIDTH - 64)) # Clamp Bloop to screen

                    self.last_attack_time = current_time
                    self.attacking = True # Brief flag for visual/audio feedback if needed
                    self.current_ability = None  # Attack completed, reset ability
                else:
                    self.attacking = False
            else:
                self.attacking = False
                # If Bloop is out of range, clear ability to let ReGlobulus do something else
                if current_time - self.last_ability_time > self.ability_cooldown:
                    self.current_ability = None

        # Spawn Sir Blub (Phase 2 only, one time use)
        elif self.current_ability == "spawn" and self.phase == 2:
            self.current_animation = f"idle_{self.direction}" # ReGlobulus stays in idle animation
            self.update_animation() # Keep animating idle

            if not self.spawn_sir_blub_used:
                # Spawn SirBlub roughly near ReGlobulus
                self.spawned_sir_blub = SirBlub(self.x + random.randint(-50, 50), self.y)
                self.spawned_sir_blub.current_hp = 200
                self.spawn_sir_blub_used = True
                self.current_ability = None # Ability used, reset

        # --- Choose a New Ability or Idle State ---
        # This block runs ONLY if no specific ability is currently active.
        if self.current_ability is None and not self.transformation_active:
            if current_time - self.last_ability_time >= self.ability_cooldown:
                self.last_ability_time = current_time
                
                # Choose abilities based on phase
                if self.phase == 1:
                    self.current_ability = random.choice(["melee", "teleport", "slime_combo"])
                else: # Phase 2
                    available_abilities = ["melee", "teleport", "slime_combo"]
                    if not self.spawn_sir_blub_used:
                        available_abilities.append("spawn") # Add spawn only if not used
                    self.current_ability = random.choice(available_abilities)
                
                # Initialize variables for the chosen ability
                if self.current_ability == "teleport":
                    self.teleport_charging = True
                    self.teleport_charge_start_time = current_time
                    self.teleport_target_x = bloop.x # Register Bloop's X at charge start
                elif self.current_ability == "slime_combo":
                    self.slime_combo_charging = True
                    self.slime_combo_charge_start_time = current_time
                elif self.current_ability == "spawn":
                    # No specific charging animation, ReGlobulus just uses idle
                    pass
                elif self.current_ability == "melee":
                    # No specific charging, just a quick action
                    pass
                
            # Update idle animation if truly idling (not in an ability state)
            if self.current_ability is None: # Only update idle if not preparing/doing an ability
                self.current_animation = f"idle_{self.direction}"
                self.update_animation()


        # --- Handle Damage from Bloop ---
        # This section is independent of ReGlobulus's abilities
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

        # --- Update Fire Lines ---
        self.fire_lines = [fl for fl in self.fire_lines if fl.update(current_time)]
        # Check collision with Bloop for active fire lines
        for fl in self.fire_lines:
            if fl.get_rect().colliderect(bloop.get_rect()):
                bloop.take_damage(fl.damage) # Fire line damage


        # --- Check for Phase Transition / Defeat ---
        if self.current_hp <= 0:
            if self.phase == 1 and not self.transformation_active:
                # Initiate transformation
                self.transformation_active = True
                self.transformation_start_time = current_time
                self.frame_index = 0 # Start transform animation from first frame
                self.frame_timer = 0
                self.current_ability = None # Clear current ability during transformation
                bloop.current_hp = bloop.max_hp
                
            elif self.phase == 2:
                # Fully defeated in Phase 2
                raise Exception("ReGlobulus is defeated!")

        # --- Update Spawned SirBlub ---
        if self.spawned_sir_blub:
            self.spawned_sir_blub.update(bloop)


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
        # Returns the current bounding box for ReGlobulus
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw ReGlobulus's current image
        screen.blit(self.image, (self.x, self.y))
        
        # Draw Fire Lines
        for fl in self.fire_lines:
            fl.draw(screen)

        # Draw Slime Balls
        for s_ball in self.slime_balls:
            s_ball.draw(screen)

        # Draw Spawned SirBlub
        if self.spawned_sir_blub:
            self.spawned_sir_blub.draw(screen)
        
        # Draw Health Bar
        hp_ratio = self.current_hp / self.max_hp
        # Background of health bar
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y - 10, self.width, 5))
        # Foreground (current HP) of health bar, color changes based on phase or just blue
        hp_color = (0, 100, 255) if self.phase == 1 else (255, 50, 0) # Blue for P1, Red for P2
        pygame.draw.rect(screen, hp_color, (self.x, self.y - 10, self.width * hp_ratio, 5))

