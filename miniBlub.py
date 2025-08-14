import pygame

class MiniBlub:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = 2
        self.hp = 1
        self.hit_registered = False
        self.alive = True

        # Preload images once
        self.image_left = pygame.transform.scale(
            pygame.image.load("images/blub/mini-blub/frame_1.png").convert_alpha(),
            (self.width, self.height)
        )
        self.image_right = pygame.transform.scale(
            pygame.image.load("images/blub/mini-blub/frame_0.png").convert_alpha(),
            (self.width, self.height)
        )

        self.image = self.image_right  # Default facing right
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, bloop):
        # Move toward Bloop
        if bloop.x < self.x:
            self.x -= self.speed
            self.image = self.image_left
        elif bloop.x > self.x:
            self.x += self.speed
            self.image = self.image_right

        # Always update rect position
        self.rect.topleft = (self.x, self.y)

        if self.rect.colliderect(bloop.get_rect()):
            bloop.take_damage(0.2)
        if bloop.melee_active and self.rect.colliderect(bloop.get_melee_rect()):
            if not self.hit_registered:
                self.hp -= 4
                self.hit_registered = True
        else:
            self.hit_registered = False

        # --- Danno da proiettili ---
        for p in bloop.projectiles:
            if p["active"]:
                proj_rect = pygame.Rect(p["x"], p["y"], 64, 64)
                if self.rect.colliderect(proj_rect):
                    self.hp -= p["damage"]
                    p["active"] = False

        # --- Morte ---
        if self.hp <= 0:
            self.alive = False

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)
        else:
            self.y = -100
