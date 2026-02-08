from Utils.classes_raiz import *
from Utils.actions import *


class Villager(Character):
    
    def __init__(self, *groups, collision_sprites:pygame.sprite.Group,creatures_sprites:pygame.sprite.Group, npc_name="Nina", house_point=(0,0), is_ranged=False, attack_hitbox_list={"Front": (150,70), "Back": (150,70), "Left": (70,150), "Right": (70,150),}, range_distance=36, default_size = HDCS + HHDCS, team_members = [], original_speed:int=200, actions_to_add=[], forma_character:str="", initial_position=None):
        scale_attacks = {
            "Obi": 3,
            "Dash": 1,
            "Nash": 3,
            "Rose": 1,
            "Holz": 2,
            "Fischerin": 2,
            "Sammy": 3,
            "Nina": 1,
            "Verant":1
        }
        super().__init__(*groups, collision_sprites=collision_sprites,creatures_sprites=creatures_sprites, personal_name=npc_name, scale_on_attack_value=scale_attacks[npc_name], is_ranged=is_ranged, range_distance=range_distance, team_members=team_members)
        self.all_groups= groups
        self.is_player = False
        self.is_human = True
        self.npc_name = npc_name

        self.village_rect = pygame.Rect(3800,1400,2200, 2000)
        self.water_sources = [(5528, 2200), (4618, 2836), (4481, 2000) ]
        self.house_point = house_point

        self.forma = forma_character
        self.armor_type = ""
        self.default_folder_path = join(getcwd(), "NPCs", npc_name, self.forma)
        print(f"Caminho completo: {self.default_folder_path} -- {self.forma}")
        self.scripts = load_scripts(self.default_folder_path)
        self.default_size = default_size
        self.waking_up_hour = randint(4,7)

        self.action = "Walk"
        self.state, self.frame_index = "Front", 0
        self.actions = ["Walk", "Idle", "Hurt", "Run","Attack_1", "Attack_2", "Dying", "Dead"] + actions_to_add
        self.actions = ["Walk", "Idle", "Hurt", "Run","Attack_1", "Attack_2", "Dying", "Dead", "Beg", "Begging", "WakeUp"] + actions_to_add
        self.load_character_images()
        
        
        self.image = pygame.transform.scale(self.frames[self.action][self.state][0], (self.default_size, self.default_size))
        self.rect = self.image.get_frect(center = (5010, 3010))
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
        self.attack_hitbox_list = attack_hitbox_list
        self.last_attack_time = pygame.time.get_ticks()
        
        #brain
        self.brains = {
            "Obi": ObiBrain(self,can_attack=True),
            "Dash": LaRochBrothers(self,can_attack=True),
            "Nash": LaRochBrothers(self,can_attack=True),
            "Rose": RoseBrain(self, ),
            "Holz": HolzBrain(self, can_attack=True),
            "Fischerin": FischerinBrain(self, ),
            "Sammy": SammyBrain(self, ),
            "Nina": NinaBrain(self,),
            "Verant": VerantBrain(self,)
        }
        self.brain = self.brains[npc_name]
        
        
        
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


        self.max_hp = 100
        self.hp = 100
        self.attack_damage = 10
        self.attacked_by_character = None

        self.attack_1,self.attack_2 = False,False
        self.specie = "HUMAN"

        self.current_id = "1"
        self.pontuacao = 0.0
        self.confiabilidades["ORC"] = 0.3

        self.can_talk =True

        if initial_position:
            self.rect = self.image.get_frect(center = initial_position)
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
    def sensed_creature(self,):
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
        self.position_vector = pygame.Vector2(self.rect.center)
        
        if not self.handle_states(dt):
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
            if self.brain != None:
                try:
                    choosen_action = self.brain.choose_action(**important_infos)
                except Exception as e:
                    raise Exception(f"Erro ao escolher ação com cérebro {self.brain} do usuário {self}: \n {e}")
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


    def escolhe_fala(self, ):
        fala_data = self.talks.get(self.current_id)
        if not fala_data:
            return "", []
        
        # Verifica se é fim (sem respostas) e aplica reputação
        if not fala_data["respostas"]:
            delta_rep = self.pontuacao * 20  # Exemplo: pontuação alta -> +rep, baixa -> -rep
            return fala_data["fala"], []  # Mostra fala final e encerra
        
        return fala_data["fala"], list(fala_data["respostas"].keys())

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
        return self.npc_name

