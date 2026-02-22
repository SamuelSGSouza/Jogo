from settings import *

class StaticMap(pygame.sprite.Sprite):
    def __init__(self, groups, surface):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=(0,0))
        self.is_ground = True

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, *groups, root:str="",obj=None,animation_speed=3, use_center=True, pos,is_detail =False, hitbox_scale =1, has_light=False, surfaces=[], is_on = False):
        super().__init__(*groups)
        self.has_light = has_light
        self.is_detail = is_detail
        if surfaces:
            self.on_surfaces  = surfaces
            self.off_surfaces = surfaces
        else:
            self.on_surfaces, self.off_surfaces = self.load_on_off_surfaces(root, obj)
        self.on=is_on
        if is_on:
            self.frames = self.on_surfaces
        else:
            self.frames = self.off_surfaces
        self.frame_index = 0
        self.animation_speed = min(len(self.on_surfaces), len(self.off_surfaces))
        self.image = self.off_surfaces[0]
        if use_center:
            self.rect = self.image.get_frect(center=pos)

        else:
            self.rect = self.image.get_frect(topleft=pos)
        self.hitbox= pygame.FRect(self.rect.left, self.rect.top,self.rect.width, self.rect.height)
        
        self.hitbox.width = self.rect.width *hitbox_scale

        self.hitbox.height = self.rect.height *hitbox_scale
        self.hitbox.center = self.rect.center

        self.pos = self.hitbox.center

    def load_on_off_surfaces(self,root, obj):
        on_surfs = []
        animations_on = list(sorted([join(root, "on", file) for file in listdir(join(root, "on"))]))
        for img in animations_on:
            surf = pygame.image.load(img)
            scaled_surf = pygame.transform.scale(surf, (obj.width*SCALE, obj.height*SCALE)).convert_alpha()
            on_surfs.append(scaled_surf)

        off_surfs = []
        animations_off = list(sorted([join(root, "off", file) for file in listdir(join(root, "off"))]))
        for img in animations_off:
            surf = pygame.image.load(img)
            scaled_surf = pygame.transform.scale(surf, (obj.width*SCALE, obj.height*SCALE)).convert_alpha()
            off_surfs.append(scaled_surf)

        return on_surfs, off_surfs

    
    def turn_on(self,):
        
        self.frames = self.on_surfaces
        self.image = self.frames[0]
        self.on = True

    def turn_off(self,):
        self.frames = self.off_surfaces
        self.image = self.frames[0]
        self.on=False

    def update(self, *args, **kwargs):
        self.frame_index += 0.01 *len(self.frames)
        if self.frame_index >= len(self.frames)-1:
            self.frame_index =  0
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        return super().update(*args, **kwargs)


class AnimatedGrowingSprite(AnimatedSprite):
    def __init__(self, *groups, surfaces, animation_speed=3, use_center=True,growth_duration_ms=800, pos, start_scale=0.001):
        super().__init__(*groups, surfaces=surfaces, animation_speed=animation_speed, use_center=use_center, pos=pos)
        self.original_frames = surfaces[:]   # guarda originais
        self.original_w = self.original_frames[0].get_width()
        self.original_h = self.original_frames[0].get_height()

        self.growth_duration_ms = growth_duration_ms
        self.start_time = pygame.time.get_ticks()
        self.current_scale = max(0.001, start_scale)

        self.frames = self._resize_frames(self.current_scale)
        # recalc inicial coerente
        self.frame_index = 0.0
        self.image = self.frames[0]
        self.rect = self.image.get_frect(center=self.pos)
        self._recalc_hitbox()


    def _recalc_hitbox(self):
        self.hitbox.update(self.rect.left, self.rect.top, self.rect.width, self.rect.height)
        self.hitbox.width  = self.rect.width 
        self.hitbox.height = self.rect.height
        self.hitbox.center = self.rect.center

    def _resize_frames(self, scale):
        w = max(1, int(self.original_w * scale))
        h = max(1, int(self.original_h * scale))
        return [pygame.transform.scale(f, (w, h)) for f in self.original_frames]

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1.0, elapsed / self.growth_duration_ms)
        new_scale = progress

        if abs(new_scale - self.current_scale) > 0.01:
            self.current_scale = new_scale
            center = self.rect.center
            self.frames = self._resize_frames(self.current_scale)
            # manter frame atual após trocar frames
            idx = int(self.frame_index) % len(self.frames)
            self.image = self.frames[idx]
            self.rect = self.image.get_frect(center=center)
            self.rect.y -= self.current_scale
            self._recalc_hitbox()

class EffectSprite(AnimatedGrowingSprite):
    def __init__(self, *groups, surfaces, animation_speed=3, use_center=True, growth_duration_ms=500,  start_scale=0.001,effect, pos,):
        super().__init__(*groups, surfaces=surfaces, animation_speed=animation_speed, use_center=use_center, growth_duration_ms=growth_duration_ms, pos=pos, start_scale=start_scale)
        self.effect = effect
        
