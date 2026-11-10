// node promo/shoot.js <outdir>  -> 6 piezas × (post 1080x1350, story 1080x1920) PNG
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const names = ['general', 'alerta-mujer', 'reportes', 'avisos', 'camion', 'mensajes'];
  for (const fmt of ['post', 'story']) {
    const pg = await b.newPage({ viewport: { width: 1080, height: fmt === 'story' ? 1920 : 1350 } });
    pg.on('pageerror', e => console.log('ERR', e.message));
    for (let p = 0; p < names.length; p++) {
      await pg.goto('file://' + path.resolve(__dirname, 'index.html') + `?fmt=${fmt}&p=${p}`);
      await pg.waitForFunction(() => window.done === true, null, { timeout: 20000 });
      await pg.locator('canvas').screenshot({ path: path.join(out, `quiroga_proximamente_${String(p + 1).padStart(2, '0')}_${names[p]}_${fmt}.png`) });
    }
    await pg.close();
  }
  await b.close();
})();
