# Sonido y Karaoke: video promocional (30 s)

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
- **Tu video (VID-20261105-WA0017, vertical, 10,5 s):** lo usé en los 4 marcos de eventos, un tramo distinto en cada uno (0–2,5 s, 2,5–5 s, 5–7,5 s y 7,5–10 s), para que no se repita ninguna toma. Le subí un poco la saturación y el contraste para que las luces se vean más vivas.
  - **En vertical**, el marco tiene la misma proporción que tu video, así que se ve completo y grande.
  - **En horizontal**, tu video va al centro y detrás una copia desenfocada llena el marco, que es la técnica estándar para poner video vertical en pantalla ancha.
  - El audio original del clip no se usa; suena la cumbia sonidera, para que todo vaya al ritmo.
  - Si me mandas más clips, cada evento puede tener su propio video. La pista de baile animada queda como respaldo para cualquier marco sin clip.
- **Zonas seguras en vertical:** los textos importantes quedan arriba de la franja donde TikTok y Reels ponen sus botones.

## Pendiente (me lo tienes que pasar)

1. **El nombre exacto del sonido.** Por ahora dice "SONIDO / Y KARAOKE". Se cambia en una sola línea (`BRAND`).
2. **El teléfono o WhatsApp.** El cierre dice "Informes y contrataciones" y hay espacio listo para el número. No inventé ninguno.
3. **Más videos (opcional)**: con uno por evento (un cumpleaños, un bautizo, unos XV, una boda) queda todavía más fuerte.
4. **Redes sociales y ciudad**, si quieres que salgan.

## Iteraciones

1. **v1:** la gente de la pista salía amontonada al centro. En horizontal, la bocina derecha tapaba "Y KARAOKE". En vertical, la etiqueta se encimaba con el logo. El ícono del teléfono no se entendía.
2. **v2:** repartí a la gente a lo ancho, quité las bocinas del logo en horizontal, bajé la etiqueta y redibujé el teléfono.
3. **v3, con tu video:** detuve el render que iba corriendo para meter tu clip. Ajusté el marco vertical a la proporción del video, porque al principio quedaban franjas desenfocadas a los lados, y moví la etiqueta para que no chocara con la tilde de la Ñ.

## Rehacerlo

```bash
./build.sh
```

Si se interrumpe, se puede volver a correr: retoma los segmentos que quedaron incompletos.
