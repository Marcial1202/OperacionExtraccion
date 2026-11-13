import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from obj_loader import cargar_obj, dibujar_obj
import os

RUTA_MODELOS = os.path.join('assets', 'models')
RUTA_ZOMBI = os.path.join(RUTA_MODELOS, 'Zombie_Basic.obj')
RUTA_ATLAS = os.path.join(RUTA_MODELOS, 'Zombie_Atlas.png')
MODELO_ZOMBI = MODELO_BARRIL = MODELO_CONTENEDOR = None
try:
    if os.path.exists(RUTA_ZOMBI): MODELO_ZOMBI = cargar_obj(RUTA_ZOMBI, RUTA_ATLAS)
    if os.path.exists(os.path.join(RUTA_MODELOS,'Barrel.obj')): MODELO_BARRIL = cargar_obj(os.path.join(RUTA_MODELOS,'Barrel.obj'))
    if os.path.exists(os.path.join(RUTA_MODELOS,'Container_Green.obj')): MODELO_CONTENEDOR = cargar_obj(os.path.join(RUTA_MODELOS,'Container_Green.obj'))
except Exception as e: print('Aviso al cargar modelos:', e)

ANCHO, ALTO = 1100, 700
VELOCIDAD = 5.0
SENSIBILIDAD = 0.12

jugador = [0.0, 1.7, 8.0]
yaw, pitch = 0.0, 0.0
vida = 100
balas = [30, 12]  # munición en cargador
reserva = [90, 36]
CARGADOR_MAX = [30, 12]
arma = 1
zombis = [[random.uniform(-12, 12), 0.0, random.uniform(-22, -10), 100] for _ in range(7)]
cajas = [[-7, 0, -8], [8, 0, -15]]
ultimo_disparo = False
mensaje = "Sobrevive y llega a la zona verde de extracción"
estado = "jugando"  # jugando, victoria o gameover
zombis_eliminados = 0
obstaculos = [(-8,-5),(7,-10),(-4,-16),(12,2),(0,-22)]
ultimo_ataque = 0.0

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
    global yaw, pitch, vida, arma, balas, zombis, jugador, mensaje, estado, zombis_eliminados, ultimo_ataque
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
                if evento.key == K_r: recargar()
            if evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                disparar()
            if evento.type == MOUSEBUTTONDOWN and evento.button == 3:
                recoger()

        if estado != "jugando":
            pygame.mouse.get_rel()
            dibujar()
            pygame.display.flip()
            continue
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
            nx = jugador[0] + vx/largo*VELOCIDAD*dt
            nz = jugador[2] + vz/largo*VELOCIDAD*dt
            if not colisiona(nx, jugador[2]): jugador[0] = nx
            if not colisiona(jugador[0], nz): jugador[2] = nz
        jugador[0] = max(-21, min(21, jugador[0]))
        jugador[2] = max(-29, min(19, jugador[2]))
        if jugador[0] > 14 and jugador[2] < -20 and all(z[3] <= 0 for z in zombis):
            estado = "victoria"; mensaje = "EXTRACCION COMPLETADA"

        actualizar_zombis(dt)
        dibujar()
        pygame.display.flip()

    pygame.quit()

def disparar():
    global mensaje, zombis_eliminados
    if estado != "jugando": return
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
        if objetivo[3] <= 0: zombis_eliminados += 1
        mensaje = "Impacto! Zombi eliminado" if objetivo[3] <= 0 else "Zombi herido"
    else:
        mensaje = "Disparo..."
        
def recargar():
    global mensaje
    faltan = CARGADOR_MAX[arma] - balas[arma]
    transferir = min(faltan, reserva[arma])
    if transferir <= 0:
        mensaje = "Cargador lleno o sin reserva"; return
    balas[arma] += transferir
    reserva[arma] -= transferir
    mensaje = "Recarga completada"

def recoger():
    global mensaje
    if estado != "jugando": return
    for caja in cajas[:]:
        if distancia(jugador, caja) < 2.2:
            reserva[0] += 30
            reserva[1] += 12
            cajas.remove(caja)
            mensaje = "Municion recogida"
            return
    mensaje = "Acercate a una caja y pulsa clic derecho"

