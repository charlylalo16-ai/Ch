// node promo/shoot_feature.js <out.png>  -> 1024x500 PNG sin transparencia (requisito de Google Play)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2048, height: 1000 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'feature.html')); await p.waitForFunction(() => window.done === true);
  await p.locator('canvas').screenshot({ path: process.argv[2] + '.2x.png' }); await b.close();
})();
