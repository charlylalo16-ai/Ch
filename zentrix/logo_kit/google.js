// Logo cuadrado para Google (Perfil de Negocio / cuenta): solo el símbolo ZS, centrado dentro del círculo de recorte.
const { chromium } = require('playwright'); const fs = require('fs');
const V = [
  ['zentrix_google_fondo_oscuro', 'zentrix_icono_fondo_oscuro', 'radial-gradient(circle at 50% 45%, #0f2a66 0%, #07080B 70%)'],
  ['zentrix_google_fondo_blanco', 'zentrix_icono_fondo_claro', '#FFFFFF'],
  ['zentrix_google_fondo_azul', 'zentrix_icono_blanco', 'linear-gradient(135deg, #3FB4FF 0%, #1E6BFF 50%, #0A35C9 100%)'],
];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2048, height: 2048 } });
  fs.mkdirSync('dist/google', { recursive: true });
  for (const [out, src, bg] of V) {
    const svg = fs.readFileSync(`dist/svg/${src}.svg`, 'utf8').replace('<svg ', '<svg style="width:74%;height:auto;display:block" ');
    await p.setContent(`<html><body style="margin:0"><div style="width:2048px;height:2048px;background:${bg};display:flex;align-items:center;justify-content:center">${svg}</div></body></html>`);
    await p.screenshot({ path: `dist/google/${out}_2048.png` });
    console.log(out);
  }
  await b.close();
})();
