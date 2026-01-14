from settings import *
from Utils.classes_raiz import *
from Utils.actions import *

class Monster(Character):
        
    def __init__(self, *groups, collision_sprites:pygame.sprite.Group,creatures_sprites:pygame.sprite.Group, monster_name="Winter Slime", house_point=(0,0), initial_position, actions =[], can_talk=False,scale_on_attack_value=1,original_speed=100, attack_damage=5, max_hp=80, default_character_size=DCS):
        super().__init__(*groups, collision_sprites=collision_sprites,creatures_sprites=creatures_sprites, personal_name=monster_name+" "+f"{randint(0,100)}",scale_on_attack_value=scale_on_attack_value, attack_damage=attack_damage, max_hp=max_hp, )
        self.all_groups= groups
        self.is_player = False
        self.is_human = False
        self.specie = monster_name

        self.village_rect = pygame.Rect(3800,1400,2200, 2000)
        self.water_sources = [(5528, 2200), (4618, 2836), (4481, 2000) ]
        self.house_point = house_point

        self.armor_type = ""
        self.default_folder_path = join(getcwd(), "Ecosystem","Winter","Monsters", monster_name,)
        
        if can_talk:
            self.scripts = load_scripts(self.default_folder_path)
        self.default_size = default_character_size
        self.waking_up_hour = randint(4,7)

        self.action = "Idle"
        self.state, self.frame_index = "Front", 0
        self.actions = actions
        self.load_character_images()
        
        
        self.image = pygame.transform.scale(self.frames[self.action][self.state][0], (self.default_size, self.default_size))
        self.rect = self.image.get_frect(center = initial_position)
        self.hitbox = pygame.FRect(
            self.rect.left + self.rect.width/2,
            self.rect.top + self.rect.height/3+50,
            self.rect.width/2,
            self.rect.height * 2/3
            )
        
        self.hitbox.center = self.rect.center

        self.original_speed = original_speed
        self.direction = pygame.Vector2()

        #ATTACK
        self.animation_speed = 5
        self.attack_hitbox_list = {
            "Front": (150,70),#width, height
            "Back": (150,70),#width, height
            "Left": (70,150),#width, height
            "Right": (70,150),#width, height
        }
        self.last_attack_time = pygame.time.get_ticks()
        
        self.brain = Brain(self,)
    

        
        
        # === SENSES===
        self.last_called_senses_time = pygame.time.get_ticks()
        self.call_senses_delay = 200


        # === VISÃO: lista de hitboxes à frente ===
        self.vision_max_dist = 150

        # Abordagem simples: “cone” aproximado com N retângulos AABB
        self.vision_segments = 4                               # quantos retângulos formam o cone
        self.vision_step = self.vision_max_dist / self.vision_segments
        self.vision_base_width = self.hitbox.width     # largura inicial
        self.vision_spread_per_seg = max(2, int(self.hitbox.width * 0.12))  # cresce a cada segmento
        self.vision_hitboxes: list[pygame.FRect] = []
        self.update_vision_hitboxes()  # gerar já na criação


        self.attacked_by_character = None

        self.attack_1,self.attack_2 = False,False

        self.attack_delay=5000

        self.specie = "MONSTER"

        self.scripts = {}
    # ---------------------------------------------------------
    # Direção “para onde está olhando”. Se tiver direction != 0,
    # usa ela; senão usa self.state.
    # ---------------------------------------------------------
    def _get_facing_dir(self) -> pygame.Vector2:
        d = self.direction
        if d.x != 0 or d.y != 0:
            try:
                return d.normalize()
            except ValueError:
                pass
        if self.state == "Front":
            return pygame.Vector2(0, 1)
        if self.state == "Back":
            return pygame.Vector2(0, -1)
        if self.state == "Left":
            return pygame.Vector2(-1, 0)
        return pygame.Vector2(1, 0)  # "Right" ou default

    # ---------------------------------------------------------
    # Constrói a lista de retângulos (FRect) à frente do monstro.
    # Retângulos AABB, baratos de checar, bons p/ broad-phase.
    # ---------------------------------------------------------
    def update_vision_hitboxes(self):
        if self.fixed_decided == False:
            if len(self.collision_sprites) > 0:
                self.fixed_decided = True
                self.fixed_sprites =[sprite for sprite in self.collision_sprites if isinstance(sprite, CollisionSprites) and sprite.is_getable ==False]
        facing = self._get_facing_dir()
        origin = pygame.Vector2(self.hitbox.center)

        self.vision_hitboxes.clear()
        step = self.vision_step
        base_w = self.vision_base_width
        spread = self.vision_spread_per_seg

        # Para manter AABB barato:
        # - Se olhando horizontalmente, cada segmento é um retângulo mais comprido no eixo X
        #   e vai “engordando” no eixo Y (largura).
        # - Se olhando verticalmente, análogo ao eixo Y.
        for i in range(1, self.vision_segments + 1):
            center = origin + facing * (i * step)
            widen = base_w + (i - 1) * spread

            if abs(facing.x) > 0:   # olhando p/ esquerda/direita
                rect_w = step       # comprimento do segmento
                rect_h = widen      # “abertura” (altura)
            else:                   # olhando p/ cima/baixo
                rect_w = widen
                rect_h = step

            r = pygame.FRect(0, 0, rect_w, rect_h)
            r.center = (center.x, center.y)

            for colission_box in self.fixed_sprites:
                if colission_box.rect.colliderect(r):
                    return
            self.vision_hitboxes.append(r)

    #SENSES
    def sensed_creature(self,) -> Character:
        self.seeing = ""
        self.hearing = ""

        
        for creature in self.creatures_sprites:
            if creature.personal_name == self.personal_name:
                continue
            if creature == self:
                continue
            if creature.is_human == True:
                continue
            if creature.is_dead == True:
                continue
                
            if self.rect.colliderect(creature.rect):
                return creature

            if self.has_vision:
                    
                # Para manter a "leveza", a condição mais simples é a criatura estar visível
                # e dentro do alcance de visão.
                is_visible = getattr(creature, 'is_visible', True) # Assumindo True se não definido
                
                if is_visible:
                    for vh in self.vision_hitboxes:
                        if vh.colliderect(creature.hitbox):
                            self.seeing = f"seeing {creature.personal_name}"
                            return creature

            if self.has_hearing:
                if creature.is_making_noise:
                    creature_center = pygame.Vector2(creature.rect.center)
                    self_center = pygame.Vector2(self.rect.center)
                    dist = ( creature_center- self_center).length()
                    if dist <= creature.noise_intensity:
                        self.hearing = f"hearing {creature}"
                        return creature      

        return None

    ##Vision
    def can_see_target(monster, target, blockers: pygame.sprite.Group,
                   radius: float = 250.0,
                   fov_deg: float = 90.0,
                   step: float = 8.0,
                   rays: int = 3) -> bool:
        """
        Retorna True se o 'monster' puder ver o 'target'.
        Combina checagem de cone de visão (ângulo + raio)
        e raycast leve (obstáculos).

        Parâmetros:
            monster, target: Sprites com hitbox
            blockers: grupo de colisão (paredes, árvores, etc.)
            radius: distância máxima de visão
            fov_deg: abertura do cone (em graus)
            step: tamanho de passo do raycast
            rays: número de raios testados (centro + laterais)
        """
        origin = pygame.Vector2(monster.hitbox.center)
        to_target = pygame.Vector2(target.hitbox.center) - origin
        dist = to_target.length()
        if dist > radius:
            return False
        if dist == 0:
            return True

        # Vetor de direção do monstro (usando ângulo ou estado)
        angle = atan2(monster.direction.y, monster.direction.x)

        facing = pygame.Vector2(cos(angle), sin(angle))
        to_target_norm = to_target.normalize()
        dot = facing.dot(to_target_norm)
        if dot < cos(radians(fov_deg / 2)):
            return False  # fora do cone de visão

        # Pré-carrega retângulos para desempenho
        blocker_rects = [b.hitbox for b in blockers]

        # Gera raios central + laterais dentro do cone
        base_angle = atan2(facing.y, facing.x)
        half_spread = radians(fov_deg / 6)  # leve variação angular
        offsets = [0.0]
        if rays >= 3:
            offsets += [-half_spread, half_spread]
        elif rays == 5:
            offsets += [-half_spread, half_spread, -2*half_spread, 2*half_spread]

        for off in offsets:
            dir_vec = pygame.Vector2(cos(base_angle + off), sin(base_angle + off))
            pos = origin.copy()
            traveled = 0.0
            while traveled < dist:
                pos += dir_vec * step
                traveled += step
                if any(r.collidepoint(pos) for r in blocker_rects):
                    break  # bloqueado
                if (target.hitbox.collidepoint(pos)):
                    return True  # visão confirmada
        return False

    def update(self, dt: float,):
        self.now = pygame.time.get_ticks()
        if not self.handle_states(dt):
            return
        
        self.position_vector = pygame.Vector2(self.rect.center)
        
        if self.is_dead:
            return
        if self.is_sleeping:
            if self.daytime >= self.waking_up_hour:
                self.is_sleeping = False
                self.is_invisible=False
            return
        if self.is_dying:
            self.action = "Dying"
            if self.frame_index >= len(self.frames[self.action][self.state]):
                self.action="Dead"
                self.is_dead = True
            self.animate(dt)
            return 
        if self.is_handling_damage:
            self.action = "Hurt"
            if self.frame_index >= len(self.frames[self.action][self.state]):
                self.action="Idle"
                self.is_handling_damage = False
            self.animate(dt)
            return
        
        if self.is_chatting:
            self.action = "Idle"
            self.animate(dt)
            if self.current_action:
                self.current_action.update(dt)
            return
        self.dt = dt
        self.regen_life(self.now)
        # if not self.current_action or self.current_action.is_finished():
            # 1) Fugir de um alvo (por ~1.5s ou até ficar longe 220px):
            # move_action = Move(player, mode="flee", threat=orc, duration_ms=1500, flee_until=220)

            # 2) Ir até um ponto:
            # move_action = Move(npc, mode="to", dest=(1200, 640), duration_ms=3000, arrival_radius=10)

            # 3) Passear (wander) por ~2s:
            # self.current_action = Move(self, mode="wander", duration_ms=2000)

        # 2) Ir até um ponto (encerra ao chegar)
        # creat.current_action = Move(creat, mode='to', target_pos=(1200, 640), arrive_radius=24)

        # # 3) Fugir de um ponto (por 1.2s)
        # creat.current_action = Move(creat, mode='from', from_pos=self.player.hitbox.center, duration_ms=1200, speed_multiplier=1.15)

        # self.current_action.update(dt)
        if self.now - self.last_called_senses_time > self.call_senses_delay:
            percepted_monster =self.sensed_creature()
            self.update_vision_hitboxes()
            self.last_called_senses_time = self.now

            important_infos = {
                "percepted_enemy": percepted_monster
            }
            choosen_action = self.brain.choose_action(**important_infos)
            self.current_action = choosen_action
        self.handle_effects()
        
        
        # if now - self.last_called_senses_time >= self.call_senses_delay:
        #     self.last_called_senses_time = now
        # self.move(dt)
        if self.current_action and not self.is_handling_damage:
            self.current_action.update(dt)
        if self.is_running:
            if not self.running_speed_applied:
                self.speed_multipliers.append(self.running_speed_multiplier)
                self.running_speed_applied = True
        else:
            if self.running_speed_applied:
                self.speed_multipliers.remove(self.running_speed_multiplier)
                self.running_speed_applied = False
        
        self.animate(dt)
        self.attack(self.attack_1,self.attack_2)

