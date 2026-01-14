from settings import *
from abc import ABC, abstractmethod
from sprites import WinterCurseSprites

class Effect(ABC):
    def __init__(self, duration_ms=800, name="Effect", color=(255,0,0)):
        self.duration_ms = duration_ms
        self.name = name
        self.color = color
        self._applied = False

    def update(self, character):
        now = pygame.time.get_ticks()
        if not self._applied:
            self.start = pygame.time.get_ticks()
            self.on_apply(character)
            self._applied = True

        if self.duration_ms > 0:
            if now - self.start >= self.duration_ms:
                self.on_remove(character)
                try: character.effects.remove(self)
                except ValueError: pass
                return

        self.on_tick(now, character)

    @abstractmethod
    def on_apply(self): ...
    def on_tick(self, now, *args, **kwargs): pass
    @abstractmethod
    def on_remove(self): ...



class Slow(Effect):
    def __init__(self, duration_ms=800, factor=0.5, **kw):
        super().__init__(duration_ms, name="Slow", **kw)
        self.factor = factor

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.speed_multipliers.append(self.factor)

    def on_remove(self, character):
        # remove UM multiplicador correspondente (sem resetar outros)
        try: character.speed_multipliers.remove(self.factor)
        except ValueError: pass

class Fast(Effect):
    def __init__(self, duration_ms=800, factor=1.5, **kw):
        super().__init__(duration_ms, name="Fast", **kw)
        self.factor = factor

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.speed_multipliers.append(self.factor)

    def on_remove(self, character):
        # remove UM multiplicador correspondente (sem resetar outros)
        try: character.speed_multipliers.remove(self.factor)
        except ValueError: pass

class Stun(Effect):
    def __init__(self, duration_ms=800, factor=0.0, **kw):
        super().__init__(duration_ms, name="Stunned", **kw)
        self.factor = factor

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.speed_multipliers.append(self.factor)

    def on_remove(self, character):
        # remove UM multiplicador correspondente (sem resetar outros)
        try: character.speed_multipliers.remove(self.factor)
        except ValueError: pass

class Poison(Effect):
    def __init__(self, duration_ms=4000, factor=1.0, tick_delay_ms=2000, **kw):
        super().__init__(duration_ms, name="Poisoned", **kw)
        self.factor = factor
        self.tick_delay = tick_delay_ms
        self.last_applied_tick = pygame.time.get_ticks()

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.handle_damage(self.factor, shake_screen=True)

    def on_tick(self, now, character):
        if now - self.last_applied_tick >  self.tick_delay:
            character.handle_damage(self.factor,shake_screen=True)
            self.last_applied_tick = now

    def on_remove(self, character):
        pass

class Blind(Effect):
    def __init__(self, duration_ms=4000, factor=1.0, tick_delay_ms=1000, **kw):
        super().__init__(duration_ms, name="Blind", **kw)
        self.factor = factor
        self.tick_delay = tick_delay_ms
        self.last_applied_tick = pygame.time.get_ticks()

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.is_blind = True
        

    def on_tick(self, now, character):
        character.is_blind = True

    def on_remove(self, character):
        character.is_blind = False

class Invisibility(Effect):
    def __init__(self, duration_ms=4000, factor=1.0, tick_delay_ms=1000, **kw):
        super().__init__(duration_ms, name="Invisible", **kw)
        self.factor = factor
        self.tick_delay = tick_delay_ms
        self.last_applied_tick = pygame.time.get_ticks()

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.is_invisible = True
        

    def on_tick(self, now, character):
        character.is_invisible = True

    def on_remove(self, character):
        character.is_invisible = False

class SpacialSkillBLock(Effect):
    def __init__(self, duration_ms=4000, factor=1.0, tick_delay_ms=200, **kw):
        super().__init__(duration_ms, name="Spacial Lock", **kw)
        self.factor = factor
        self.tick_delay = tick_delay_ms
        self.last_applied_tick = pygame.time.get_ticks()

    def on_apply(self, character):
        # idempotente: só adiciona o multiplicador
        character.spacial_skill_blocked = True
        

    def on_tick(self, now, character):
        character.spacial_skill_blocked = True

    def on_remove(self, character):
        character.spacial_skill_blocked = False

class FrozenEffect(Effect):
    def __init__(self, duration_ms=4000, tick_delay_ms=150, curse_groups=[], **kw):
        super().__init__(duration_ms, name="Frozen", **kw)
        self.curse_groups:list = curse_groups
        self.winter_curse_sprite = None
        self.duration = duration_ms
        self.start = pygame.time.get_ticks()
        self.marked_as_dying = False

    def on_apply(self, character):
        # o personagem é dado como congelado
        character.is_frozen = True
        #surge um sprite de gelo no midbottom dele
        x, y = character.rect.midbottom
        x += character.hitbox.width//2
        y += character.hitbox.height//2-2
        self.winter_curse_sprite = WinterCurseSprites(*self.curse_groups, pos=(x,y), stacks=3, duration=5000)
        #o sprite vai crescendo ao longo de 10 segundos
        character.action="Hurt"

    def on_tick(self, now, character):
        if pygame.time.get_ticks() - self.start > self.duration//4 and not self.marked_as_dying:
            character.is_dying =True
            self.marked_as_dying = True
            

    def on_remove(self, character):
        pass