class Verant(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Verant", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 80, actions_to_add=[], player=None):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)

        self.max_hp = randint(20,30)
        self.hp=self.max_hp
        self.attack_damage = randint(12,20)

        self.encontrou_player = False
        self.player = player
        
        #Falas loop 1 - primeiro encontro
        self.talks_loop_1 = {
            "1": {
                "fala": "Olha só o que os ventos do sul trouxeram. Bem-vindo viajante, à vila de Tod. A vila mais ao norte do continente!",
                "respostas": {
                    "Obrigado. É um lugar bonito.": {"next_id": "2"},
                    "Vocês parecem isolados aqui.": {"next_id": "2_clima"}
                }
            },
            "2": {
                "fala": "Bonito e resistente, como meu povo. Sou o Chefe, responsável por manter todos alimentados e seguros.",
                "respostas": {
                    "Parece uma tarefa difícil.": {"next_id": "end"}
                }
            },
            "2_clima": {
                "fala": "Isolados, mas autossuficientes. O frio é rigoroso, mas nossos estoques são o orgulho deste vale.",
                "respostas": {
                    "Entendo.": {"next_id": "end"}
                }
            },
            "end": {
                "fala": "Aproveite a estadia. Só não se perca no labirinto ao entardecer.",
                "respostas": {}
            }
        }

        self.talks_loop_2 = {
            "1": {
                "fala": "Olha só o que os ventos do sul trouxeram. Bem-vindo viajante, à vila de Tod. A vila mais ao norte do continente!",
                "respostas": {
                    "Obrigado. Não pude deixar de notar que a vila está bem agitada.": {"next_id": "2_tensao"},
                    "Obrigado pela hospitalidade, mas sabe, pela minha experiência um sorriso sempre esconde algo por trás. E você chefe, o que você está escondendo?": {"next_id": "2_direto"}
                }
            },
            "2_tensao": {
                "fala": "Olhos aguçados. O inverno está chegando e os estoques precisam estar trancados. Segurança é nossa prioridade.",
                "respostas": {
                    "Segurança contra o frio ou contra o que está lá fora?": {"next_id": "end"}
                }
            },
            "2_direto": {
                "fala": "Cuidado com as palavras. Um convidado não deve questionar a hospitalidade de quem o protege.",
                "respostas": {
                    "Entendo.": {"next_id": "end"}
                }
            },
            "end": {
                "fala": "Apenas aproveite o dia. Ele costuma ser curto por aqui.",
                "respostas": {}
            }
        }

        self.talks_loop_3 = {
            "1": {
                "fala": "Olha só o que os ventos do sul trouxeram. Bem-vindo viajante, à vila de Tod. A vila mais ao norte do continente!",
                "respostas": {
                    "Obrigado, chefe. Eu vi uma movimentação estranha dos Orcs enquanto vinha para cá. Sabe o que está acontecendo?": {"next_id": "2_tensao"},
                }
            },
            "2_tensao": {
                "fala": "Foi um ano difícil de caça e as tempestades de inverno estão chegando. Mas não precisa se preocupar, nós somos muito melhores nisso então nossos estoques estão cheios!",
                "respostas": {
                    "Uns morrem de sede enquanto outros se afogam...": {"next_id": "end"}
                }
            },
            "end": {
                "fala": "Não é problema meu! Meus deveres acabam nos limites dessa vila. Aproveite sua estada aqui.",
                "respostas": {}
            }
        }
        
        self.talks_loop_4 = {
            "1": {
                "fala": "Olha só o que os ventos do sul trouxeram. Bem-vindo viajante, à vila de Tod. A vila mais ao norte do continente!",
                "respostas": {
                    "Obrigado, chefe, mas eu trago más notícias: essa vila vai ser atacada pelos Orcs essa noite.": {"next_id": "2_alerta"},
                    "Chefe, eu preciso falar com você com urgência. É sobre os Orcs.": {"next_id": "2_alerta_sutil"}
                }
            },

            "2_alerta": {
                "fala": "Atacada? Orcs não marcham até aqui por acaso. São criaturas selvagens demais para tamanha organização.",
                "respostas": {
                    "Eles estão famintos. Não é um ataque por ódio.": {"next_id": "3_fome"},
                    "Você está subestimando o desespero deles.": {"next_id": "3_desespero"}
                }
            },

            "2_alerta_sutil": {
                "fala": "Se isso for mais uma história para assustar meu povo, poupe seu fôlego. Já temos medo suficiente.",
                "respostas": {
                    "Não é história. Eu vi um Orc cair na floresta.": {"next_id": "3_orc"},
                }
            },

            "3_fome": {
                "fala": "Fome? Todos passam fome no inverno. A diferença é que nós nos preparamos.",
                "respostas": {
                    "Vocês se prepararam… eles não.": {"next_id": "4_frio"}
                }
            },

            "3_desespero": {
                "fala": "Desespero não justifica atravessar minhas muralhas com machados.",
                "respostas": {
                    "Então prepare suas muralhas. Eles virão de qualquer forma.": {"next_id": "4_preparo"}
                }
            },

            "3_orc": {
                "fala": "Um Orc morto não é novidade. A floresta sempre cobra seu preço.",
                "respostas": {
                    "Esse não morreu lutando.": {"next_id": "4_frio"}
                }
            },

            "4_frio": {
                "fala": "Mesmo que fosse verdade… o que espera que eu faça? Abrir meus celeiros para monstros?",
                "respostas": {
                    "Espero que você sobreviva à noite.": {"next_id": "end"},
                }
            },

            "4_preparo": {
                "fala": "Se eles ousarem chegar até aqui, encontrarão lanças e fogo.",
                "respostas": {
                    "Então essa noite vai ser longa.": {"next_id": "end"}
                }
            },

            "end": {
                "fala": "A vila de Tod já enfrentou coisas piores do que boatos. Agora, se me der licença, tenho um povo para proteger.",
                "respostas": {}
            }
        }

        self.talks_loop_5 = {
            "1": {
                "fala": "Olha só o que os ventos do sul trouxeram. Bem-vindo viajante, à vila de Tod. A vila mais ao norte do continente!",
                "respostas": {
                    "Obrigado, chefe, mas eu trago más notícias: essa vila vai ser atacada pelos Orcs essa noite.": {"next_id": "2_alerta"},
                    "Chefe, eu preciso falar com você com urgência. É sobre os Orcs.": {"next_id": "2_alerta_sutil"}
                }
            },

            "2_alerta": {
                "fala": "Atacada? Orcs não marcham até aqui por acaso. São criaturas selvagens demais para tamanha organização.",
                "respostas": {
                    "Eles estão famintos. Não é um ataque por ódio.": {"next_id": "3_fome"},
                    "Você está subestimando o desespero deles.": {"next_id": "3_desespero"}
                }
            },

            "2_alerta_sutil": {
                "fala": "Se isso for mais uma história para assustar meu povo, poupe seu fôlego. Já temos medo suficiente.",
                "respostas": {
                    "Não é história. Eu vi um Orc cair na floresta.": {"next_id": "3_orc"},
                }
            },

            "3_fome": {
                "fala": "Fome? Todos passam fome no inverno. A diferença é que nós nos preparamos.",
                "respostas": {
                    "Vocês se prepararam… eles não.": {"next_id": "4_frio"}
                }
            },

            "3_desespero": {
                "fala": "Desespero não justifica atravessar minhas muralhas com machados.",
                "respostas": {
                    "Então prepare suas muralhas. Eles virão de qualquer forma.": {"next_id": "4_preparo"}
                }
            },

            "3_orc": {
                "fala": "Um Orc morto não é novidade. A floresta sempre cobra seu preço.",
                "respostas": {
                    "Esse não morreu lutando.": {"next_id": "4_frio"}
                }
            },

            "4_frio": {
                "fala": "Mesmo que fosse verdade… o que espera que eu faça? Abrir meus celeiros para monstros?",
                "respostas": {
                    "Espero que você sobreviva à noite.": {"next_id": "end"},
                }
            },

            "4_preparo": {
                "fala": "Se eles ousarem chegar até aqui, encontrarão lanças e fogo.",
                "respostas": {
                    "Então essa noite vai ser longa.": {"next_id": "end"}
                }
            },

            "end": {
                "fala": "A vila de Tod já enfrentou coisas piores do que boatos. Agora, se me der licença, tenho um povo para proteger.",
                "respostas": {}
            }
        }

        self.talks_loop_5_sucesso = {
            "1": {
                "fala": (
                    "Vejo pelo seu rosto que algo mudou. \n"
                    "Ou você traz boas notícias… ou veio me dizer que eu estava certo desde o início."
                ),
                "respostas": {
                    "O ataque foi suspenso.": {"next_id": "2_suspenso"},
                    "Eu falei com o chefe dos orcs.": {"next_id": "2_suspenso"}
                }
            },

            "2_suspenso": {
                "fala": (
                    "Suspenso? \n"
                    "Orcs não suspendem ataques. Eles vencem ou morrem tentando."
                ),
                "respostas": {
                    "Eles estão famintos, não sedentos por guerra.": {"next_id": "3_fome"},
                    "Eles recuaram porque ainda há uma saída sem sangue.": {"next_id": "3_saida"}
                }
            },

            "3_fome": {
                "fala": (
                    "Fome… \n"
                    "Meu povo também passa fome no inverno. A diferença é que eu os preparei."
                ),
                "respostas": {
                    "Preparou alguns, enquanto outros morrem do lado de fora.": {"next_id": "4_confronto"},
                }
            },

            "3_saida": {
                "fala": (
                    "E essa saída exige o quê? \n"
                    "Que eu abra meus celeiros para monstros?"
                ),
                "respostas": {
                    "Exige racionamento. Para todos.": {"next_id": "4_racionamento"},
                    "Exige que você governe, não acumule.": {"next_id": "4_confronto"}
                }
            },

            "4_confronto": {
                "fala": (
                    "Cuidado. \n"
                    "Você fala como se entendesse o peso de manter uma vila inteira viva."
                ),
                "respostas": {
                    "Eu entendo o peso de enterrar vilas inteiras.": {"next_id": "5_verdade"},
                    "Você não está protegendo seu povo. Está protegendo seu controle.": {"next_id": "5_verdade"}
                }
            },

            "4_racionamento": {
                "fala": (
                    "Racionamento causa pânico. \n"
                    "Pânico vira revolta. Revolta derruba chefes."
                ),
                "respostas": {
                    "A guerra derruba tudo.": {"next_id": "5_verdade"},
                    "Dividir comida custa menos do que reconstruir cinzas.": {"next_id": "5_verdade"}
                }
            },

            "5_verdade": {
                "fala": (
                    "… \n"
                    "Se meu povo souber que eu escondi comida enquanto outros morriam…"
                ),
                "respostas": {
                    "Então seja lembrado como quem mudou o curso da história.": {"next_id": "end_positivo"},
                    "Ou seja lembrado como o último chefe de Tod.": {"next_id": "end_positivo"}
                }
            },

            "end_positivo": {
                "fala": (
                    "Você me colocou diante de uma escolha que evitei por tempo demais. \n"
                    "Se os Orcs ficarem… haverá regras. Vigilância. Troca justa."
                    "\n\nMas se houver paz esta noite… será porque alguém teve coragem de dividir."
                ),
                "respostas": {}
            }
        }

        self.talks_loop_5_fracasso = {
            "1": {
                "fala": (
                    "Vejo pelo seu rosto que algo mudou. \n"
                    "Aquelas criaturas não aceitaram um acordo, não é?."
                ),
                "respostas": {
                    "Eu falhei em convencê-lo.": {"next_id": "2_suspenso"},
                    "Você é um tolo se está mais preocupado em estar certo do que com o futuro da vila.": {"next_id": "2_suspenso"}
                }
            },

            "2_suspenso": {
                "fala": (
                    "Nem por um segundo eu acreditei que seria possível dialogar com aquelas criaturas."
                ),
                "respostas": {
                    "Então agora só resta o derramamento de sangue...": {"next_id": "3_fome"},
                }
            },

            "3_fome": {
                "fala": "Exato! E Tod irá impedir esses selvagens!",
                "respostas": {}
            },


        }

        vr = self.village_rect #village rect
        matriz_mundo = self.groups()[0].world_matriz

        self.locais_patrulha = []
        for _ in range(0,200):
            x, y = randint(vr.left, vr.right), randint(vr.top, vr.bottom)
            if matriz_mundo[x//GRID_SIZE][y//GRID_SIZE] != 1 and (x,y) not in self.locais_patrulha:
                self.locais_patrulha.append((x,y))
        
    def escolhe_fala(self, ):
        #falas 1 a 4 dependem do loop de morte do jogador. 
        #falas 5 só são desbloqueadas depois de falar com o chefe dos orcs e conseguir convencer ele a suspender o ataque.
    
        loop = self.player.loop

        if self.player.falou_chefe_orcs:
            if self.player.convenceu_chefe_orcs:
                falas = {
                    1: self.talks_loop_5_sucesso,
                }
            else:
                falas = {
                    1: self.talks_loop_5_fracasso,
                }
        else:
            falas = {
                1: self.talks,
                2: self.talks_loop_2,
                3: self.talks_loop_3,
                4: self.talks_loop_4,
                5: self.talks_loop_5,
            }
        if loop not in falas.keys():
            loop = choice(list(falas.keys()))

        

        fala_data = falas[loop].get(self.current_id)
        if not fala_data:
            return "", []
        
        # Verifica se é fim (sem respostas) e aplica reputação
        if not fala_data["respostas"]:
            delta_rep = self.pontuacao * 20  # Exemplo: pontuação alta -> +rep, baixa -> -rep
            return fala_data["fala"], []  # Mostra fala final e encerra
        
        return fala_data["fala"], list(fala_data["respostas"].keys())


class Nina(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS - HHDCS, team_members=[], original_speed = 200, actions_to_add=[], player):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add, )
        self.encontrou_player = False
        self.player = player
        
        #Falas loop 1
        self.talks = {
            "1": {  # Encontro inicial com Nina
                "fala": "Oi. Você não é daqui, é?",
                "respostas": {
                    "Não. Cheguei hoje.": {"pontuacao": 0, "next_id": "2"},
                    "Não sou, não.": {"pontuacao": 0, "next_id": "2"},
                    "Oi.": {"pontuacao": 0, "next_id": "end_curto"}
                }
            },
            "2": {  
                "fala": "Eu sei que você não é. Conheço todo mundo que mora aqui no vale. (sorriso)",
                "respostas": {
                    "Onde eu estou?": {"pontuacao": 0, "next_id": "2_vale"},
                }
            },
            "2_vale": {  
                "fala": "Bem vindo viajante, ao Vale do Retorno! Só não sei por que chamam assim, já que todo mundo que vai embora nunca quer voltar...",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },

            "2_conversa": {
                "fala": "Eu fico aqui de manhã. Dá pra ver o vale inteiro daqui.",
                "respostas": {
                    "O que você está vendo agora?": {"pontuacao": 0, "next_id": "5"},
                    "É um bom lugar.": {"pontuacao": 0, "next_id": "3"}
                }
            },

            "3": {
                "fala": "Quando alguém passa correndo, eu imagino pra onde está indo.",
                "respostas": {
                    "E pra onde você acha que eu estou indo?": {"pontuacao": 0, "next_id": "4"},
                    "Você parece gostar daqui.": {"pontuacao": 0, "next_id": "5"},
                    "Faz sentido.": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "4": {
                "fala": "Você? Ainda não sei.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "5": {  
                "fala": "Hoje todo mundo parece agitado. É estranho.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },

            "6": {
                "fala": "Mas logo passa.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "end"}
                }
            },

            "end": {
                "fala": "Boa sorte… hoje",
                "respostas": {}
            },
            "end_curto": {
                "fala": "Oi.",
                "respostas": {}
            }
        }

        self.talks_loop_2 = {
            "1": {  # Encontro inicial com Nina
                "fala": "Oi. Você não é daqui, é?",
                "respostas": {
                    "Não. Cheguei hoje.": {"pontuacao": 0, "next_id": "2"},
                    "Não sou, não.": {"pontuacao": 0, "next_id": "2"},
                    "Oi.": {"pontuacao": 0, "next_id": "end_curto"}
                }
            },
            "2": {  
                "fala": "Eu sei que você não é. Conheço todo mundo que mora aqui no vale.",
                "respostas": {
                    "Onde eu estou?": {"pontuacao": 0, "next_id": "2_vale"},
                    "É, imaginei que você soubesse.": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },
            "2_vale": {  
                "fala": "Vale do Retorno. Nome estranho, né? Quase ninguém volta",
                "respostas": {
                    "Você ficaria surpresa.": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },

            "2_conversa": {
                "fala": "Eu fico aqui de manhã. Gosto de olhar tudo antes de ficar cheio.",
                "respostas": {
                    "Está vendo alguma coisa estranha agora?": {"pontuacao": 0, "next_id": "5_quieto"},
                    "É um bom lugar.": {"pontuacao": 0, "next_id": "3"}
                }
            },

            "3": {
                "fala": "Quando alguém passa correndo, eu fico pensando se já vi isso antes.",
                "respostas": {
                    "... E o que você tem a dizer sobre mim?": {"pontuacao": 0, "next_id": "4"},
                    "...": {"pontuacao": 0, "next_id": "5"},
                }
            },

            "4": {
                "fala": "Você… parece meio confuso.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "5_quieto": {  
                "fala": "Eu vi um orc entrando no labirinto da floresta mas ele ainda não saiu. Foi bem estranho.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },
            "5": {  
                "fala": "Sabe, hoje todo mundo está mais agitado que o normal. Isso me dá um frio na barriga.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5_quieto"}
                }
            },

            "6": {
                "fala": "Mas deve ser só impressão.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "end"}
                }
            },

            "end": {
                "fala": "Boa sorte hoje.",
                "respostas": {}
            },
            "end_curto": {
                "fala": "Oi.",
                "respostas": {}
            }
        }

        self.talks_loop_3 = {
            "1": {  # Encontro inicial com Nina
                "fala": "Oi… você voltou?",
                "respostas": {
                    "Você me conhece?": {"pontuacao": 0, "next_id": "2"},
                    "Voltei... Sabe quem eu sou?": {"pontuacao": 0, "next_id": "2"},
                    "Oi.": {"pontuacao": 0, "next_id": "end_curto"}
                }
            },
            "2": {  
                "fala": "Desculpa. Achei que já tinha te visto antes.",
                "respostas": {
                    "Onde eu estou?": {"pontuacao": 0, "next_id": "2_vale"},
                }
            },
            "2_vale": {  
                "fala": "Vale do Retorno. Nome estranho, né? Quase ninguém volta",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },

            "2_conversa": {
                "fala": "Eu fico aqui de manhã. Alguém sempre passa por aqui cedo.",
                "respostas": {
                    "O que você vê daí?": {"pontuacao": 0, "next_id": "5_quieto"},
                    "É um bom lugar.": {"pontuacao": 0, "next_id": "3"}
                }
            },

            "3": {
                "fala": "Quando alguém corre, eu tento lembrar de onde conheço o passo.",
                "respostas": {
                    "Você reconhece os meus?": {"pontuacao": 0, "next_id": "4"},
                    "Você parece gostar daqui.": {"pontuacao": 0, "next_id": "5"},
                    "Faz sentido.": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "4": {
                "fala": "Um pouco... Como se eu já tivesse ouvido antes.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "5_quieto": {  
                "fala": "Hoje tá agitado… de novo.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },
            "5": {  
                "fala": "Hoje tá agitado… de novo.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },

            "6": {
                "fala": "Não gosto quando fica assim.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "end"}
                }
            },

            "end": {
                "fala": "Se cuida hoje.",
                "respostas": {}
            },
            "end_curto": {
                "fala": "Oi.",
                "respostas": {}
            }
        }
        
        self.talks_loop_4 = {
            "1": {  # Encontro inicial com Nina
                "fala": "Você chegou cedo hoje.",
                "respostas": {
                    "Você me conhece?": {"pontuacao": 0, "next_id": "2"},
                    "Cheguei... Sabe quem eu sou?": {"pontuacao": 0, "next_id": "2"},
                    "Oi.": {"pontuacao": 0, "next_id": "end_curto"}
                }
            },
            "2": {  
                "fala": "Conheço todo mundo daqui… menos você. Ainda.",
                "respostas": {
                    "Onde eu estou?": {"pontuacao": 0, "next_id": "2_vale"},
                }
            },
            "2_vale": {  
                "fala": "Vale do Retorno. Talvez o nome faça sentido pra alguns.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },

            "2_conversa": {
                "fala": "De manhã tudo parece possível.",
                "respostas": {
                    "Como estão as coisas hoje?": {"pontuacao": 0, "next_id": "5_quieto"},
                    "Você é esperta. Tem alguma coisa pra dizer pra mim?": {"pontuacao": 0, "next_id": "3"}
                }
            },

            "3": {
                "fala": "Quando alguém corre, geralmente já tá atrasado.",
                "respostas": {
                    "E o que tem a dizer sobre mim?": {"pontuacao": 0, "next_id": "4"},
                    "Tem razao...": {"pontuacao": 0, "next_id": "5"},
                }
            },

            "4": {
                "fala": "Você não devia ficar parado.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "5_quieto": {  
                "fala": "Hoje tá agitado… de novo.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },
            "5": {  
                "fala": "Hoje tá agitado… de novo.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },

            "6": {
                "fala": "Não gosto quando fica assim.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "end"}
                }
            },

            "end": {
                "fala": "Se cuida hoje.",
                "respostas": {}
            },
            "end_curto": {
                "fala": "Oi.",
                "respostas": {}
            }
        }

        self.talks_loop_5 = {
            "1": {  # Encontro inicial com Nina
                "fala": "Ah… é você.",
                "respostas": {
                    "Você me conhece?": {"pontuacao": 0, "next_id": "2"},
                    "Sim... Sou eu.": {"pontuacao": 0, "next_id": "2"},
                    "Oi.": {"pontuacao": 0, "next_id": "end_curto"}
                }
            },
            "2": {  
                "fala": "Você sempre aparece quando o vale tá assim.",
                "respostas": {
                    "O que quer dizer?": {"pontuacao": 0, "next_id": "2_vale"},
                }
            },
            "2_vale": {  
                "fala": "Vale do Retorno. Alguns voltam porque precisam.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "2_conversa"},
                }
            },

            "2_conversa": {
                "fala": "Eu fico aqui de manhã. Depois disso… não gosto.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5_quieto"},
                    "Vai dar tudo certo dessa vez.": {"pontuacao": 0, "next_id": "3"}
                }
            },

            "3": {
                "fala": "Você sabe pra onde tá indo. Dá pra ver.",
                "respostas": {
                    "Dessa vez eu sei.": {"pontuacao": 0, "next_id": "5_quieto"},
                }
            },

            "4": {
                "fala": "Você não devia ficar parado.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },

            "5_quieto": {  
                "fala": "Hoje tá agitado demais.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "5"}
                }
            },
            "5": {  
                "fala": "Quando fica assim… algo já foi decidido.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "6"}
                }
            },

            "6": {
                "fala": "Não gosto quando fica assim.",
                "respostas": {
                    "...": {"pontuacao": 0, "next_id": "end"}
                }
            },

            "end": {
                "fala": "Não chega tarde.",
                "respostas": {}
            },
            "end_curto": {
                "fala": "Oi.",
                "respostas": {}
            }
        }

        self.locais_patrulha = []
        vr_left = 3972 #village rect
        vr_right = 6000
        vr_top = 0
        vr_bottom = 1075
        vr = self.village_rect #village rect
        matriz_mundo = self.groups()[0].world_matriz

        self.locais_patrulha = []
        self.locais_montanha = []

        for _ in range(0,200):
            x, y = randint(vr_left, vr_right), randint(vr_top, vr_bottom)
            if matriz_mundo[x//GRID_SIZE][y//GRID_SIZE] != 1 and (x,y) not in self.locais_patrulha:
                self.locais_montanha.append((x,y))

        for _ in range(0,200):
            x, y = randint(vr.left, vr.right), randint(vr.top, vr.bottom)
            if matriz_mundo[x//GRID_SIZE][y//GRID_SIZE] != 1 and (x,y) not in self.locais_patrulha:
                self.locais_patrulha.append((x,y))

    def escolhe_fala(self, ):

        loop = self.player.loop

        falas = {
            1: self.talks,
            2: self.talks_loop_2,
            3: self.talks_loop_3,
            4: self.talks_loop_4,
            5: self.talks_loop_5,
        }
        if loop not in falas.keys():
            loop = choice(list(falas.keys()))

        

        fala_data = falas[loop].get(self.current_id)
        if not fala_data:
            return "", []
        
        # Verifica se é fim (sem respostas) e aplica reputação
        if not fala_data["respostas"]:
            delta_rep = self.pontuacao * 20  # Exemplo: pontuação alta -> +rep, baixa -> -rep
            return fala_data["fala"], []  # Mostra fala final e encerra
        
        return fala_data["fala"], list(fala_data["respostas"].keys())

class Dash(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[]):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)

        self.talks = {
        "1": {  # Introdução
            "fala": "Ei, estranho... Eu sou Dash, caçador da vila. Estou abatendo alguns monstros nas redondezas. Você parece saber se virar... Ajuda na caçada?",
            "respostas": {
                "Claro, vamos caçar juntos. Posso ajudar com minha habilidade.": {"pontuacao": 0.8, "next_id": "2_positiva"},
                "Por que eu me arriscaria por uma vila que nem conheço?": {"pontuacao": -0.6, "next_id": "2_negativa"},
                "Talvez, se houver uma recompensa envolvida.": {"pontuacao": 0.2, "next_id": "2_neutra"},
                "Caçe sozinho, não é problema meu.": {"pontuacao": -1.0, "next_id": "end_negativo"}
            }
        },
        "2_positiva": {
            "fala": "Ótimo! Um aliado confiável. Preciso de alguém pra cobrir as florestas enquanto miro com o arco. Tem armadilhas ou iscas?",
            "respostas": {
                "Aqui, use isso. (Fornece item)": {"pontuacao": 0.7, "next_id": "end_positivo"},
                "Não tenho agora, mas posso rastrear pegadas.": {"pontuacao": 0.3, "next_id": "3_positiva"},
                "Só se me der parte do couro do lobo.": {"pontuacao": -0.4, "next_id": "2_negativa"}
            }
        },
        "2_negativa": {
            "fala": "Arriscar? A vila protege viajantes como você! Egoísta... Mas se mudar de ideia, prove seu valor.",
            "respostas": {
                "Desculpe, foi rude. Vamos caçar.": {"pontuacao": 0.4, "next_id": "3_neutra"},
                "A vila que se vire sozinha!": {"pontuacao": -0.8, "next_id": "end_negativo"},
                "Tudo bem, o que precisa exatamente?": {"pontuacao": 0.1, "next_id": "2_neutra"}
            }
        },
        "2_neutra": {
            "fala": "Recompensa? A vila paga bem por caçadas. 20 moedas se pegarmos o lobo. Aceita?",
            "respostas": {
                "Aceito, e ajudo de boa vontade.": {"pontuacao": 0.5, "next_id": "end_positivo"},
                "Faça 50 moedas e eu lidero a caçada.": {"pontuacao": -0.2, "next_id": "3_neutra"},
                "Esquece, boa sorte sozinho.": {"pontuacao": -0.5, "next_id": "end_negativo"}
            }
        },
        "3_positiva": {
            "fala": "Apreciado. Volte quando puder; a vila valoriza aliados como você.",
            "respostas": {
                "Conte comigo. Fique seguro!": {"pontuacao": 0.4, "next_id": "end_positivo"}
            }
        },
        "3_neutra": {
            "fala": "50 é justo pelo risco. Vamos nessa, parceiro.",
            "respostas": {
                "Combinado. Vamos caçar.": {"pontuacao": 0.0, "next_id": "end_neutro"}
            }
        },
        "end_positivo": {
            "fala": "Você é um verdadeiro herói! A vila te deve uma. Venha pra fogueira depois! (Sorri e agradece)",
            "respostas": {}
        },
        "end_negativo": {
            "fala": "Covarde! Não volte pra vila se precisar de ajuda!",
            "respostas": {}
        },
        "end_neutro": {
            "fala": "Negócio fechado. Sem mais obrigações.",
            "respostas": {}
        }
    }
        
        self.max_hp = randint(20,30)
        self.attack_damage = randint(12,20)

class Nash(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[]):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)

        self.talks = {
            "1": {  # Introdução
                "fala": "Você pisa leve demais pra ser só mais um viajante. Sou Nash, caçadora da vila. As trilhas estão perigosas… e eu não gosto de trabalhar com desconhecidos.",
                "respostas": {
                    "Fico na retaguarda e não atrapalho. Sei seguir ordens.": {"pontuacao": 0.6, "next_id": "2_positiva"},
                    "Desconfiada assim não vai longe. Precisa de ajuda ou não?": {"pontuacao": -0.5, "next_id": "2_negativa"},
                    "Depende. O que você está caçando exatamente?": {"pontuacao": 0.2, "next_id": "2_neutra"},
                    "Não tenho tempo pra caçadora paranoica.": {"pontuacao": -1.0, "next_id": "end_negativo"}
                }
            },
            "2_positiva": {
                "fala": "Bom. Disciplina é rara. Estou rastreando um javali corrompido. Forte, rápido… e esperto demais.",
                "respostas": {
                    "Posso distrair a fera enquanto você finaliza.": {"pontuacao": 0.7, "next_id": "end_positivo"},
                    "Consigo montar uma emboscada com o terreno.": {"pontuacao": 0.4, "next_id": "3_positiva"},
                    "Só entro se ficar com as presas do javali.": {"pontuacao": -0.3, "next_id": "2_negativa"}
                }
            },
            "2_negativa": {
                "fala": "Cuidado com o tom. A última pessoa que me provocou virou isca.",
                "respostas": {
                    "Não foi minha intenção. Vamos focar na caçada.": {"pontuacao": 0.3, "next_id": "3_neutra"},
                    "Ameaças não funcionam comigo.": {"pontuacao": -0.7, "next_id": "end_negativo"},
                    "Então me diga o plano e eu ajudo.": {"pontuacao": 0.1, "next_id": "2_neutra"}
                }
            },
            "2_neutra": {
                "fala": "Um javali desses rende bem. A vila paga 30 moedas… se voltarmos vivos.",
                "respostas": {
                    "Fechado. Vamos fazer isso direito.": {"pontuacao": 0.4, "next_id": "end_positivo"},
                    "Quero 60 moedas e a liderança.": {"pontuacao": -0.2, "next_id": "3_neutra"},
                    "Arriscado demais pra mim.": {"pontuacao": -0.5, "next_id": "end_negativo"}
                }
            },
            "3_positiva": {
                "fala": "Você pensa antes de agir. Gosto disso. Volte quando quiser caçar de verdade.",
                "respostas": {
                    "Estarei por perto. Boa caça.": {"pontuacao": 0.4, "next_id": "end_positivo"}
                }
            },
            "3_neutra": {
                "fala": "Não confio fácil, mas aceito o acordo. Não me faça arrepender.",
                "respostas": {
                    "Sem promessas vazias. Só resultados.": {"pontuacao": 0.0, "next_id": "end_neutro"}
                }
            },
            "end_positivo": {
                "fala": "Você sobreviveu… e ajudou. Isso já te coloca acima da maioria. A vila vai lembrar do seu nome.",
                "respostas": {}
            },
            "end_negativo": {
                "fala": "Suma das minhas trilhas antes que vire parte da paisagem.",
                "respostas": {}
            },
            "end_neutro": {
                "fala": "Acordo cumprido. Nada mais, nada menos.",
                "respostas": {}
            }
        }
        
        self.max_hp = randint(20,30)
        self.attack_damage = randint(12,20)

class Obi(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[]):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)
        self.locais_patrulha = []
        vr = self.village_rect #village rect
        matriz_mundo = self.groups()[0].world_matriz

        self.locais_patrulha = []
        for _ in range(0,200):
            x, y = randint(vr.left, vr.right), randint(vr.top, vr.bottom)
            if matriz_mundo[x//GRID_SIZE][y//GRID_SIZE] != 1 and (x,y) not in self.locais_patrulha:
                self.locais_patrulha.append((x,y))
        
        self.talks = {
        "1": {  # Introdução
            "fala": "Pare aí. A vila anda tensa, e eu não deixo qualquer um circular livremente. Sou Obi, guarda da vila. Diga por que está aqui.",
            "respostas": {
                "Só estou de passagem. Não quero problemas.": {"pontuacao": 0.3, "next_id": "2_neutra"},
                "Posso ajudar na patrulha se precisar.": {"pontuacao": 0.6, "next_id": "2_positiva"},
                "Isso é um interrogatório ou você sempre trata assim?": {"pontuacao": -0.5, "next_id": "2_negativa"},
                "Saia da minha frente ou vai se arrepender.": {"pontuacao": -1.0, "next_id": "end_negativo"}
            }
        },
        "2_positiva": {
            "fala": "Ajuda é bem-vinda… desde que siga ordens. Temos relatos de movimentação estranha perto do portão norte.",
            "respostas": {
                "Posso vigiar enquanto você faz a ronda interna.": {"pontuacao": 0.7, "next_id": "end_positivo"},
                "Prefiro investigar sozinho e te reportar depois.": {"pontuacao": 0.4, "next_id": "3_positiva"},
                "Só se tiver alguma recompensa envolvida.": {"pontuacao": -0.3, "next_id": "2_neutra"}
            }
        },
        "2_negativa": {
            "fala": "Atitude suspeita. Não me obrigue a te retirar da vila à força.",
            "respostas": {
                "Calma, só estava testando. Vamos conversar.": {"pontuacao": 0.2, "next_id": "3_neutra"},
                "Tente a sorte.": {"pontuacao": -0.8, "next_id": "end_negativo"},
                "O que está acontecendo exatamente?": {"pontuacao": 0.1, "next_id": "2_neutra"}
            }
        },
        "2_neutra": {
            "fala": "Se ficar, siga as regras. Patrulha reforçada rende 15 moedas por turno.",
            "respostas": {
                "Aceito. Ordem é ordem.": {"pontuacao": 0.4, "next_id": "end_positivo"},
                "Quinze é pouco. Quero 30.": {"pontuacao": -0.2, "next_id": "3_neutra"},
                "Prefiro não me envolver.": {"pontuacao": -0.5, "next_id": "end_negativo"}
            }
        },
        "3_positiva": {
            "fala": "Você se move bem e não chama atenção. Isso é útil pra um guarda.",
            "respostas": {
                "Fico feliz em ajudar a manter a vila segura.": {"pontuacao": 0.4, "next_id": "end_positivo"}
            }
        },
        "3_neutra": {
            "fala": "Não gosto de negociar, mas a vila precisa de braços. Só não cause problemas.",
            "respostas": {
                "Sem confusão. Só trabalho.": {"pontuacao": 0.0, "next_id": "end_neutro"}
            }
        },
        "end_positivo": {
            "fala": "Bom trabalho. Enquanto eu estiver de guarda, você é bem-vindo na vila.",
            "respostas": {}
        },
        "end_negativo": {
            "fala": "Chega. Fora da vila. Agora.",
            "respostas": {}
        },
        "end_neutro": {
            "fala": "Faça seu serviço e siga seu caminho. Nada além disso.",
            "respostas": {}
        }
    }
    
        self.max_hp = randint(40,60)
        self.attack_damage = randint(24,40)

class Rose(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[]):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)

        self.talks = {
            "1": {  # Introdução
                "fala": "Ah… passos cansados. Eu reconheço esse som. Sou Rose, cuido dos feridos e dos que ainda fingem estar bem. O que te traz até mim, filho?",
                "respostas": {
                    "Preciso de ajuda. Estou machucado.": {"pontuacao": 0.6, "next_id": "2_positiva"},
                    "Só queria conversar um pouco.": {"pontuacao": 0.4, "next_id": "2_neutra"},
                    "Curandeira, faça seu trabalho rápido.": {"pontuacao": -0.6, "next_id": "2_negativa"},
                    "Não confio em remédios e superstições.": {"pontuacao": -1.0, "next_id": "end_negativo"}
                }
            },
            "2_positiva": {
                "fala": "Machucados no corpo são fáceis. Difícil é tratar o que sangra por dentro. Sente-se, vou cuidar de você.",
                "respostas": {
                    "Obrigado, Rose. A vila tem sorte de ter você.": {"pontuacao": 0.7, "next_id": "end_positivo"},
                    "Não se preocupe, já aguentei coisa pior.": {"pontuacao": 0.3, "next_id": "3_positiva"},
                    "Isso vai me custar quanto?": {"pontuacao": -0.2, "next_id": "2_neutra"}
                }
            },
            "2_neutra": {
                "fala": "Conversas também curam, às vezes mais que ervas. Mas o tempo não espera. O que deseja saber?",
                "respostas": {
                    "O que anda acontecendo com a vila?": {"pontuacao": 0.5, "next_id": "3_positiva"},
                    "Preciso só de algo para seguir viagem.": {"pontuacao": 0.1, "next_id": "3_neutra"},
                    "Nada. Foi perda de tempo.": {"pontuacao": -0.5, "next_id": "end_negativo"}
                }
            },
            "2_negativa": {
                "fala": "Cuidado com as palavras. Já vi muita gente forte cair por menos.",
                "respostas": {
                    "Perdão, estou exausto.": {"pontuacao": 0.3, "next_id": "3_neutra"},
                    "Não preciso de sermões.": {"pontuacao": -0.7, "next_id": "end_negativo"},
                    "Só diga se pode ajudar ou não.": {"pontuacao": 0.0, "next_id": "2_neutra"}
                }
            },
            "3_positiva": {
                "fala": "A vila sente medo. Dash luta com o coração, Nash com a cabeça… e Obi carrega o peso de todos. Você pode ser o equilíbrio.",
                "respostas": {
                    "Vou fazer o possível para ajudar.": {"pontuacao": 0.6, "next_id": "end_positivo"},
                    "Não prometo nada, mas ouvirei.": {"pontuacao": 0.2, "next_id": "end_neutro"}
                }
            },
            "3_neutra": {
                "fala": "Leve estas ervas. Não curam tudo, mas ajudam a seguir em frente.",
                "respostas": {
                    "Agradeço. Já é mais do que esperava.": {"pontuacao": 0.3, "next_id": "end_neutro"}
                }
            },
            "end_positivo": {
                "fala": "Vá com cuidado, meu filho. A vila precisa de mais gente que escute antes de agir.",
                "respostas": {}
            },
            "end_negativo": {
                "fala": "Quando a dor apertar, talvez lembre das minhas palavras… ou talvez seja tarde.",
                "respostas": {}
            },
            "end_neutro": {
                "fala": "O caminho continua. Cabe a você como trilhá-lo.",
                "respostas": {}
            }
        }

class Holz(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Nina", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[]):
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)

        self.talks = {
            "1": {  # Introdução
                "fala": "Cuidado onde pisa. Um golpe errado de machado e ninguém volta inteiro pra casa. Sou Holz… corto lenha pra vila desde antes de você aparecer.",
                "respostas": {
                    "Só estou observando. Não quero atrapalhar.": {"pontuacao": 0.4, "next_id": "2_neutra"},
                    "Posso ajudar com o trabalho, se quiser.": {"pontuacao": 0.6, "next_id": "2_positiva"},
                    "Trabalho pesado pra pouca recompensa, não acha?": {"pontuacao": -0.4, "next_id": "2_negativa"},
                    "Sai da frente, tenho coisas mais importantes.": {"pontuacao": -1.0, "next_id": "end_negativo"}
                }
            },
            "2_positiva": {
                "fala": "Ajuda sempre é bem-vinda. As florestas andam estranhas… árvores caindo sozinhas, bichos fugindo do nada.",
                "respostas": {
                    "Posso vigiar enquanto você corta.": {"pontuacao": 0.5, "next_id": "3_positiva"},
                    "Se algo atacar, eu seguro a criatura.": {"pontuacao": 0.7, "next_id": "end_positivo"},
                    "Só se dividir o pagamento.": {"pontuacao": -0.3, "next_id": "2_neutra"}
                }
            },
            "2_neutra": {
                "fala": "Observar é melhor que atrapalhar. Se ficar, mantenha distância do machado.",
                "respostas": {
                    "Entendido. Segurança primeiro.": {"pontuacao": 0.3, "next_id": "3_neutra"},
                    "Já vi coisa pior.": {"pontuacao": -0.2, "next_id": "2_negativa"},
                    "Vou seguir meu caminho então.": {"pontuacao": -0.4, "next_id": "end_negativo"}
                }
            },
            "2_negativa": {
                "fala": "Pouca recompensa? Essa lenha aquece crianças e mantém a vila de pé.",
                "respostas": {
                    "Não quis desrespeitar. Me expressei mal.": {"pontuacao": 0.3, "next_id": "3_neutra"},
                    "Cada um escolhe o peso que carrega.": {"pontuacao": -0.6, "next_id": "end_negativo"},
                    "O que anda acontecendo na floresta?": {"pontuacao": 0.1, "next_id": "2_neutra"}
                }
            },
            "3_positiva": {
                "fala": "Você não foge do trabalho duro. Gosto disso. A vila precisa de gente assim.",
                "respostas": {
                    "Faço o que precisa ser feito.": {"pontuacao": 0.4, "next_id": "end_positivo"}
                }
            },
            "3_neutra": {
                "fala": "Não confio fácil, mas você não parece problema.",
                "respostas": {
                    "Já é um começo.": {"pontuacao": 0.0, "next_id": "end_neutro"}
                }
            },
            "end_positivo": {
                "fala": "Se precisar de lenha, abrigo ou uma mão firme… me procure. Você é amigo da vila.",
                "respostas": {}
            },
            "end_negativo": {
                "fala": "Vai. Antes que eu diga algo que não possa desfazer.",
                "respostas": {}
            },
            "end_neutro": {
                "fala": "Cada um segue seu caminho. O meu começa antes do amanhecer.",
                "respostas": {}
            }
        }

        self.max_hp = randint(20,30)
        self.attack_damage = randint(12,20)

class Sammy(Villager):
    def __init__(self, *groups, collision_sprites, creatures_sprites, npc_name="Sammy", house_point=(0, 0), is_ranged=False, attack_hitbox_list={ "Front": (150, 70),"Back": (150, 70),"Left": (70, 150),"Right": (70, 150) }, range_distance=36, default_size=HDCS + HHDCS, team_members=[], original_speed = 200, actions_to_add=[], initial_position:set=()):

        
        self.talks = {
        "1": {  # Introdução
            "fala": "Pare aí. A vila anda tensa, e eu não deixo qualquer um circular livremente. Sou Obi, guarda da vila. Diga por que está aqui.",
            "respostas": {
                "Só estou de passagem. Não quero problemas.": {"pontuacao": 0.3, "next_id": "2_neutra"},
                "Posso ajudar na patrulha se precisar.": {"pontuacao": 0.6, "next_id": "2_positiva"},
                "Isso é um interrogatório ou você sempre trata assim?": {"pontuacao": -0.5, "next_id": "2_negativa"},
                "Saia da minha frente ou vai se arrepender.": {"pontuacao": -1.0, "next_id": "end_negativo"}
            }
        },
        "2_positiva": {
            "fala": "Ajuda é bem-vinda… desde que siga ordens. Temos relatos de movimentação estranha perto do portão norte.",
            "respostas": {
                "Posso vigiar enquanto você faz a ronda interna.": {"pontuacao": 0.7, "next_id": "end_positivo"},
                "Prefiro investigar sozinho e te reportar depois.": {"pontuacao": 0.4, "next_id": "3_positiva"},
                "Só se tiver alguma recompensa envolvida.": {"pontuacao": -0.3, "next_id": "2_neutra"}
            }
        },
        "2_negativa": {
            "fala": "Atitude suspeita. Não me obrigue a te retirar da vila à força.",
            "respostas": {
                "Calma, só estava testando. Vamos conversar.": {"pontuacao": 0.2, "next_id": "3_neutra"},
                "Tente a sorte.": {"pontuacao": -0.8, "next_id": "end_negativo"},
                "O que está acontecendo exatamente?": {"pontuacao": 0.1, "next_id": "2_neutra"}
            }
        },
        "2_neutra": {
            "fala": "Se ficar, siga as regras. Patrulha reforçada rende 15 moedas por turno.",
            "respostas": {
                "Aceito. Ordem é ordem.": {"pontuacao": 0.4, "next_id": "end_positivo"},
                "Quinze é pouco. Quero 30.": {"pontuacao": -0.2, "next_id": "3_neutra"},
                "Prefiro não me envolver.": {"pontuacao": -0.5, "next_id": "end_negativo"}
            }
        },
        "3_positiva": {
            "fala": "Você se move bem e não chama atenção. Isso é útil pra um guarda.",
            "respostas": {
                "Fico feliz em ajudar a manter a vila segura.": {"pontuacao": 0.4, "next_id": "end_positivo"}
            }
        },
        "3_neutra": {
            "fala": "Não gosto de negociar, mas a vila precisa de braços. Só não cause problemas.",
            "respostas": {
                "Sem confusão. Só trabalho.": {"pontuacao": 0.0, "next_id": "end_neutro"}
            }
        },
        "end_positivo": {
            "fala": "Bom trabalho. Enquanto eu estiver de guarda, você é bem-vindo na vila.",
            "respostas": {}
        },
        "end_negativo": {
            "fala": "Chega. Fora da vila. Agora.",
            "respostas": {}
        },
        "end_neutro": {
            "fala": "Faça seu serviço e siga seu caminho. Nada além disso.",
            "respostas": {}
        }
    }
    
        super().__init__(*groups, collision_sprites=collision_sprites, creatures_sprites=creatures_sprites, npc_name=npc_name, house_point=house_point, is_ranged=is_ranged, attack_hitbox_list=attack_hitbox_list, range_distance=range_distance, default_size=default_size, team_members=team_members, original_speed=original_speed, actions_to_add=actions_to_add)
        self.all_groups= groups
        self.is_player = False
        self.is_human = True


        self.village_rect = pygame.Rect(3800,1400,2200, 2000)
        self.water_sources = [(5528, 2200), (4618, 2836), (4481, 2000) ]
        self.house_point = house_point

        self.armor_type = ""
        self.default_folder_path = join(getcwd(), "NPCs", npc_name,)
        self.scripts = load_scripts(self.default_folder_path)
        self.default_size = default_size
        self.waking_up_hour = randint(4,7)

        self.action = "Walk"
        self.state, self.frame_index = "Front", 0
        self.actions = ["Walk", "Idle", "Hurt", "Run","Attack_1", "Attack_2", "Dying", "Dead", "Run"]
        self.load_character_images()
        
        
        self.image = pygame.transform.scale(self.frames[self.action][self.state][0], (self.default_size, self.default_size))
        
        if initial_position:
            self.rect = self.image.get_frect(center = initial_position)
        else:
            self.rect = self.image.get_frect(center = (5010, 3010))
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
        self.attack_hitbox_list = attack_hitbox_list
        self.last_attack_time = pygame.time.get_ticks()
                
        
        
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


        self.max_hp = 9999
        self.hp = 9999
        self.attack_damage = 9999
        self.attacked_by_character = None

        self.attack_1,self.attack_2 = False,False
        self.specie = "SAMMY"

        self.current_id = "1"
        self.pontuacao = 0.0
        self.confiabilidades["ORC"] = 10
        self.confiabilidades["GOBLIN"] = 10
        self.confiabilidades["HUMAN"] = 10
        self.confiabilidades["SLIME"] = 10
        self.confiabilidades["GOLEM"] = 10
        self.confiabilidades["GHOST"] = 10

        self.can_talk =True







    


    




