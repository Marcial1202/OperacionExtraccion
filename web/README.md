# OPERACIÓN EXTRACCIÓN — versión web

## Ejecutar
Desde la carpeta `web`, iniciar un servidor HTTP (por ejemplo):
```powershell
python -m http.server 8000
```
Abrir `http://localhost:8000/`. Se requiere conexión a internet para descargar Three.js y los modelos GLTF desde CDN/archivos del proyecto.

## Controles
- **W A S D:** moverse (W hacia delante, S atrás, A/D lateral).
- **Mouse:** mirar y apuntar (clic en Iniciar misión para activar captura del mouse).
- **Clic izquierdo:** disparar al objetivo del centro de la mira.
- **1 / 2:** AK-47 / escopeta.
- **R:** recargar usando munición de reserva.
- **E:** recoger cajas de munición al acercarse.
- **Shift:** correr.
- **Esc:** pausar y liberar el mouse; Continuar vuelve al juego.

## Objetivo
Eliminar los 7 zombis (se acercan y atacan al jugador), conservar vida y munición, y entrar en el círculo verde de extracción cuando el contador llegue a 7/7. Si la vida llega a cero, se pierde.
