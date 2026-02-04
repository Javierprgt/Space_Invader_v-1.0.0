import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import random

ANCHO, ALTO = 800, 600
COLOR_FONDO = (10, 10, 25)
FPS = 60

def obtener_max_puntaje():
    try:
        with open("puntaje.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def guardar_puntaje(nuevo):
    max_actual = obtener_max_puntaje()
    if nuevo > max_actual:
        with open("puntaje.txt", "w") as f:
            f.write(str(nuevo))

class Laser:
    def __init__(self, x, y, velocidad):
        self.rect = pygame.Rect(x, y, 5, 20)
        self.velocidad = velocidad

    def mover(self):
        self.rect.y += self.velocidad

    def dibujar(self, superficie):
        color = (255, 0, 0) if self.velocidad > 0 else (0, 255, 0)
        pygame.draw.rect(superficie, color, self.rect)

class Nave:
    def __init__(self):
        self.imagen_original = pygame.image.load("nave.png").convert_alpha()
        self.imagen = pygame.transform.scale(self.imagen_original, (50, 40))
        self.rect = self.imagen.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.bottom = ALTO - 10
        self.velocidad = 5
        self.lasers = []
        self.cool_down = 0

    def dibujar(self, superficie):
        superficie.blit(self.imagen, self.rect)

    def disparar(self):
        if self.cool_down == 0:
            nuevo_laser = Laser(self.rect.centerx - 2, self.rect.top, -10)
            self.lasers.append(nuevo_laser)
            self.cool_down = 20

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT] and self.rect.right < ANCHO:
            self.rect.x += self.velocidad

class Enemigo:
    def __init__(self, x, y):
        try:
            self.imagen_orig = pygame.image.load("enemigo.png").convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen_orig, (40, 30))
            self.usa_imagen = True
        except:
            self.usa_imagen = False

        self.rect = pygame.Rect(x, y, 40, 30)
        self.color = (random.randint(150, 255), 50, 50)

    def mover(self, vel_y):
        self.rect.y += vel_y

    def dibujar(self, superficie):
        if self.usa_imagen:
            superficie.blit(self.imagen, self.rect)
        else:
            pygame.draw.rect(superficie, self.color, self.rect)

class Boton:
    def __init__(self, texto, x, y, ancho, alto, color):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color

    def dibujar(self, superficie, fuente):
        pygame.draw.rect(superficie, self.color, self.rect, border_radius=10)
        txt = fuente.render(self.texto, True, (255, 255, 255))
        superficie.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def clicado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)

def juego(pantalla, reloj, fuente):
    jugador = Nave()
    enemigos = []
    puntos = 0
    nivel = 1
    corriendo_juego = True

    def spawn(n):
        for i in range(5 + n):
            enemigos.append(Enemigo(random.randint(0, ANCHO-40), random.randint(-600, -50)))

    spawn(nivel)

    while corriendo_juego:
        pantalla.fill(COLOR_FONDO)
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return puntos

        jugador.mover(teclas)
        if teclas[pygame.K_SPACE]: jugador.disparar()
        if jugador.cool_down > 0: jugador.cool_down -= 1

        for e in enemigos[:]:
            e.mover(1 + (nivel * 0.3))
            e.dibujar(pantalla)
            if e.rect.colliderect(jugador.rect) or e.rect.bottom > ALTO:
                corriendo_juego = False
            for l in jugador.lasers[:]:
                if l.rect.colliderect(e.rect):
                    enemigos.remove(e)
                    jugador.lasers.remove(l)
                    puntos += 10
                    break

        if not enemigos:
            nivel += 1
            spawn(nivel)

        for l in jugador.lasers[:]:
            l.mover()
            l.dibujar(pantalla)
            if l.rect.bottom < 0: jugador.lasers.remove(l)

        jugador.dibujar(pantalla)
        ui = fuente.render(f"Puntos: {puntos}  Nivel: {nivel}", True, (255, 255, 255))
        pantalla.blit(ui, (10, 10))
        pygame.display.flip()
        reloj.tick(FPS)
    return puntos

def main():
    pygame.init()
    icono_ventana = pygame.image.load("nave.png")
    pygame.display.set_icon(icono_ventana)

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Videojuego_Space_Invader_ProyectoFinal")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Arial Black", 30)
    
    btn_jugar = Boton("JUGAR", 300, 200, 200, 60, (0, 120, 0))
    btn_puntos = Boton("PUNTAJES", 300, 300, 200, 60, (0, 0, 120))
    btn_salir = Boton("SALIR", 300, 400, 200, 60, (120, 0, 0))

    estado = "MENU"
    ejecutando = True

    while ejecutando:
        pantalla.fill((15, 15, 30))
        m_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if estado == "MENU":
                    if btn_jugar.clicado(m_pos):
                        pts = juego(pantalla, reloj, fuente)
                        guardar_puntaje(pts)
                    if btn_puntos.clicado(m_pos): estado = "PUNTAJES"
                    if btn_salir.clicado(m_pos): ejecutando = False
                elif estado == "PUNTAJES":
                    estado = "MENU"

        if estado == "MENU":
            btn_jugar.dibujar(pantalla, fuente)
            btn_puntos.dibujar(pantalla, fuente)
            btn_salir.dibujar(pantalla, fuente)
        elif estado == "PUNTAJES":
            max_p = obtener_max_puntaje()
            t1 = fuente.render(f"Puntaje Máximo: {max_p}", True, (255, 215, 0))
            t2 = fuente.render("Click para volver", True, (200, 200, 200))
            pantalla.blit(t1, (ANCHO//2 - t1.get_width()//2, 250))
            pantalla.blit(t2, (ANCHO//2 - t2.get_width()//2, 400))

        pygame.display.flip()
        reloj.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
