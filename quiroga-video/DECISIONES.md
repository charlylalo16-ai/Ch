# Quiroga Digital: video promocional (40 s)

Entregables (no se suben al repo público):
- `out/quiroga_digital_9x16.mp4`, vertical 1080×1920.
- `out/quiroga_digital_16x9.mp4`, horizontal 1920×1080.

Los dos van a 60 fps y llevan música original.

## La idea (lo que pidió el cliente)

Un teléfono con la app ya instalada. Se abre, se hace el registro, se entra, se recorren las funciones (con más detalle en Alerta Mujer) y al final viene el cierre con el estilo del Ayuntamiento y sus colores.

## Decisión clave: pantallas reales, no recreadas

Todas las pantallas dentro del teléfono son **capturas de la app real** (`charlylalo16-ai/quiroga-app`, `index.html`), no dibujos que la imitan:

- `lab/shoot.js` abre la app en un Chromium sin interfaz, como un teléfono de 412×892 px a 3×.
- **Firebase va simulado** (`lab/stub-firebase.js`). La app no se conecta a ningún servidor ni toca datos reales; las colecciones devuelven **datos de demostración ficticios**: "María López", teléfono 443 123 4567, folios de ejemplo.
- `lab/record.js` recorre la app llamando a sus propias funciones (`switchAuthTab`, `mostrarMainApp`, `showSection`, `mostrarOverlayEnviando`, `mostrarOverlayAlerta`, `toast`, `abrirChat`…). Escribe en los campos letra por letra y guarda 88 estados, con la posición de cada botón para colocar el dedo.
- **No fue necesario iniciar sesión** en la cuenta real del cliente. Así no aparece ningún dato de ciudadanos y nadie tuvo que compartir contraseñas.
- **Recursos externos bloqueados por la red:** Font Awesome y Leaflet los descargué desde npm. Los mosaicos del mapa del camión los generé con código: un mapa estilizado de calles, con un lago al suroeste como el de Pátzcuaro. La dirección de la alerta es la de demostración, "Centro, Quiroga, Mich.".

## Guion (120 BPM, 20 compases de 2 s)

| Tiempo | Escena |
|---|---|
| 0–4 s | Intro blanca del Ayuntamiento: explosión de pétalos otomíes, logo "QUIROGA ¡es ahora!" con rebote y "Quiroga Digital · La app de tu municipio". Pasa al azul con un barrido circular. |
| 4–6 s | Entra el teléfono con la pantalla de inicio de Android y el **ícono real de la app** (el Palacio Municipal); el dedo lo toca. |
| 6–8 s | El ícono se expande y aparece el **splash real**, con su propio video de bienvenida (`splash-video.mp4`). |
| 8–14 s | **Registro:** la pestaña "Registrarse", nombre escrito letra por letra, contraseña, teléfono, género, localidad, dirección, términos y "Crear cuenta". Después la **verificación por SMS** y "¡Teléfono verificado!". |
| 14–16 s | Inicio: "Bienvenido a Quiroga Digital · Hola, María", con un desplazamiento suave. |
| 16–24 s | **ALERTA MUJER** (fondo rojo con pulsos): se mantiene presionado el botón **2 segundos reales**, con un anillo de progreso y acercamiento de cámara. Luego "Enviando alerta…", "ALERTA MUJER ACTIVA" con folio, ubicación y hora, se elige "Estoy en peligro" y la barra de estados avanza: Enviada → Recibida → **Personal de seguridad asignado** → **En atención**. |
| 24–26 s | El widget "ALERTA MUJER" en la pantalla de inicio y el acceso directo con pulsación larga sobre el ícono. |
| 26–30 s | Reportes: área Obras Públicas, "Bache en calle Morelos", descripción, ubicación, "Enviar" y "Reporte enviado · Folio". |
| 30–32 s | Avisos oficiales: vacunación, alumbrado y horario de Presidencia, con desplazamiento. |
| 32–34 s | Camión de basura en tiempo real, avanzando por el mapa. |
| 34–36 s | Mensajes: las áreas del Ayuntamiento y un chat con Obras Públicas. |
| 36–40 s | Cierre blanco: logo, ícono, "Quiroga Digital · Tu municipio en tu celular", las 5 funciones y "¡Muy pronto en tu celular!". |

## Identidad visual

- **Colores de la app** (`--primary #002068`, `--secondary-container #e2007c`) y del logo: amarillo, verde, rojo y celeste de las flores otomíes.
- **Tipografía de la app:** Plus Jakarta Sans.
- **No puse escudo ni nombre oficial de la administración, ni dónde se descarga**, porque el cliente lo pidió así: "apenas es una prueba".

## Música y sonido (`src/synth.py`, sintetizado desde cero)

- Pop institucional optimista en Sol mayor, con la progresión G–D–Em–C.
- Las secciones siguen la historia: intro, groove ligero, tensión en Alerta Mujer, groove completo con melodía de campanas y cierre.
- **El diseño de sonido va sincronizado con la pantalla** mediante `src/timeline.json`:
  - un clic en cada toque y tecleo suave al escribir;
  - "whoosh" en cada transición y campanitas en las confirmaciones;
  - un **latido que acelera** durante los 2 segundos de presión de la Alerta Mujer, y la alarma al enviarse.

## Iteraciones

1. **Laboratorio:** al principio varias pantallas salían en blanco, porque la app se queda oculta los ~7 s de su video de bienvenida. Lo resolví mostrando `#app` de inmediato.
2. **Mapa gris** por los mosaicos bloqueados; generé mosaicos estilizados.
3. **v1 del video:**
   - en vertical, el logo pequeño chocaba con el número del título;
   - el acercamiento de la Alerta Mujer tapaba el título;
   - en horizontal, la línea de acento cruzaba la "A".

   Corregí el acomodo y cambié el acercamiento para que crezca hacia abajo, con la parte de arriba fija.

## Rehacerlo

```bash
node lab/shoot.js lab/record.js lab/rec1    # capturas de la app (requiere el repo quiroga-app en /home/user)
./build.sh                                  # música + video en los dos formatos
```
