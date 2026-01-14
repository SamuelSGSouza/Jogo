from Utils.classes_raiz import Spell, Character
from sprites import EffectSprite
from settings import *
from Utils.effects import SpacialSkillBLock

class SpacialSpell(Spell):
    def __init__(self, *, mana_cost = 0, spelling_difficult_level = 1, spell_type = "AT", spell_subtype = "Spacial", spell_range = 0):
        super().__init__(mana_cost=mana_cost, spelling_difficult_level=spelling_difficult_level, spell_type=spell_type, spell_subtype=spell_subtype, spell_range=spell_range)

    def can_use(self, user: Character, target: Character, *args, **kwargs) -> bool:
        if user.spacial_skill_blocked:
            return False
        return True

class ChangePositions(SpacialSpell):
    def __init__(self, *, mana_cost=0, spelling_difficult_level=3, spell_type="AT", spell_subtype="Spacial", spell_range=550):
        super().__init__(mana_cost=mana_cost, spelling_difficult_level=spelling_difficult_level, spell_type=spell_type, spell_subtype=spell_subtype, spell_range=spell_range)

    def use(self, user: Character, target: Character, *args, **kwargs):
        # pega posição atual REAL (prioriza hitbox)
        user_pos = (user.hitbox.center if hasattr(user, "hitbox")
                    else user.rect.center)
        target_pos = (target.hitbox.center if hasattr(target, "hitbox")
                      else target.rect.center)

        # troca do usuário
        if hasattr(user, "hitbox"):
            user.hitbox.center = target_pos
        user.rect.center = target_pos

        # troca do alvo
        if hasattr(target, "hitbox"):
            target.hitbox.center = user_pos
        target.rect.center = user_pos


spacial_lock_images = []
image_path = join(getcwd(), "Utils", "items", "block_space_magic_spell.png")
for i in range(2,21):
    spacial_lock_images.append(load_with_alpha(image_path, i/20))
for i in range(21,2, -1):
    spacial_lock_images.append(load_with_alpha(image_path, i/20))
class SpacialLock(Spell):
    def __init__(self, *, mana_cost = 0, spelling_difficult_level = 1, spell_type = "AT", spell_subtype = "Spacial", spell_range = 550):
        super().__init__(mana_cost=mana_cost, spelling_difficult_level=spelling_difficult_level, spell_type=spell_type, spell_subtype=spell_subtype, spell_range=spell_range)
        
    def use(self, user: Character, target: Character=None, all_sprites=[], collision_sprites=[]):
        # pega posição atual REAL (prioriza hitbox)
        user_pos = user.hitbox.center 
        
        surfaces = [pygame.transform.scale(image, (self.spell_range, self.spell_range)) for image in spacial_lock_images]

        EffectSprite(all_sprites, collision_sprites, surfaces = surfaces, pos=user_pos, effect=SpacialSkillBLock, animation_speed=12,)



