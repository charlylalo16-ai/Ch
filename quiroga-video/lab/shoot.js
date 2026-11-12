// Abre la app real (index.html del repo) en un teléfono virtual y ejecuta pasos.
// node shoot.js <pasos.js> <outdir>
// pasos.js exporta: async function (page, shot) { ... }  — shot(nombre) guarda una captura.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const APP = '/home/user/quiroga-app/index.html';
const C = path.join(__dirname, 'cache');
const FA = path.join(C, 'fortawesome-fontawesome-free-6.4.0/package');
const LF = path.join(C, 'leaflet-1.9.4/package/dist');
(async () => {
  const [stepsFile, outdir] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: +(process.env.VW || 412), height: +(process.env.VH || 892) }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
    geolocation: { latitude: 19.6650, longitude: -101.5240 }, permissions: ['geolocation'], locale: 'es-MX', timezoneId: 'America/Mexico_City' });
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('[pageerror]', String(e).slice(0, 200)));
  await page.addInitScript({ path: path.join(__dirname, 'stub-firebase.js') });
  await page.route('**/*', async route => {
    const u = route.request().url();
    if (u.startsWith('file://') || u.startsWith('data:') || u.startsWith('blob:')) return route.continue();
    const ok = (file, type) => route.fulfill({ path: file, contentType: type });
    if (u.includes('gstatic.com/firebasejs')) return route.fulfill({ body: '/* firebase simulado */', contentType: 'text/javascript' });
    if (u.startsWith('https://fonts.googleapis.com/css2')) return ok(path.join(C, 'gf_local.css'), 'text/css');
    if (u.startsWith('https://fonts.gstatic.com/gfonts/')) return ok(path.join(C, u.split('fonts.gstatic.com/')[1]), 'font/woff2');
    if (u.includes('font-awesome') && u.endsWith('all.min.css')) return ok(path.join(FA, 'css/all.min.css'), 'text/css');
    if (u.includes('/webfonts/')) return ok(path.join(FA, 'webfonts', u.split('/webfonts/')[1].split('?')[0]), 'font/woff2');
    if (u.includes('leaflet') && u.endsWith('leaflet.css')) return ok(path.join(LF, 'leaflet.css'), 'text/css');
    if (u.includes('leaflet') && u.endsWith('leaflet.js')) return ok(path.join(LF, 'leaflet.js'), 'text/javascript');
    if (u.includes('/images/') && u.includes('leaflet')) return ok(path.join(LF, 'images', u.split('/images/')[1]), 'image/png');
    if (/tile|openstreetmap|arcgis|carto/.test(u)) { fs.appendFileSync(path.join(__dirname, 'tiles.log'), u + '\n'); const t = path.join(__dirname, 'tiles', u.replace(/[^a-z0-9]/gi, '_') + '.png'); if (fs.existsSync(t)) return ok(t, 'image/png'); }
    return route.abort();
  });
  let n = 0;
  const shot = async (name) => { await page.waitForTimeout(250); await page.screenshot({ path: path.join(outdir, `${String(++n).padStart(2, '0')}_${name}.png`) }); };
  await page.goto('file://' + APP);
  await require(path.resolve(stepsFile))(page, shot);
  await browser.close();
})();
