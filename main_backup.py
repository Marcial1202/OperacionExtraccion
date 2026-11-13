import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

ANCHO, ALTO = 1100, 700
VELOCIDAD = 5.0
SENSIBILIDAD = 0.12

jugador = [0.0, 1.7, 8.0]
yaw, pitch = 0.0, 0.0
vida = 100
balas = [30, 12]
arma = 1
zombis = [[random.uniform(-12, 12), 0.0, random.uniform(-22, -10), 100] for _ in range(7)]
cajas = [[-7, 0, -8], [8, 0, -15]]
ultimo_disparo = False
mensaje = "Sobrevive y llega a la zona verde de extracción"

def cubo(x, y, z, sx, sy, sz, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glBegin(GL_QUADS)
    caras = [
        ((0,0,1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)),
        ((0,0,-1),(1,-1,-1),(-1,-1,-1),(-1,1,-1),(1,1,-1)),
        ((1,0,0),(1,-1,1),(1,-1,-1),(1,1,-1),(1,1,1)),
        ((-1,0,0),(-1,-1,-1),(-1,-1,1),(-1,1,1),(-1,1,-1)),
        ((0,1,0),(-1,1,1),(1,1,1),(1,1,-1),(-1,1,-1)),
        ((0,-1,0),(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1))
    ]
    for normal, *vertices in caras:
        glNormal3f(*normal)
        for v in vertices:
            glVertex3f(*v)
    glEnd()
    glPopMatrix()

def texto(x, y, contenido, color=(255,255,255), tam=24):
    fuente = pygame.font.SysFont("consolas", tam, bold=True)
    superficie = fuente.render(contenido, True, color)
    pantalla = pygame.display.get_surface()
    pantalla.blit(superficie, (x,y))

def distancia(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[2]-b[2])**2)

def iniciar():
    global yaw, pitch, vida, arma, balas, zombis, jugador, mensaje
    pygame.init()
    pygame.display.set_caption("Operacion Extraccion - FPS")
    pygame.display.set_mode((ANCHO, ALTO), DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    glViewport(0, 0, ANCHO, ALTO)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, ANCHO/ALTO, 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.04, 0.05, 0.08, 1)
    reloj = pygame.time.Clock()
    pygame.mouse.get_rel()

    corriendo = True
    while corriendo:
        dt = min(reloj.tick(60)/1000, 0.05)
        for evento in pygame.event.get():
            if evento.type == QUIT:
                corriendo = False
            if evento.type == KEYDOWN:
                if evento.key == K_ESCAPE:
                    corriendo = False
                if evento.key == K_1: arma = 0
                if evento.key == K_2: arma = 1
            if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                disparar()
            if evento.type == MOUSEBUTTONDOWN and evento.button == 3:
                recoger()

        mx, my = pygame.mouse.get_rel()
        yaw += mx * SENSIBILIDAD
        pitch = max(-85, min(85, pitch - my*SENSIBILIDAD))
        teclas = pygame.key.get_pressed()
        adelante = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
        derecha = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
        vx = (adelante[0]*(teclas[K_w]-teclas[K_s]) + derecha[0]*(teclas[K_d]-teclas[K_a]))
        vz = (adelante[1]*(teclas[K_w]-teclas[K_s]) + derecha[1]*(teclas[K_d]-teclas[K_a]))
        largo = math.hypot(vx, vz)
        if largo:
            jugador[0] += vx/largo*VELOCIDAD*dt
            jugador[2] += vz/largo*VELOCIDAD*dt
        jugador[0] = max(-22, min(22, jugador[0]))
        jugador[2] = max(-25, min(15, jugador[2]))

        actualizar_zombis(dt)
        dibujar()
        pygame.display.flip()

    pygame.quit()

