// Frame renderer: headless Chromium draws each frame deterministically from its index.
//   node render.js preview <outdir> f1 f2 ...      -> PNG stills
//   node render.js segment <out.mkv> <from> <to>   -> lossless RGB segment [from, to)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const [mode, outp, ...rest] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  page.on('console', m => console.log('[page]', m.text()));
  await page.goto('file://' + path.resolve(__dirname, 'index.html'));
  await page.evaluate(() => window.ready);
  const clip = { x: 0, y: 0, width: 1920, height: 1080 };
  if (mode === 'preview') {
    fs.mkdirSync(outp, { recursive: true });
    for (const f of rest.map(Number)) {
      await page.evaluate(f => window.renderFrame(f), f);
      await page.screenshot({ path: path.join(outp, `f${String(f).padStart(4, '0')}.png`), clip });
    }
  } else {
    const from = +rest[0], to = +rest[1];
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '60', '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', outp], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let f = from; f < to; f++) {
      await page.evaluate(f => window.renderFrame(f), f);
      const buf = await page.screenshot({ type: 'png', clip });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((f - from) % 30 === 0) console.log(`[${from}-${to}] frame ${f} ${((Date.now() - t0) / (f - from + 1)).toFixed(0)}ms/f`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
