# Sonido y Karaoke Show Charly: video promocional (30 s)

Entregables:
- `out/sonido_karaoke_9x16.mp4`, 1080×1920 a 60 fps, para TikTok, Reels y Shorts.
- `out/sonido_karaoke_16x9.mp4`, 1920×1080 a 60 fps, para YouTube y Facebook.

Usé el mismo método que en los videos anteriores: todo está hecho con código y la música es original, sintetizada desde cero.

## Guion (12 compases de 2,5 s, a 96 BPM)

| Tiempo | Escena |
|---|---|
| 0–2,5 s | **Intro.** Escenario oscuro: entran las bocinas, se encienden las luces robóticas una por una, láseres sincronizados con el audio y "SONIDO" en neón que se prende letra por letra con el acordeón. |
| 2,5–5 s | **Logo.** Golpe, bola disco, sello con micrófono, "SONIDO / Y KARAOKE" y la etiqueta "Música · Karaoke · Diversión". |
| 5–7,5 s | **"¡AMENIZAMOS TODO TIPO DE EVENTOS!"**, una línea por tiempo con confeti. |
| 7,5–17,5 s | **Cumpleaños · Bautizos · XV años · Bodas.** Cada evento tiene su color, su ícono animado (pastel con velas, paloma, corona, anillos) y **un marco de video**. |
| 17,5–20 s | **"…O CUALQUIER EVENTO QUE TENGAS"**, con un desfile de íconos. |
| 20–25 s | **Karaoke.** Pantalla con la letra que se ilumina al ritmo y una pelotita que rebota: "¡Canta con nosotros! / ¡Esta noche es tuya!". |
| 25–27,5 s | **"¡CONTRÁTANOS!"** con todos los servicios. |
| 27,5–30 s | **Cierre.** Logo e "Informes y contrataciones". |

## Decisiones

- **Texto del cliente:** corregí "amenazamos" a "amenizamos" y respeté la lista: cumpleaños, bautizos, XV años, bodas "o cualquier evento que tengas".
- **Música: cumbia sonidera** a 96 BPM en La menor. Lleva:
  - güiro largo-corto-corto, congas y redobles de timbal cada 2 compases;
  - bajo cumbiero y acordeón con **eco de sonidero** (*delay* de 3/16);
  - los clásicos **"láser"** de sonidero, que en pantalla se ven como rayos sincronizados.
- **Identidad de fiesta nocturna:** fondo morado noche con magenta, cian y amarillo neón. Las bocinas laten con el bombo y hay luces robóticas y bola disco con destellos.
- **Tus 4 videos:**

  | Escena | Video | Por qué |
  |---|---|---|
  | Cumpleaños | WA0017 (vertical, pista llena), 0–2,5 s | Ambiente de fiesta con mucha gente |
  | Bautizos | WA0018 (carpa con altar y cruces), 2–4,5 s | Es una ceremonia religiosa |
  | XV años | WA0017, 5–7,5 s | Pista con luces y gente bailando |
  | Bodas | WA0019 (DJ con luces robóticas), 9–11,5 s | Lo más vistoso del equipo de luces |
  | Karaoke (fondo de la pantalla) | WA0020, desde el segundo 21 | Charly cantando al micrófono |

  - **Encuadre:** si el video tiene la misma forma que el marco, lo llena. Si no, va centrado y un poco acercado, con una copia desenfocada atrás que llena el marco, que es la técnica estándar de los editores.
  - **Color:** les subí un poco la saturación y el contraste para que las luces se vean más vivas.
  - **Audio:** no uso el sonido original de los clips. Suena la cumbia sonidera, para que todo vaya al ritmo.
  - **Archivo repetido:** WA0018 llegó dos veces (idéntico), así que lo usé una sola vez.
  - **Videos fuera del repo:** tus videos originales están en `media/` y no se suben al repo; solo se suben los videos terminados.
- **Zonas seguras en vertical:** los textos importantes quedan arriba de la franja donde TikTok y Reels ponen sus botones.

## Datos del cliente

- **Nombre:** Sonido y Karaoke Show Charly. En el logo: "SONIDO Y KARAOKE" en neón, "CHARLY" grande y la etiqueta "SHOW".
- **Teléfonos:** 443 119 4256 y 443 171 3766. Aparecen en "¡Contrátanos!" y en el cierre.

## Opcional

- Redes sociales (Facebook o TikTok) y ciudad, si quieres que salgan en el cierre.

## Iteraciones

1. **v1:** la gente de la pista salía amontonada al centro. En horizontal, la bocina derecha tapaba "Y KARAOKE". En vertical, la etiqueta se encimaba con el logo. El ícono del teléfono no se entendía.
2. **v2:** repartí a la gente a lo ancho, quité las bocinas del logo en horizontal, bajé la etiqueta y redibujé el teléfono.
3. **v3, con tu primer video:** ajusté el marco vertical a la proporción del video, porque quedaban franjas desenfocadas a los lados, y moví la etiqueta para que no chocara con la tilde de la Ñ.
4. **v4, con 3 videos:** cambié la carga de los videos para leer solo los cuadros que se necesitan en cada momento y no saturar la memoria. Repartí los clips por escena, aclaré el fondo del karaoke y acerqué los videos horizontales en el formato vertical.
5. **v5, con el nombre, los teléfonos y WA0020:** rehice el logo con el nombre real, agregué los dos teléfonos y metí el video de Charly cantando en XV años y en el karaoke. También acomodé la etiqueta "SHOW", que tapaba "KARAOKE", el espacio de los teléfonos y la bola disco, que tocaba el logo en vertical.

## Rehacerlo

```bash
./build.sh
```

Si se interrumpe, se puede volver a correr: retoma los segmentos que quedaron incompletos.