def actualizar_zombis(dt):
    global vida, mensaje, estado, ultimo_ataque
    for z in zombis:
        if z[3] <= 0: continue
        d = distancia(jugador, z)
        if d > 2.5:
            z[0] += (jugador[0]-z[0])/max(d,0.01)*1.25*dt
            z[2] += (jugador[2]-z[2])/max(d,0.01)*1.25*dt
        else:
            ahora = pygame.time.get_ticks()/1000
            if ahora-ultimo_ataque >= 1.0:
                vida = max(0, vida-8); ultimo_ataque = ahora
                mensaje = "Te estan atacando!"
    if vida <= 0:
        estado = "gameover"; mensaje = "GAME OVER"

def colisiona(x, z):
    # Colision simple jugador-obstaculos (radio de seguridad)
    for ox, oz in obstaculos:
        if abs(x-ox) < 2.0 and abs(z-oz) < 2.0: return True
    return False

def esfera(x, y, z, radio, color, slices=12, stacks=8):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x, y, z)
    quad = gluNewQuadric()
    gluSphere(quad, radio, slices, stacks)
    gluDeleteQuadric(quad)
    glPopMatrix()

def cilindro(x1, y1, z1, x2, y2, z2, radio, color):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(x1, y1, z1)
    vx, vy, vz = x2-x1, y2-y1, z2-z1
    largo = math.sqrt(vx*vx + vy*vy + vz*vz)
    if largo > 0:
        glRotatef(math.degrees(math.acos(vy/largo)), vz, 0, -vx)
        quad = gluNewQuadric()
        gluCylinder(quad, radio, radio*0.85, largo, 8, 2)
        gluDeleteQuadric(quad)
    glPopMatrix()

