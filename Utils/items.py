from Utils.classes_raiz import Item, Character
from settings import *

class DrawnItem(Item):
    def __init__(self, name, all_sprites, collision_sprites, image_surface = None, image_path = ""):
        """
        São itens que desenham alguma coisa na tela
        """
        super().__init__(name, all_sprites, collision_sprites, image_surface, image_path)

class Jar(Item):
    def __init__(self,  all_sprites, collision_sprites, image_surface: pygame.Surface=None,image_path:str="",):
        super().__init__(
            "Water Jar",
            all_sprites, 
            collision_sprites, 
            image_surface,
            image_path,
        )

    def on_consume(self, character:Character) -> bool:
        """Cura o usuário e consome 1 unidade."""
        pass

class HealthPotion(Item):
    def __init__(self,  all_sprites, collision_sprites, image_surface: pygame.Surface=None,image_path:str="",):
        super().__init__(
            "Health Potion",
            all_sprites, 
            collision_sprites, 
            image_surface,
            image_path,
        )
        self.heal_amount = 25

    def on_consume(self, character:Character) -> bool:
        """Cura o usuário e consome 1 unidade."""
        if not hasattr(character, "hp") or not hasattr(character, "max_hp"):
            return False
        if character.hp >= character.max_hp:
            return False
        character.hp = min(character.max_hp, character.hp + self.heal_amount)


class WaterCanteen(Item):
    def __init__(self,  all_sprites, collision_sprites, image_surface: pygame.Surface=None,image_path:str="",):
        super().__init__(
            "Water Canteen",
            all_sprites, 
            collision_sprites, 
            image_surface,
            image_path,
        )
        self.thist_regen_amout = 25

    def on_consume(self, character:Character) -> bool:
        """Cura o usuário e consome 1 unidade."""
        if character.thirst_percent <= 0:
            return False
        character.hp = max(0, character.thirst_percent + self.thist_regen_amout)

#parchments
class Parchment(Item):

    """
    Pergaminhos criam uma zona permanente com o efeito imbutido neles.
    Quando usados, adiciona no all_sprites o círculo mágico que vai ficar acima do chão mas embaixo dos objetos
    """


