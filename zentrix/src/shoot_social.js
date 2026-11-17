// node src/shoot_social.js <outdir>
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const P = { avatar: [1080, 1080], fb: [1640, 624], yt: [2560, 1440], li: [1584, 396], post1: [1080, 1350], post2: [1080, 1350], post3: [1080, 1350], post4: [1080, 1350], story1: [1080, 1920], story2: [1080, 1920], story3: [1080, 1920], story4: [1080, 1920] };
const NAMES = { avatar: 'perfil_1080', fb: 'portada_facebook_1640x624', yt: 'banner_youtube_2560x1440', li: 'banner_linkedin_1584x396' };
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  for (const [k, [w, h]] of Object.entries(P)) {
    const pg = await b.newPage({ viewport: { width: w, height: h } }); pg.on('pageerror', e => console.log('ERR', k, e.message));
    await pg.goto('file://' + path.resolve(__dirname, 'social.html') + '?p=' + k); await pg.waitForFunction(() => window.done === true, null, { timeout: 60000 });
    const name = NAMES[k] || (k.startsWith('post') ? `publicacion_${k.slice(4)}_1080x1350` : `historia_${k.slice(5)}_1080x1920`);
    await pg.locator('canvas').screenshot({ path: path.join(out, `zentrix_${name}.png`) }); await pg.close();
  }
  await b.close();
})();
