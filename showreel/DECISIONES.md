# DECISIONES — Showreel de motion design (15 s · 1920×1080 · 60 fps)

**Entregable:** `showreel.mp4`: H.264 High, yuv420p BT.709, CRF 14, 900 fotogramas exactos, AAC 320 kbps 48 kHz estéreo, 15,000 s.
**Regla que me impuse:** todo sale de código. No hay imágenes, vídeo, audio ni samples, y no usé modelos generativos. Las únicas dependencias externas son tipografías del sistema (Inter Display y JetBrains Mono).

---

## 1. La idea rectora: la película vive en la rejilla musical

Lo primero que decidí fue el tempo, antes que cualquier imagen. A **128 BPM**, **8 compases de 4/4 duran exactamente 15,000 s**: cada compás dura 1,875 s, cada negra 0,46875 s y cada semicorchea 0,117 s. Con eso:

- Cada compás es una escena (8 escenas) y cada corte cae en un tiempo fuerte.
- El vídeo y la música usan la misma lista de bombos. La de `synth.py` está replicada literalmente en `index.html`, y de ella se calculan los pulsos de zoom, los anillos del drop, el *shake* de cámara y el rebote de los metaballs. La sincronía es exacta por construcción; no la ajusté "a ojo".
- La forma es la de un tema de electrónica: intro (compás 1), *build* (2–4), silencio de una semicorchea, **drop** (5–7) y resolución en el logo (8). La curva emocional la marca la música y la imagen la sigue.

## 2. Guion (compás por compás)

| # | Tiempo | Escena | Qué demuestra | Transición de salida |
|---|---|---|---|---|
| 1 | 0,00–1,88 | **Intro / dial**: un punto que crece y se vuelve anillo, 64 marcas que aparecen en corcheas (cada mayor coincide con un *tick* de audio) y un contador 000→100 % | Timing, anticipación | El dial gira y se encoge con `easeInBack` (anticipación) |
| 2 | 1,88–3,75 | **MOTION → DESIGN**: wipe circular doble (crema y luego naranja), letras que suben por máscara con *stagger*, *flip* letra a letra de MOTION a DESIGN (ambas palabras tienen 6 letras, a propósito) | Tipografía cinética | Todo el bloque se aplasta (*squash*) hasta quedar en una línea |
| 3 | 3,75–5,63 | **Lenguaje de formas**: rejilla de 66 objetos que se transforman círculo→cuadrado→triángulo→cruz con una onda radial de *offset* (260 ms del centro al borde) | Morphing, *offset animation*, sistemas | La línea anterior se abre como un panel crema. Al final todo colapsa al centro |
| 4 | 5,63–7,50 | **Dimensión**: icosfera 3D propia (42 vértices, proyección en perspectiva y profundidad codificada en grosor y alfa), campo de 520 estrellas que acelera con el *riser* y tipografía extruida por capas | 3D sin motor 3D, *build* de tensión | Zoom exponencial, *shake* creciente y, en la última semicorchea, negro con una sola línea: la respiración antes del drop |
| 5 | 7,50–9,38 | **DROP · RHYTHM**: flash, caleidoscopio de cuñas, anillos que nacen en cada bombo, espectro radial y la palabra que tartamudea cada semicorchea (aberración cromática, saltos, cortes, *outline*) | Energía, ritmo, *audio-reactive* | Un iris de tinta se traga el cuadro |
| 6 | 9,38–11,25 | **FLOW**: metaballs con **normales analíticas e iluminación por píxel** (difusa, especular y *rim*). La palabra FLOW aparece invertida dentro del líquido | Simulación orgánica y *shading* | Las bolas se funden en una sola |
| 7 | 11,25–13,13 | **DETAIL**: subdivisión recursiva del cuadro en corcheas (1→2→4→8→16→~24 paneles), cada uno con su propia micro-animación | Composición, densidad, *design systems* | *Glitch* de cortes horizontales sincronizado con el *stutter* del audio y colapso al centro |
| 8 | 13,13–15,00 | **Identidad**: onda de choque, ráfaga de partículas, anillo que se dibuja, punto naranja que orbita y **aterriza en la muesca justo en la campana FM**, nombre con *tracking* que se comprime y subtítulos descifrados | Cierre de marca | Fundido a negro con la cola de reverb |

**Capa de "acabado"** sobre todo el vídeo:
- HUD de editor (timecode real a 60 fps, escena, metrónomo visual de 4 puntos, barra de progreso, marcas de corte) en modo `difference`, para que se lea sobre cualquier fondo.
- Grano de película animado y viñeta.
- *Shake* de cámara con ruido suave que decae tras cada impacto.

## 3. Decisiones técnicas

- **Motor visual:** Canvas 2D en Chromium headless (Playwright). Cada fotograma es una función pura del número de fotograma, así que el render es determinista y se pudo **paralelizar en 4 procesos**. Todo el azar es sembrado (`mulberry32` y un hash entero).
- **Motion blur real:** acumulo sub-fotogramas con un obturador de 180°. Normalmente uso 8 sub-muestras; **16 en los 0,22 s posteriores a cada corte**, donde los movimientos son más violentos; 2 en los metaballs, que son caros por píxel; y **1 durante el glitch**, que tiene que verse nítido. HUD y grano se aplican después de la acumulación para que no se emborronen.
- **Morphing:** las cuatro formas se muestrean a 96 puntos por perímetro, todas en sentido horario desde las 12. Así la interpolación es limpia y no aparecen "nudos".
- **Metaballs:** campo Σr²/d² a media resolución (960×540) con antialiasing por distancia firmada aproximada (f−1)/|∇f|. La normal sale del gradiente de h = 1−1/f. Para mezclar dos capas (FLOW crema detrás y FLOW tinta recortado con la máscara del líquido) uso `destination-in`.
- **Paleta:** tinta `#0C0C11`, crema `#F4EFE6`, naranja `#FF4A1C`, cobalto `#2B3BFF` y acentos lima y rosa. Hay pocos colores, todos muy saturados, y cada escena domina uno, de modo que cada corte también cambia de color.
- **Tipografía:** Inter Display Black para los titulares (impacto) y JetBrains Mono para los metadatos (el tono "técnico" del HUD).
- **Pipeline:** PNG → segmentos `libx264rgb` sin pérdida → concatenación → codificación final única, con conversión explícita a BT.709 y rango TV para no desplazar los colores.