def dibujar_zombi(z):
    x, _, zz, vida_z = z
    if MODELO_ZOMBI is not None:
        dibujar_obj(MODELO_ZOMBI, x, 0.0, zz, escala=0.85, color=(0.48,0.62,0.38), rotacion=180)
        glDisable(GL_DEPTH_TEST)
        cubo(x, 2.35, zz, 0.35, 0.035, 0.025, (0.45,0.05,0.05))
        cubo(x-0.35+(vida_z/100)*0.35, 2.35, zz-0.03, (vida_z/100)*0.35, 0.04, 0.03, (0.1,0.85,0.15))
        glEnable(GL_DEPTH_TEST)
        return
    piel = (0.28, 0.62, 0.25)
    ropa = (0.20, 0.24, 0.18)
    pantalon = (0.12, 0.16, 0.13)
    cubo(x, 1.15, zz, 0.38, 0.55, 0.22, ropa)
    esfera(x, 1.92, zz, 0.28, piel)
    esfera(x-0.10, 1.98, zz-0.22, 0.055, (0.9, 0.08, 0.05), 8, 6)
    esfera(x+0.10, 1.98, zz-0.22, 0.055, (0.9, 0.08, 0.05), 8, 6)
    cilindro(x-0.42, 1.52, zz, x-0.62, 0.85, zz-0.05, 0.13, piel)
    cilindro(x+0.42, 1.52, zz, x+0.62, 0.85, zz+0.08, 0.13, piel)
    cilindro(x-0.18, 0.65, zz, x-0.22, 0.12, zz, 0.15, pantalon)
    cilindro(x+0.18, 0.65, zz, x+0.22, 0.12, zz, 0.15, pantalon)
    cubo(x-0.22, 0.08, zz-0.08, 0.20, 0.08, 0.30, (0.08,0.08,0.07))
    cubo(x+0.22, 0.08, zz-0.08, 0.20, 0.08, 0.30, (0.08,0.08,0.07))
    glDisable(GL_DEPTH_TEST)
    cubo(x, 2.35, zz, 0.35, 0.035, 0.025, (0.45,0.05,0.05))
    cubo(x-0.35+(vida_z/100)*0.35, 2.35, zz-0.03, (vida_z/100)*0.35, 0.04, 0.03, (0.1,0.85,0.15))
    glEnable(GL_DEPTH_TEST)

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
    # Obstaculos y modelos OBJ del pack descargado
    for x,z in obstaculos:
        cubo(x,1,z,1.5,1,1.5,(0.35,0.28,0.18))
    if MODELO_BARRIL is not None:
        for x,z in [(-10,-12),(10,-18),(-14,3)]: dibujar_obj(MODELO_BARRIL,x,0,z,escala=0.7,color=(1,1,1))
    if MODELO_CONTENEDOR is not None:
        dibujar_obj(MODELO_CONTENEDOR,-15,0,-20,escala=2.0,color=(1,1,1),rotacion=90)
    # Extraccion
    cubo(17,0.03,-23,3,0.03,3,(0.1,0.8,0.25))
    # Cajas de municion
    for x,y,z in cajas:
        cubo(x,0.45,z,0.45,0.45,0.45,(0.9,0.65,0.1))
    # Zombis
    for z in zombis:
        if z[3] <= 0: continue
        dibujar_zombi(z)
    # Arma en pantalla, en la esquina inferior derecha
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, ANCHO, 0, ALTO, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)

    # Cuerpo del rifle
    glColor3f(0.12, 0.13, 0.15)
    glBegin(GL_QUADS)
    glVertex2f(ANCHO-300, 80)
    glVertex2f(ANCHO-90, 125)
    glVertex2f(ANCHO-65, 205)
    glVertex2f(ANCHO-260, 170)
    glEnd()

    # Cañon y punta
    glColor3f(0.22, 0.23, 0.25)
    glBegin(GL_QUADS)
    glVertex2f(ANCHO-145, 165)
    glVertex2f(ANCHO-45, 185)
    glVertex2f(ANCHO-45, 205)
    glVertex2f(ANCHO-145, 190)
    glEnd()
    glColor3f(0.04, 0.04, 0.05)
    glBegin(GL_QUADS)
    glVertex2f(ANCHO-55, 182)
    glVertex2f(ANCHO-25, 188)
    glVertex2f(ANCHO-25, 205)
    glVertex2f(ANCHO-55, 199)
    glEnd()

    # Empuñadura
    glColor3f(0.08, 0.09, 0.10)
    glBegin(GL_QUADS)
    glVertex2f(ANCHO-205, 75)
    glVertex2f(ANCHO-145, 65)
    glVertex2f(ANCHO-125, 145)
    glVertex2f(ANCHO-180, 155)
    glEnd()

    # Mira del rifle
    glColor3f(0.35, 0.36, 0.38)
    glBegin(GL_QUADS)
    glVertex2f(ANCHO-220, 175)
    glVertex2f(ANCHO-150, 185)
    glVertex2f(ANCHO-150, 205)
    glVertex2f(ANCHO-220, 195)
    glEnd()

    glDepthMask(GL_TRUE)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Mira en el centro de la pantalla
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, ANCHO, ALTO, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.5)
    cx, cy = ANCHO/2, ALTO/2
    glBegin(GL_LINES)
    glVertex2f(cx-12,cy); glVertex2f(cx-4,cy)
    glVertex2f(cx+4,cy); glVertex2f(cx+12,cy)
    glVertex2f(cx,cy-12); glVertex2f(cx,cy-4)
    glVertex2f(cx,cy+4); glVertex2f(cx,cy+12)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    texto(20,18,f"VIDA: {int(vida)}", (255,80,80))
    texto(20,50,f"ARMA {arma+1} | CARGADOR: {balas[arma]}/{CARGADOR_MAX[arma]} | RESERVA: {reserva[arma]}",(255,230,100))
    texto(20,82,mensaje,(220,220,220),18)
    texto(20,ALTO-65,f"ZOMBIS: {zombis_eliminados}/{len(zombis)} | Municion: cajas restantes {len(cajas)}",(180,190,200),16)
    texto(20,ALTO-38,"WASD mover | Mouse mirar | Click disparar | 1/2 arma | R recargar | Click derecho recoger | ESC salir",(180,190,200),16)
    if estado in ("victoria","gameover"):
        glColor3f(0.0,0.0,0.0)
        texto(ANCHO//2-170,ALTO//2-25,mensaje,(80,255,100) if estado=="victoria" else (255,70,70),36)
        texto(ANCHO//2-130,ALTO//2+25,"Presiona ESC para cerrar",(255,255,255),20)

if __name__ == "__main__":
    iniciar()
