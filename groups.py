from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self,):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.world_w, self.world_h = (0,0)
        self.world_matriz = None
        self.matriz_pura = None

        # === Visão limitada / fog ===
        self.blind_enabled = True           # usa getattr(player, "is_blind", False) no draw
        self.ambient = 20                   # 0 = escuridão total | 255 = sem escurecer
        self.blind_radius = 70             # raio claro em px
        self.blind_feather = 50           # suavização (borda) do “cone” de visão
        self._light_grad = None             # gradiente pré-gerado
        self._light_grad_size = (0, 0)
        self._lightmap = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

        self.frame_index = 0
    def att_world_size(self,w,h):
        self.world_w = w
        self.world_h = h

    def _camera_topleft(self, target_pos):
        cam_x = target_pos[0] - WINDOW_WIDTH  / 2
        cam_y = target_pos[1] - WINDOW_HEIGHT / 2
        max_cam_x = max(0, self.world_w  - WINDOW_WIDTH)
        max_cam_y = max(0, self.world_h - WINDOW_HEIGHT)
        cam_x = max(0, min(cam_x, max_cam_x))
        cam_y = max(0, min(cam_y, max_cam_y))
        return pygame.Vector2(cam_x, cam_y)

    # ---------- FOG/LIGHT HELPERS ----------
    def _ensure_light_grad_alpha(self):
        """Gradiente radial só no canal alpha (centro opaco=255 -> borda 0)."""
        size = 2 * (self.blind_radius + self.blind_feather)
        if getattr(self, "_light_grad_alpha", None) is not None and self._light_grad_size == (size, size):
            return

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        outer = self.blind_radius + self.blind_feather

        # De fora p/ dentro: alpha cresce até 255 no núcleo (que "abre" o buraco na camada escura)
        for r in range(outer, self.blind_radius - 1, -1):
            t = (r - self.blind_radius) / max(1, self.blind_feather)  # 0..1
            a = int(255 * (1.0 - t))
            pygame.draw.circle(surf, (0, 0, 0, a), (cx, cy), r)

        pygame.draw.circle(surf, (0, 0, 0, 255), (cx, cy), self.blind_radius)

        self._light_grad_alpha = surf
        self._light_grad_size = (size, size)
        if not hasattr(self, "_fog_overlay") or self._fog_overlay.get_size() != (WINDOW_WIDTH, WINDOW_HEIGHT):
            self._fog_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    def _apply_light_fast(self, center_on_screen):
        """Fog rápido: camada preta com alpha = (255 - ambient) e 'furo' radial no player."""
        self._ensure_light_grad_alpha()

        darkness = 255 - self.ambient  # quanto escurecer (0 = nada, 255 = preto total)
        self._fog_overlay.fill((0, 0, 0, darkness))

        grad_rect = self._light_grad_alpha.get_rect(center=(int(center_on_screen[0]), int(center_on_screen[1])))
        # Subtrai alpha do gradiente => abre um "buraco" suave no escuro
        self._fog_overlay.blit(self._light_grad_alpha, grad_rect, special_flags=pygame.BLEND_RGBA_SUB)

        # Um único blit com alpha (bem mais leve que multiplicar a tela inteira)
        self.display_surface.blit(self._fog_overlay, (0, 0))

    def _get_player_cached(self):
        p = getattr(self, "_player", None)
        if p is not None:
            return p
        # primeira vez: encontra e cacheia
        for s in self.sprites():
            if getattr(s, "is_player", False):
                self._player = s
                return s
        return None

    def draw(self, target_pos):
        # --- câmera / offsets inteiros (evita custo de floats a cada soma) ---
        cam = self._camera_topleft(target_pos)
        off_x = -int(cam.x)
        off_y = -int(cam.y)

        player = self._get_player_cached()
        if player is None:
            return

        shake = player.sample_shake_offset()
        sx, sy = int(shake.x), int(shake.y)
        dx = off_x + sx
        dy = off_y + sy

        self.offset.x = dx
        self.offset.y = dy

        # --- viewport (em coords de mundo) com pequena margem p/ evitar pop-in ---
        pad = 8
        vx0 = int(cam.x) - pad; vy0 = int(cam.y) - pad
        vx1 = vx0 + WINDOW_WIDTH + 2 * pad
        vy1 = vy0 + WINDOW_HEIGHT + 2 * pad

        ds = self.display_surface
        blits = ds.blits  # bind local p/ reduzir lookups

        grounds_seq =       []
        magic_circle_seqs = []
        obj_visible =       []
        obj_details =       []
        characters  =       []
        winter_curses  =    []
        # --- 1 única passada: classifica + culling; nada de 2 list comps + sort global ---
        for sp in self.sprites():
            r = sp.rect  # assuma r é FRect/Rect; acessos diretos e inteiros
            if r.right < vx0 or r.left > vx1 or r.bottom < vy0 or r.top > vy1:
                continue  # fora da tela
            if getattr(sp, "is_invisible", False):
                continue

            elif getattr(sp, "is_ground", False):
                grounds_seq.append((sp.image, (int(r.x) + dx, int(r.y) + dy)))
            elif getattr(sp, "is_magic_circle", False):
                magic_circle_seqs.append((sp.image, (int(r.x) + dx, int(r.y) + dy)))
            elif getattr(sp, "is_detail", False):
                obj_details.append((sp.image, (int(r.x) + dx, int(r.y) + dy)))
            elif getattr(sp, "is_winter_curse", False):
                winter_curses.append((sp.image, (int(r.x) + dx, int(r.y) + dy)))
            
            else:
                
                obj_visible.append(sp)

        # --- chão: 1 chamada em lote ---
        if grounds_seq:
            blits(grounds_seq, False)
            
        # --- círculos mágicos: 2 chamada em lote ---
        if magic_circle_seqs:
            blits(magic_circle_seqs, False)

        # --- objetos visíveis: sort só do subconjunto reduzido ---
        if obj_visible:
            obj_visible.sort(key=lambda s: s.rect.centery)
            obj_seq = [(s.image, (int(s.rect.x) + dx, int(s.rect.y) + dy)) for s in obj_visible]
            blits(obj_seq, False)
        
        if obj_details:
            blits(obj_details, False)

            
        if winter_curses:
            blits(winter_curses, False)

        # --- fog leve (alpha) apenas quando precisar ---
        if getattr(player, "is_blind", False) and self.blind_enabled:
            pcx = int(player.rect.centerx) + dx
            pcy = int(player.rect.centery) + dy
            self._apply_light_fast((pcx, pcy))


        