## 4. Música (sintetizada desde cero con numpy)

Fa menor, 128 BPM. Progresión: Fm · Fm · D♭ · E♭ (*build*) · Fm · D♭ · A♭→E♭ · Fm9.

- **Bombo:** seno con barrido de pitch, *click* filtrado y saturación `tanh`.
- **Clap:** 4 ráfagas de ruido pasabanda más una cola.
- **Hi-hats:** ruido más parciales cuadradas inarmónicas (sonido "metálico"), con *swing* en semicorcheas.
- **Bajo:** sierra aditiva *band-limited* con un "filtro" espectral que se abre con envolvente, más un sub. En el drop pasa a *rolling bass* en semicorcheas.
- **Pads:** *supersaw* de 7 voces desafinadas y abiertas en estéreo, con la frecuencia de corte automatizada por compás, que es la que cuenta la historia: cerrado en la intro y abierto en el drop.
- **Arpegio *pluck*** con *delay ping-pong* de 3/16, insinuado ya en el *build*.
- **Diseño sonoro:** *ticks* del dial, *reverse swell*, *riser* (ruido filtrado más tono que sube tres octavas), *whooshes* en cada transición, impactos (sub + crack + aire) en los tres momentos clave, redoble de caja que acelera y **campanas FM** que suenan cuando el punto del logo aterriza.
- **Mezcla:** *sidechain* desde el bombo sobre bajo, pads y arpegio; reverb por **convolución FFT con una respuesta al impulso sintética** que se oscurece con el tiempo; hueco de silencio antes del drop; *stutter* (re-disparo de *slices* cada vez más cortas y agudas) en el último tiempo del compás 7; *soft-clip* y techo de −1 dBFS.

## 5. Lo que descarté (y por qué)

- **WebGL/shaders:** en este contenedor Chromium no tiene GPU (SwiftShader). Canvas 2D por CPU era más predecible y alcanzó para la iluminación por píxel.
- **Python/PIL para la imagen:** daba un antialiasing pobre y tipografía limitada. Canvas ofrece trazados, texto, composición y filtros.
- **Reverb Schroeder/Freeverb con bucles:** era lenta en Python puro. La convolución FFT es más rápida y suena mejor.
- **Filtros recursivos para pads y bajo:** los sustituí por síntesis aditiva con atenuación espectral variable en el tiempo, que es vectorizable y no tiene *aliasing*.
- **Marching squares para los metaballs:** daba bordes nítidos pero sin volumen. El *shading* por píxel lucía mucho más.
- **Una melodía *lead*:** en 15 s competía con la tipografía. Me quedé con el arpegio y los pads.
- **Más escenas (partículas con física, *line-art* de mapas):** superaban una por compás y diluían el ritmo de cortes.

## 6. Iteraciones

1. **v1 de la música:** la revisé con espectrograma y sonoridad por medio compás (no puedo escuchar, así que verifiqué la forma: dinámica de la intro, *riser* que culmina en 7,5 s, hueco antes del drop y campanas en el logo). La estructura salió bien a la primera.
2. **v1 visual (fotogramas sueltos en hoja de contactos):** encontré tres problemas:
   - el texto *scramble* sólo mostraba la letra "A", porque mi hash desbordaba la precisión del float. Lo reescribí con `Math.imul`;
   - una etiqueta chocaba con el HUD;
   - los metaballs se salían del cuadro por arriba.
3. **v2:** corregí además una costura dura en la rampa de color del líquido (el *wrap* pasaba de naranja a azul de golpe) con una rampa *ping-pong* suavizada, y unifiqué la numeración de escenas con el HUD. Hice el primer render completo y lo revisé fotograma a fotograma en las transiciones.
4. **v3:** en los movimientos ultrarrápidos (wipe circular, *pop* elástico de la esfera) el motion blur se veía **escalonado**, como anillos discretos. Introduje sub-muestreo adaptativo (16 sub-fotogramas tras cada corte). También adelanté los subtítulos del logo, que terminaban de descifrarse justo cuando empezaba el fundido. Hice el render final y lo verifiqué: 900 fotogramas, 15,000 s, audio de 15,000 s.

## 7. Tiempo total

| Fase | Hora (UTC) |
|---|---|
| Inicio (exploración del entorno) | 18:17 |
| Música v1 terminada | 18:24 |
| Motor visual v1 y primera revisión | 18:28 |
| v2 renderizado y revisado | 18:34 |
| v3 final renderizado y codificado | 18:40 |
| Documentación y entrega | ~18:45 |

**Total: unos 28 minutos de reloj.** Cada render completo tarda unos 4–5 min de CPU con 4 procesos (~0,8–1 s por fotograma por proceso, por el motion blur multimuestra), y la síntesis de audio unos 30 s.

## 8. Cómo reproducirlo

```bash
./build.sh   # requiere python3+numpy, node+playwright (Chromium), ffmpeg
```

Fuentes: `src/synth.py` (música), `src/index.html` (todas las escenas) y `src/render.js` (render por fotogramas).
