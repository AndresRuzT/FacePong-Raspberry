# FacePong — Raspberry Pi 4 Computer Vision Pong

[![CI Pipeline](https://github.com/AndresRuzT/FacePong-Raspberry/actions/workflows/ci.yml/badge.svg)](https://github.com/AndresRuzT/FacePong-Raspberry/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

**FacePong** es un sistema interactivo multijugador en tiempo real que traslada el clásico juego arcade Pong a una interfaz humano-computador (HCI) basada en **visión artificial y estimación de pose cefálica**.

Diseñado y optimizado específicamente para hardware embebido **Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.8GHz, aarch64)** para entornos de investigación y demostración académica.

---

## 🎯 Características Principales

- **Control Contactless (Sin Mandos):** El desplazamiento vertical de la pala responde al movimiento de cabeza/mirada de cada participante.
- **Multijugador en Cámara Única:** Algoritmo de partición de cuadro horizontal (*frame splitting*) que procesa simultáneamente a los dos jugadores desde una sola cámara USB de bajo coste.
- **Arquitectura Multinúcleo Concurrente:** La inferencia de visión se desacopla del motor gráfico mediante procesos independientes (`multiprocessing`), garantizando **60 FPS estables** en el bucle de juego sin bloqueos por el Global Interpreter Lock (GIL).
- **Procesamiento de Señal Robusto:** Filtro EMA (*Exponential Moving Average*) y umbral de zona muerta (*deadzone*) para eliminar vibraciones musculares y fluctuaciones de iluminación.
- **Modo Fallback / Calibración:** Compatibilidad nativa con teclado para pruebas sin cámara o depuración en estaciones de desarrollo.
- **Estándar de Calidad:** Código 100% tipado estáticamente, verificado con `mypy` y formateado con `ruff`.

---

## 🏗️ Arquitectura del Sistema

```text
┌────────────────────────────────────────────────────────────────┐
│                   MAIN PROCESS (Cores 0-1)                     │
│               Pygame-CE Loop @ 60 FPS Constantes               │
│                                                                │
│  [Event Handler] ──> [Game State] ──> [Ball Physics / Col]     │
│                             │                                  │
│                             ▼                                  │
│                    [Input Manager Layer]                       │
│                    (P1 Adapter / P2 Adapter)                   │
└──────────────────────────────▲─────────────────────────────────┘
                               │ Non-blocking IPC Queue (Freshest frame)
┌──────────────────────────────┴─────────────────────────────────┐
│                    CV WORKER PROCESS (Cores 2-3)               │
│               OpenCV + MediaPipe Face Mesh (Lite)              │
│                                                                │
│  1. Captura USB (320x240 @ 20 FPS)                             │
│  2. Partición Horizontal:                                      │
│       • Subframe Izquierdo ──> Jugador 1 (Landmarks 4, 10, 152)│
│       • Subframe Derecho   ──> Jugador 2 (Landmarks 4, 10, 152)│
│  3. Extracción de ratios normalizados de cabeceo vertical       │
│  4. Publicación no-bloqueante a Queue                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 📐 Métricas de Estimación Cefálica

Para minimizar la latencia y evitar la sobrecarga de resolver `solvePnP` completo en ARM Cortex-A72, se utiliza el ratio geométrico vertical entre puntos clave de la malla facial:

$$\text{face\_height} = y_{\text{chin}} - y_{\text{forehead}}$$
$$\text{pitch\_ratio} = \frac{y_{\text{nose}} - y_{\text{forehead}}}{\text{face\_height}}$$

- **Puntos de referencia (MediaPipe Face Mesh):**
  - Frente (nasión superior): `Landmark 10`
  - Punta de la nariz: `Landmark 4`
  - Mentón (borde inferior): `Landmark 152`
- Valor neutral en reposo: $\approx 0.45$.
- Desviación superior ($< 0.40$): Desplaza la paleta hacia arriba.
- Desviación inferior ($> 0.50$): Desplaza la paleta hacia abajo.

---

## ⚙️ Requisitos de Hardware y Software

### Hardware
- **Raspberry Pi 4 Model B** (Recomendado 4GB o 8GB RAM).
- Disipador activo o ventilador (para mantener temperatura < 65°C en inferencia sostenida).
- 1× Cámara USB (Plug & Play UVC, resolución nativa 720p o 1080p).
- Monitor o TV HDMI (1080p o 720p).

### Software
- **Raspberry Pi OS (Bookworm) 64-bit** (`aarch64`).
- **Python 3.11+** (incluido por defecto en Bookworm).

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/AndresRuzT/FacePong-Raspberry.git
cd FacePong-Raspberry
```

### 2. Configurar el entorno virtual
En Raspberry Pi OS Bookworm los entornos virtuales son mandatorios según PEP 668:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 3. Instalar dependencias
```bash
# Dependencias de ejecución:
pip install -r requirements.txt

# Para desarrollo y pruebas:
pip install -r requirements-dev.txt
```

*(Opcional) Instalación del paquete en modo editable:*
```bash
pip install -e .
```

### 4. Ejecución del Juego
```bash
# Ejecutar directamente:
python3 -m facepong.main

# O con archivo de configuración personalizado:
python3 -m facepong.main --config config/default.toml
```

---

## ⌨️ Controles de Teclado (Modo Fallback / Pruebas)

| Acción | Jugador 1 (Izquierda) | Jugador 2 (Derecha) |
|---|---|---|
| Subir Paleta | `W` | `Flecha Arriba` |
| Bajar Paleta | `S` | `Flecha Abajo` |
| Pausar / Continuar | `Espacio` | `Espacio` |
| Reiniciar Partida | `R` | `R` |
| Alternar Overlay Cámara | `C` | `C` |
| Salir del Juego | `Escape` | `Escape` |

---

## 🧪 Pruebas Unitarias y Calidad de Código

El repositorio cuenta con suite automatizada de pruebas y comprobación estática:

```bash
# Ejecutar pruebas con reporte de cobertura:
pytest

# Comprobar formato y convenciones (Ruff):
ruff check .
ruff format --check .

# Verificación de tipos estáticos (Mypy):
mypy src/
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
