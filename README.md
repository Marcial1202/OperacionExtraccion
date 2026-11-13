# OPERACIÓN EXTRACCIÓN
Proyecto de Computación Gráfica y Visual: videojuego FPS 3D de supervivencia.

## Descripción
El jugador debe sobrevivir a una ciudad infestada, eliminar 7 zombis, administrar munición y alcanzar el punto de extracción. El proyecto incluye una versión de escritorio (Python/OpenGL) y una versión web (Three.js).

## Versión web (recomendada para demostración)
### Ejecución
1. Abrir PowerShell en la carpeta `web`.
2. Ejecutar:
   ```powershell
   python -m http.server 8000
   ```
3. Abrir `http://localhost:8000/` en Chrome o Edge.
> Requiere conexión a internet para cargar Three.js desde CDN.

### Controles
| Tecla/acción | Función |
|---|---|
| W/A/S/D | Mover |
| Mouse | Mirar/apuntar (captura al iniciar) |
| Clic izquierdo | Disparar |
| 1 / 2 | AK-47 / escopeta |
| R | Recargar |
| E | Recoger munición cerca de una caja |
| Shift | Correr |
| ESC | Pausar / liberar mouse |

### Objetivo y mecánicas
- Eliminar los 7 zombis que persiguen y atacan al jugador.
- Cada zombi requiere 2 impactos; la escopeta tiene daño superior.
- Munición limitada y cajas de abastecimiento.
- HUD con vida, arma, munición, bajas y objetivo.
- Zona de extracción: se activa al eliminar todos los zombis.
- Game Over al quedarse sin vida; victoria al llegar a extracción.

## Versión de escritorio (Python + Pygame + OpenGL)
### Instalación
```bash
python -m pip install -r requirements.txt
python main.py
```
Controles: WASD, mouse, clic izquierdo, 1/2 armas, R recargar, clic derecho recoger munición, ESC salir.

## Estructura
- `main.py`: juego de escritorio.
- `obj_loader.py`: carga de modelos OBJ.
- `assets/models/` y `assets/textures/`: modelos y texturas.
- `web/index.html`, `web/style.css`, `web/game.js`: versión web.
- `web/assets/`: modelos usados por la versión web.

## Requisitos
- Python 3.10+ para versión escritorio y servidor local.
- Navegador moderno con WebGL para versión web.
- Internet para recursos CDN de la versión web.

## Video de sustentación (máximo 3 minutos)
Sugerencia de secuencia: (1) portada y objetivo, (2) iniciar misión y mostrar escenario 3D, (3) movimiento y apuntado, (4) disparar y eliminar zombis, (5) cambiar arma/recargar/recoger munición, (6) mostrar extracción y resultado.
