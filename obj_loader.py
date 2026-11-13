import os
import pygame
from OpenGL.GL import *

_CACHE = {}
_TEXTURES = {}

def cargar_textura(ruta):
    ruta = os.path.abspath(ruta)
    if ruta in _TEXTURES:
        return _TEXTURES[ruta]
    img = pygame.image.load(ruta).convert_alpha()
    img = pygame.transform.flip(img, False, True)
    w, h = img.get_size()
    data = pygame.image.tostring(img, "RGBA", True)
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glBindTexture(GL_TEXTURE_2D, 0)
    _TEXTURES[ruta] = tex
    return tex

def cargar_obj(ruta, textura=None):
    ruta = os.path.abspath(ruta)
    key = (ruta, os.path.abspath(textura) if textura else None)
    if key in _CACHE:
        return _CACHE[key]
    vertices, uvs, caras = [], [], []
    with open(ruta, encoding="utf-8", errors="ignore") as f:
        for linea in f:
            p = linea.strip().split()
            if not p: continue
            if p[0] == "v" and len(p) >= 4:
                vertices.append(tuple(map(float, p[1:4])))
            elif p[0] == "vt" and len(p) >= 3:
                uvs.append(tuple(map(float, p[1:3])))
            elif p[0] == "f" and len(p) >= 4:
                refs=[]
                for item in p[1:]:
                    q=item.split("/")
                    vi=int(q[0]); vi=vi-1 if vi>0 else len(vertices)+vi
                    ti=int(q[1]) if len(q)>1 and q[1] else 0
                    ti=ti-1 if ti>0 else (len(uvs)+ti if ti<0 else -1)
                    refs.append((vi,ti))
                for i in range(1,len(refs)-1):
                    caras.append((refs[0],refs[i],refs[i+1]))
    if not vertices or not caras: raise ValueError("OBJ sin geometría: "+ruta)
    mins=[min(v[k] for v in vertices) for k in range(3)]
    maxs=[max(v[k] for v in vertices) for k in range(3)]
    escala=2.0/max(maxs[1]-mins[1],0.001)
    centro=[(mins[k]+maxs[k])/2 for k in range(3)]
    tex=cargar_textura(textura) if textura and os.path.exists(textura) and uvs else 0
    lista=glGenLists(1); glNewList(lista,GL_COMPILE)
    if tex: glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D,tex); glColor3f(1,1,1)
    glBegin(GL_TRIANGLES)
    for cara in caras:
        a,b,c=[vertices[r[0]] for r in cara]
        ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
        vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
        nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
        n=(nx*nx+ny*ny+nz*nz)**0.5 or 1
        glNormal3f(nx/n,ny/n,nz/n)
        for vi,ti in cara:
            if tex and ti>=0 and ti<len(uvs): glTexCoord2f(*uvs[ti])
            v=vertices[vi]
            glVertex3f((v[0]-centro[0])*escala,(v[1]-mins[1])*escala,(v[2]-centro[2])*escala)
    glEnd()
    if tex: glBindTexture(GL_TEXTURE_2D,0); glDisable(GL_TEXTURE_2D)
    glEndList(); _CACHE[key]=lista
    return lista

def dibujar_obj(lista,x,y,z,escala=1.0,color=(0.55,0.62,0.48),rotacion=0):
    glPushMatrix(); glTranslatef(x,y,z); glRotatef(rotacion,0,1,0); glScalef(escala,escala,escala)
    glColor3f(*color); glCallList(lista); glPopMatrix()