class Slime(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Winter Slime", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead"]
        original_speed = randint(125, 150)
        default_character_size = DCS
        if randint(0,100)>boss_chance:
            max_hp = randint(20,40)
            attack_damage = randint(4,6)

        else:
            max_hp = randint(80,120)
            attack_damage = randint(10,30)
            default_character_size = randint(DCS, DCS*max_hp//80)
            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        self.attack_hitbox_list = {
            "Front": (self.rect.width//3,70),#width, height
            "Back": (self.rect.width//3,70),#width, height
            "Left": (70,self.rect.width//3),#width, height
            "Right": (70,self.rect.width//3),#width, height
        }
        self.effects_on_damage = []
        self.brain = SlimeBrain(self)
        self.specie = "SLIME"
        self.can_talk = False

    def __str__(self):
        return self.personal_name
    

class Ghost(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Winter Ghost", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead"]
        original_speed = randint(125, 150)
        default_character_size = DCS
        if randint(0,100)>boss_chance:
            max_hp = randint(10,20)
            attack_damage = randint(2,5)

        else:
            max_hp = randint(20,30)
            attack_damage = randint(5,7)
            default_character_size = randint(DCS, DCS*max(max_hp//80, 1))
            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        self.attack_hitbox_list = {
            "Front": (self.rect.width//3,70),#width, height
            "Back": (self.rect.width//3,70),#width, height
            "Left": (70,self.rect.width//3),#width, height
            "Right": (70,self.rect.width//3),#width, height
        }
        self.effects_on_damage = []
        self.brain = GhostBrain(self,)

        self.delete_sprites_on_death = True
        self.specie = "GHOST"
        self.can_talk = False
    def __str__(self):
        return self.personal_name




class ExplorerOrc(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Chefe dos Orcs do Gelo", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead", "Beg", "Begging", "WakeUp"]
        original_speed = randint(125, 150)
        default_character_size = DCS
        if randint(0,100)>boss_chance:
            max_hp = randint(80,120)
            attack_damage = randint(8,10)

        else:
            max_hp = randint(120,160)
            attack_damage = randint(12,20)
            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        self.attack_hitbox_list = {
            "Front": (self.rect.width,70),#width, height
            "Back": (self.rect.width,70),#width, height
            "Left": (70,self.rect.width),#width, height
            "Right": (70,self.rect.width),#width, height
        }
        self.effects_on_damage = []
        self.brain = ExplorerOrcBrain(self,)

        self.delete_sprites_on_death = True
        self.specie = "ORC"
        self.delete_sprites_on_death = False

        self.talks = {
            "1": {  # Introdução
                "fala": "Urgh... Humano... Eu... orc... ferido. Saí pra caçar... pro meu povo... fome... Ajuda?",
                "respostas": {
                    "Claro, o que precisa? Posso te dar comida ou curar sua ferida.": {"pontuacao": 0.8, "next_id": "2_positiva"},
                    "Por que eu ajudaria um orc? Vocês são selvagens.": {"pontuacao": -0.6, "next_id": "2_negativa"},
                    "Onde está caçando? Talvez eu possa ajudar... por um preço.": {"pontuacao": 0.2, "next_id": "2_neutra"},
                    "Fique quieto e morra aí.": {"pontuacao": -1.0, "next_id": "end_negativo"}
                }
            },
            "2_positiva": {
                "fala": "Bom... humano bondoso. Preciso ervas cura... ou carne fresca. Dá pra mim?",
                "respostas": {
                    "Aqui, pegue isso. (Dá item)": {"pontuacao": 0.7, "next_id": "end_positivo"},
                    "Não tenho nada agora, mas volto depois.": {"pontuacao": 0.3, "next_id": "3_positiva"},
                    "Só se me contar segredos da sua tribo.": {"pontuacao": -0.4, "next_id": "2_negativa"}
                }
            },
            "2_negativa": {
                "fala": "Selvagens?! Nós lutamos pela sobrevivência! Você... fraco... covarde!",
                "respostas": {
                    "Desculpe, não quis ofender. Deixe-me ajudar.": {"pontuacao": 0.4, "next_id": "3_neutra"},
                    "Exato, fiquem na floresta e morram de fome!": {"pontuacao": -0.8, "next_id": "end_negativo"},
                    "Tudo bem, me diga o que precisa.": {"pontuacao": 0.1, "next_id": "2_neutra"}
                }
            },
            "2_neutra": {
                "fala": "Caço javali... rio seco... nada. Preço? Ouro? Informação?",
                "respostas": {
                    "Te ajudo de graça, irmão da floresta.": {"pontuacao": 0.5, "next_id": "end_positivo"},
                    "50 moedas e te levo pro acampamento.": {"pontuacao": -0.2, "next_id": "3_neutra"},
                    "Sem chance, boa sorte.": {"pontuacao": -0.5, "next_id": "end_negativo"}
                }
            },
            "3_positiva": {
                "fala": "Obrigado... humano honrado. Volte... tribo lembra favores.",
                "respostas": {
                    "Fico feliz em ajudar. Cuide-se!": {"pontuacao": 0.4, "next_id": "end_positivo"}
                }
            },
            "3_neutra": {
                "fala": "Preço alto... mas aceito. Ajuda salva vida.",
                "respostas": {
                    "Feito. Aqui está.": {"pontuacao": 0.0, "next_id": "end_neutro"}
                }
            },
            "end_positivo": {
                "fala": "Você... bom aliado! Orcs bem-vindos você! Gruul agradece! (Elogia e sorri)",
                "respostas": {}
            },
            "end_negativo": {
                "fala": "Maldito humano traiçoeiro! Orcs esmagam você! Saia! (Ofende e rosna)",
                "respostas": {}
            },
            "end_neutro": {
                "fala": "Transação feita. Sem dívidas.",
                "respostas": {}
            }
        }
        self.current_id = "1"
        self.pontuacao = 0.0
        self.reputacao_orcs = 0.0  # Variável global do jogo, ex: de -1.0 a +1.0
        self.can_talk = True
    

    def processa_escolha(self, escolha: str):
        if escolha == "None":
            return
        respostas = self.talks[self.current_id]["respostas"]
        keys = list(respostas.keys())
        escolha = keys[int(escolha)]
        info = respostas[escolha]
        self.pontuacao += info["pontuacao"]
        self.current_id = info["next_id"]
        return True
    
    def __str__(self):
        return "Orc Explorador"
    
    
    
class Orc(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Orc do Gelo", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead","Beg", "Begging", "WakeUp"]
        original_speed = randint(125, 150)
        default_character_size = DCS
        if randint(0,100)>boss_chance:
            max_hp = randint(20,40)
            attack_damage = randint(4,6)

        else:
            max_hp = randint(80,120)
            attack_damage = randint(10,30)
            default_character_size = randint(DCS, DCS*max_hp//80)
            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        self.attack_hitbox_list = {
            "Front": (self.rect.width//3,70),#width, height
            "Back": (self.rect.width//3,70),#width, height
            "Left": (70,self.rect.width//3),#width, height
            "Right": (70,self.rect.width//3),#width, height
        }
        self.effects_on_damage = []
        self.brain = GhostBrain(self,)

        self.delete_sprites_on_death = True
        self.specie = "ORC"
        self.confiabilidades["HUMAN"] = 0.3
        self.can_talk = True

    def __str__(self):
        return self.personal_name
    
class CrystalGolem(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Snow Crystal Golem", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead"]
        original_speed = randint(125, 150)
        default_character_size = DCS*2.5
        max_hp = 400
        attack_damage = 80

            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        
        self.effects_on_damage = []
        self.brain = GolemBrain(self,)

        self.delete_sprites_on_death = True
        self.specie = "GOLEM"
        self.confiabilidades["HUMAN"] = 0.3
        self.can_talk = False

        self.hitbox.width = 70
        self.hitbox.height = 70
        self.hitbox.center = self.rect.center
        multip = 3
        self.attack_hitbox_list = {
            "Front": (self.hitbox.width*multip,self.hitbox.width*multip),#width, height
            "Back": (self.hitbox.width*multip,self.hitbox.width*multip),#width, height
            "Left": (self.hitbox.width*multip,self.hitbox.width*multip),#width, height
            "Right": (self.hitbox.width*multip,self.hitbox.width*multip),#width, height
        }
        self.use_center_on_attack=True
    def __str__(self):
        return self.personal_name


class Goblin(Monster):
    def __init__(self, *groups, collision_sprites, creatures_sprites, monster_name="Chefe dos Goblins", house_point=(0, 0), initial_position, boss_chance=20):
        actions = ["Walk", "Idle", "Hurt", "Run", "Attack_1","Attack_2", "Dying", "Dead"]
        original_speed = randint(125, 150)
        default_character_size = DCS
        if randint(0,100)>boss_chance:
            max_hp = randint(20,40)
            attack_damage = randint(4,6)

        else:
            max_hp = randint(80,120)
            attack_damage = randint(10,30)
            default_character_size = randint(DCS, DCS*max_hp//80)
            

        super().__init__(*groups, 
            collision_sprites=collision_sprites, 
            creatures_sprites=creatures_sprites, 
            monster_name=monster_name, 
            house_point=house_point, 
            initial_position=initial_position, 
            actions=actions, 
            original_speed=original_speed,
            attack_damage=attack_damage,
            max_hp=max_hp,
            default_character_size=default_character_size
            )

        self.attack_hitbox_list = {
            "Front": (self.rect.width//3,60),#width, height
            "Back": (self.rect.width//3,60),#width, height
            "Left": (60,self.rect.width//3),#width, height
            "Right": (60,self.rect.width//3),#width, height
        }
        self.effects_on_damage = []
        self.brain = SlimeBrain(self)
        self.specie = "GOBLIN"
        self.can_talk = False

    def __str__(self):
        return self.personal_name
