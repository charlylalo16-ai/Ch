# El Chiquilín: sistema de videos para el canal

Son 6 videos con la misma calidad y el mismo método que el showreel. Todo está hecho con código: ilustraciones, animación y música compuesta y sintetizada desde cero, sin fotos, stock ni samples.

| Archivo | Formato | Duración | Uso |
|---|---|---|---|
| `out/chiquilin_menu_16x9.mp4` | 1920×1080 · 60 fps | 15 s | YouTube y Facebook |
| `out/chiquilin_menu_9x16.mp4` | 1080×1920 · 60 fps | 15 s | TikTok, Reels y Shorts |
| `out/chiquilin_intro_16x9.mp4` y `_9x16` | ambos | 3,75 s | Para abrir cualquier video |
| `out/chiquilin_cierre_16x9.mp4` y `_9x16` | ambos | 3,75 s | Para cerrar cualquier video ("¡SÍGUENOS!") |

## Qué decidí

- **Identidad tomada de tu propio sistema** (`Tacos_chiquilin/index.html`):
  - Colores: rojo `#c0131b`, amarillo `#f5c800`, café `#1a0800`, crema `#fff9ee`, naranja `#e65100` y verde `#1a7a3a`.
  - Tipografía Fredoka, la misma familia redondeada de la app.
  - El lema "Tacos de Birria".
- **Menú real:** usé los productos y precios por defecto de la app (`MENU0`):
  - Taco dorado $25, Volcán $35, Sube $40, Quesadilla $45.
  - Consomé chico $20 / grande $35.
  - Bebidas desde $15.
- **Motivo de marca: papel picado** animado (6 colores, cortes calados generados por código). Se mece en cada cambio de escena.
- **Ilustraciones vectoriales en estilo sticker:** contorno café grueso y sombra plana. Cada platillo tiene su detalle animado: el queso del volcán escurre, la quesadilla se jala con hilos de queso, el consomé echa vapor y las bebidas se mueven.
- **Música:** guaracha/cumbia electrónica a 128 BPM en Fa mayor. Lleva güiro (largo-corto-corto), congas, timbales, bajo cumbiero raíz-quinta, acordeón sintetizado tipo musette con 3 lengüetas desafinadas, acordes "chucu" a contratiempo y silbato de fiesta. Igual que en el showreel, cada escena dura un compás (1,875 s) y todo va sincronizado al bombo.
- **Estructura del menú (8 compases = 15 s):** logo → 5 platillos → bebidas → cierre "¡TE ESPERAMOS!".
- **Transiciones:** barrido diagonal con filo amarillo y café, siempre el mismo, como firma visual. Hay motion blur real (de 6 a 12 sub-fotogramas).
- **Zonas seguras en vertical:** precios y textos importantes quedan fuera de la franja inferior y del lado derecho, donde TikTok y Reels ponen sus botones.

## Lo que descarté

- **Intro y cierre de 15 s:** los hice de 3,75 s (2 compases). Un intro de 15 s hace que la gente se salga del video; corto se puede pegar al inicio y al final de cualquier video. El video de menú sí dura 15 s.
- **Fotos o ilustraciones de IA:** no las usé, para mantener el método 100 % código.
- **Precios inventados:** no puse ninguno; todos vienen de tu app.

## Iteraciones

1. **v1:** la etiqueta "MENÚ · 0X/05" se encimaba con el nombre del platillo y los íconos del intro quedaban cortados abajo. Ahora la etiqueta se coloca según el tamaño real del nombre y reacomodé los íconos para cada formato.
2. **v2:** el banderín rojo desaparecía sobre el fondo rojo. Ahora el papel picado cambia ese color cuando coincide con el fondo.

## Para confirmar

- **"Sube":** no sé exactamente qué es. Lo dibujé como dos tacos con una flecha hacia arriba ("más"). Dime qué lleva y ajusto el dibujo.
- **Precios:** son los de `MENU0`. Si en Firebase tienes otros, cámbialos en `DATA.products` dentro de `src/index.html` y vuelve a correr el render.
- **Redes y dirección:** cuando tengas el nombre de usuario del canal, la dirección o el teléfono, los agrego al cierre.

## Cómo hacer más videos

```bash
./build.sh            # vuelve a generar los 6 videos
```

- Precios, nombres y colores están en `DATA.products` (`src/index.html`).
- El orden de escenas de cada pieza está en `TL`. Ahí se pueden armar piezas nuevas, como "promo del día" o "horarios", reutilizando las escenas.

## Tiempo

De las 18:47 a las ~19:10 UTC, unos 25 minutos: análisis de la marca en tu repo, música, motor visual, 2 iteraciones y render de 6 videos.