def disparar():
    global mensaje
    if balas[arma] <= 0:
        mensaje = "Sin balas: busca una caja de municion"
        return
    balas[arma] -= 1
    direccion = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
    objetivo = None
    mejor = 999
    for z in zombis:
        if z[3] <= 0: continue
        dx, dz = z[0]-jugador[0], z[2]-jugador[2]
        d = math.hypot(dx,dz)
        if d > 18: continue
        ang = math.degrees(math.acos(max(-1,min(1,(dx*direccion[0]+dz*direccion[1])/max(d,0.001)))))
        if ang < (8 if arma == 0 else 5) and d < mejor:
            mejor, objetivo = d, z
    if objetivo:
        objetivo[3] -= 50 if arma == 0 else 35
        mensaje = "Impacto! Zombi eliminado" if objetivo[3] <= 0 else "Zombi herido"
    else:
        mensaje = "Disparo..."
        
def recoger():
    global mensaje
    for caja in cajas[:]:
        if distancia(jugador, caja) < 2.2:
            balas[0] += 15
            balas[1] += 6
            cajas.remove(caja)
            mensaje = "Municion recogida"
            return
    mensaje = "Acercate a una caja y pulsa clic derecho"

def actualizar_zombis(dt):
    global vida, mensaje
    for z in zombis:
        if z[3] <= 0: continue
        d = distancia(jugador, z)
        if d > 2.5:
            z[0] += (jugador[0]-z[0])/max(d,0.01)*1.25*dt
            z[2] += (jugador[2]-z[2])/max(d,0.01)*1.25*dt
        else:
            vida = max(0, vida-12*dt)
            mensaje = "Te estan atacando!"
    if vida <= 0:
        mensaje = "GAME OVER - ESC para salir"

def dibujar():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    dx = math.sin(math.radians(yaw))*math.cos(math.radians(pitch))
    dy = math.sin(math.radians(pitch))
    dz = -math.cos(math.radians(yaw))*math.cos(math.radians(pitch))
    gluLookAt(jugador[0], jugador[1], jugador[2],
              jugador[0]+dx, jugador[1]+dy, jugador[2]+dz, 0,1,0)

    # Piso y paredes del mapa
    cubo(0,-0.15,-5,24,0.15,25,(0.18,0.20,0.22))
    for x in [-22,22]:
        cubo(x,2,-5,0.3,2,25,(0.12,0.14,0.17))
    for z in [-30,20]:
        cubo(0,2,z,22,2,0.3,(0.12,0.14,0.17))
    # Obstaculos
    for x,z in [(-8,-5),(7,-10),(-4,-16),(12,2),(0,-22)]:
        cubo(x,1,z,1.5,1,1.5,(0.35,0.28,0.18))
    # Extraccion
    cubo(17,0.03,-23,3,0.03,3,(0.1,0.8,0.25))
    # Cajas de municion
    for x,y,z in cajas:
        cubo(x,0.45,z,0.45,0.45,0.45,(0.9,0.65,0.1))
    # Zombis
    for z in zombis:
        if z[3] <= 0: continue
        cubo(z[0],0.9,z[2],0.45,0.9,0.3,(0.2,0.55,0.2))
        cubo(z[0],1.9,z[2],0.35,0.35,0.35,(0.45,0.75,0.35))
    # Arma sencilla en primera persona
    cubo(jugador[0]+dx*0.5+0.35, jugador[1]-0.35, jugador[2]+dz*0.5,
         0.18,0.18,0.55,(0.15,0.15,0.18))
    glDisable(GL_DEPTH_TEST)
    pygame.display.get_surface().fill((0,0,0), pygame.Rect(0,0,0,0))
    texto(20,18,f"VIDA: {int(vida)}", (255,80,80))
    texto(20,50,f"ARMA {arma+1} | BALAS: {balas[arma]}",(255,230,100))
    texto(20,82,mensaje,(220,220,220),18)
    texto(ANCHO//2-8,ALTO//2-12,"+",(255,255,255),26)
    texto(20,ALTO-38,"WASD mover | Mouse mirar | Click disparar | 1/2 arma | Click derecho recoger | ESC salir",(180,190,200),16)
    glEnable(GL_DEPTH_TEST)

if __name__ == "__main__":
    iniciar()