class Sprites(pygame.sprite.Sprite):
    def __init__(self, *groups,surface, pos,):
        super().__init__(*groups)
        self.image = surface
        self.rect = self.image.get_frect(topleft=pos)
        self.is_ground = True

class Steps(pygame.sprite.Sprite):
    def __init__(self, *groups,surface, pos,):
        super().__init__(*groups)
        self.image = pygame.transform.rotozoom(surface, 0, 0.5).convert_alpha()
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox= pygame.FRect(self.rect.left, self.rect.top,self.rect.width, self.rect.height)
        
        self.hitbox.width = self.rect.width/4 #fazendo a hitbox ser 1/4 da real

        self.hitbox.height = self.rect.height/3 #fazendo a hitbox ser 1/2 da real
        self.hitbox.center = self.rect.center

        self.is_fixed = True
        self.is_getable = False
        self.is_step = True

        self.existence_time = 5000
        self.start_time = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if pygame.time.get_ticks() - self.start_time > self.existence_time:
            self.kill()
            

class MoveableSprites(pygame.sprite.Sprite):
    def __init__(self, *groups,surface, pos,):
        super().__init__(*groups)
        self.image = pygame.transform.rotozoom(surface, 0, 0.5).convert_alpha()
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox= pygame.FRect(self.rect.left, self.rect.top,self.rect.width, self.rect.height)
        
        self.hitbox.width = self.rect.width/4 #fazendo a hitbox ser 1/4 da real

        self.hitbox.height = self.rect.height/3 #fazendo a hitbox ser 1/2 da real
        self.hitbox.center = self.rect.center

        self.is_fixed = True
        self.is_getable = False

class CollisionSprites(pygame.sprite.Sprite):
    def __init__(self, *groups,surface, pos,is_inventory=False, use_center=False, is_getable = False, item=None, is_tree=False, is_roof=False, is_fixed_house=False, is_invisible=False):
        super().__init__(*groups)
        self.item = item
        self.image = surface
        self.is_getable = is_getable
        self.is_tree = is_tree
        self.is_roof = is_roof
        self.is_fixed_house = is_fixed_house
        self.is_invisible=is_invisible
        if use_center:
            self.rect = self.image.get_frect(center=pos)

        else:
            self.rect = self.image.get_frect(topleft=pos)
        self.hitbox= pygame.FRect(self.rect.left, self.rect.top,self.rect.width, self.rect.height)
        
        if self.is_tree:
            self.hitbox.width = self.rect.width - self.rect.width *80/100
            self.hitbox.height = self.rect.height - self.rect.height *60/100
            self.hitbox.center = (self.rect.center[0], self.rect.center[1] + self.rect.height*10/100)
        elif self.is_invisible:
            self.hitbox.width = self.rect.width - self.rect.width *80/100
            self.hitbox.height = self.rect.height - self.rect.height *80/100
            self.hitbox.center = self.rect.center

        elif self.is_fixed_house:
            self.hitbox.width = self.rect.width - self.rect.width *30/100
            self.hitbox.height = self.rect.height - self.rect.height *50/100
            self.hitbox.midbottom = (self.rect.midbottom[0], self.rect.midbottom[1]-30)
        else:
            self.hitbox.width = self.rect.width - self.rect.width *30/100
            self.hitbox.height = self.rect.height - self.rect.height *40/100
            self.hitbox.center = self.rect.center

        #INVENTORY
        self.is_inventory = is_inventory
        self.inventory = []

        self.fixed_object = True

class WinterCurseSprites(AnimatedGrowingSprite):
    def __init__(self, *groups,pos,stacks=1, duration):
        self.stacks = stacks
        self.pos = pos
        self.image = self.load_surface()
        super().__init__(*groups, surfaces=[self.image,],growth_duration_ms=duration, pos=pos)
        self.item = None
        
        self.is_winter_curse = True        
        self.is_getable = False
        self.is_tree = False
        

        #INVENTORY
        self.is_inventory = False
        self.inventory = []

        self.fixed_object = True

    def load_surface(self,):
        curse_level = 1 if self.stacks == 1 else 2 if self.stacks == 2 else 3
        root = join(getcwd(), 'Ecosystem', "Winter", "animated_objects", "Winter Curse")

        image = join(root, f"{curse_level}.png")
        surf = pygame.image.load(image).convert_alpha()
        self.rect = surf.get_frect(midbottom=self.pos)
        self.hitbox= pygame.FRect(self.rect.left, self.rect.top,self.rect.width, self.rect.height)
        self.hitbox.width = self.rect.width - self.rect.width *60/100
        self.hitbox.height = self.rect.height - self.rect.height *70/100
        self.hitbox.center = self.rect.center
        return surf