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
- **Clips de video:** como todavía no tengo tus videos, cada marco muestra una **pista de baile animada**, con gente bailando al ritmo, piso de colores y luces. En cuanto me mandes tus clips, entran en esos marcos.
- **Zonas seguras en vertical:** los textos importantes quedan arriba de la franja donde TikTok y Reels ponen sus botones.

## Pendiente (me lo tienes que pasar)

1. **El nombre exacto del sonido.** Por ahora dice "SONIDO / Y KARAOKE". Se cambia en una sola línea (`BRAND`).
2. **El teléfono o WhatsApp.** El cierre dice "Informes y contrataciones" y hay espacio listo para el número. No inventé ninguno.
3. **Tus videos de eventos**, para reemplazar la pista animada de cada marco.
4. **Redes sociales y ciudad**, si quieres que salgan.

## Iteraciones

1. **v1:** la gente de la pista salía amontonada al centro. En horizontal, la bocina derecha tapaba "Y KARAOKE". En vertical, la etiqueta se encimaba con el logo. El ícono del teléfono no se entendía.
2. **v2:** repartí a la gente a lo ancho, quité las bocinas del logo en horizontal, bajé la etiqueta y redibujé el teléfono. Con eso hice el render final.

## Rehacerlo

```bash
./build.sh
```

Si se interrumpe, se puede volver a correr: retoma los segmentos que quedaron incompletos.
