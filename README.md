# FacePong — Raspberry Pi 4 Computer Vision Pong

[![CI Pipeline](https://github.com/AndresRuzT/FacePong-Raspberry/actions/workflows/ci.yml/badge.svg)](https://github.com/AndresRuzT/FacePong-Raspberry/actions/workflows/ci.yml)
[![Rust](https://img.shields.io/badge/rust-1.75+-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FacePong es un sistema interactivo multijugador en tiempo real que traslada el clásico juego arcade Pong a una interfaz humano-computador (HCI) basada en visión artificial y estimación de movimiento cefálico.

Diseñado y optimizado específicamente para hardware embebido Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.8GHz, aarch64) para entornos de investigación y demostración académica.

---

## Caracteristicas Principales

- Motor Nativo en Rust: Reimplementado completamente en Rust con Macroquad (aceleracion GLES 2.0 por hardware) y streaming V4L2 zero-copy desde el kernel Linux.
- Control Contactless (Sin Mandos): El desplazamiento vertical de la pala responde al cabeceo e inclinacion facial de cada participante.
- Multijugador en Camara Unica: Particion horizontal automatica con espejo que procesa a ambos jugadores simultaneamente en un unico sensor USB.
- Segmentacion de Color y Centroide Sub-milisegundo: Deteccion crominante de piel en espacio YCbCr optimizada en punto fijo que se ejecuta a mas de 100 FPS en CPUs ARM Cortex-A72.
- Compensacion Biomecanica: Multiplicador diferencial para la inclinacion superior (1.65x) que compensa la restriccion anatomica del cuello humano y el escorzo perspectivo 2D, permitiendo alcanzar los extremos superior e inferior con minimo esfuerzo.
- Filtro EMA Adaptativo: Suavizado exponencial dinamico con incremento de alfa segun velocidad de movimiento para eliminar temblores en reposo y respuesta inmediata en gestos rapidos.
- Diseno Framed Dashboard: Panel superior exterior desacoplado del campo de juego que aloja visualizador en vivo, telemetria y estado de conexion sin obstruir la cancha.
- Modo Fallback / Teclado: Deteccion automatica y soporte de control por teclado para entornos sin camara o depuracion.

---

## Arquitectura del Motor Rust

```text
+----------------------------------------------------------------+
|                   MAIN THREAD (Macroquad GLES)                |
|                    60+ FPS Hardware Rendering                  |
|                                                                |
|  [Input & Keyboard] --> [Game State] --> [Continuous Lerp]     |
|                              |                                 |
|                              v                                 |
|                     [Framed Scene Renderer]                    |
|             (Dashboard Bezel + Unobstructed Court)             |
+------------------------------^---------------------------------+
                               | Zero-latency Crossbeam Channel
+------------------------------+---------------------------------+
|                 VISION WORKER THREAD (Linux V4L2)              |
|                   Sub-millisecond Tracking                     |
|                                                                |
|  1. Captura V4L2 MMAP (/dev/video0) a 320x240 @ 30 FPS         |
|  2. Conversion YUYV -> RGB con espejo horizontal en 1 solo pase|
|  3. Particion Horizontal:                                      |
|       - Subframe Izquierdo -> Jugador 1 (Cyan)                 |
|       - Subframe Derecho   -> Jugador 2 (Amber)                |
|  4. Centroide YCbCr y compensacion biomecanica                 |
|  5. Generacion de preview RGBA anotado con cajas delimitadoras |
+----------------------------------------------------------------+
```

---

## Requisitos de Hardware y Software

### Hardware
- Raspberry Pi 4 Model B (Recomendado 2GB, 4GB o 8GB RAM).
- Disipador activo o ventilador (temperatura estable < 60 C).
- 1 Camara USB (UVC Plug & Play, soporte YUYV / MJPEG).
- Monitor o TV HDMI (1280x720 o 1920x1080).

### Software
- Raspberry Pi OS (Bookworm o Trixie) 64-bit (`aarch64`).
- Rust 1.75+ y Cargo (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`).
- Bibliotecas: `libgl1`, `libegl1`, `libasound2-dev`, `libv4l-dev`, `pkg-config`.

---

## Instalacion y Puesta en Marcha (Rust)

### 1. Clonar el repositorio
```bash
git clone https://github.com/AndresRuzT/FacePong-Raspberry.git
cd FacePong-Raspberry
```

### 2. Ejecutar script automatizado para Raspberry Pi
```bash
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh
```

### 3. Compilacion manual en modo Release
```bash
cargo build --release
```

### 4. Ejecucion del Juego
```bash
./target/release/facepong
```

O directamente mediante cargo:
```bash
cargo run --release
```

---

## Controles

| Accion | Jugador 1 (Izquierda) | Jugador 2 (Derecha) |
|---|---|---|
| Inclinacion Cabeza | Arriba / Abajo | Arriba / Abajo |
| Control Manual Teclado | `W` (Arriba) / `S` (Abajo) | `Flecha Arriba` / `Flecha Abajo` |
| Iniciar / Pausar / Continuar | `Espacio` | `Espacio` |
| Recalibrar Centro Facial | `C` | `C` |
| Reiniciar Partida | `R` | `R` |
| Salir del Juego | `Escape` | `Escape` |

---

## Pruebas Unitarias

Para ejecutar el conjunto de pruebas unitarias del motor:

```bash
cargo test
```

---

## Licencia

Este proyecto esta bajo la Licencia MIT. Consulta el archivo LICENSE para mas detalles.
