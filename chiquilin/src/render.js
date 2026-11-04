// node render.js preview <piece> <fmt> <outdir> f1 f2 ...
// node render.js segment <piece> <fmt> <out.mkv> <from> <to>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'), fs = require('fs');
(async () => {
  const [mode, piece, fmt, outp, ...rest] = process.argv.slice(2);
  const [w, h] = fmt === 'v' ? [1080, 1920] : [1920, 1080];
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
  await page.goto('file://' + path.resolve(__dirname, 'index.html') + `?piece=${piece}&fmt=${fmt}`);
  await page.evaluate(() => window.ready);
  const clip = { x: 0, y: 0, width: w, height: h };
  if (mode === 'preview') {
    fs.mkdirSync(outp, { recursive: true });
    for (const f of rest.map(Number)) { await page.evaluate(f => renderFrame(f), f); await page.screenshot({ path: path.join(outp, `${piece}_${fmt}_${String(f).padStart(4, '0')}.png`), clip }); }
  } else {
    const from = +rest[0], to = Math.min(+rest[1], await page.evaluate(() => NFRAMES));
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '60', '-c:v', 'png', '-i', '-', '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', outp], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = from; f < to; f++) {
      await page.evaluate(f => renderFrame(f), f);
      const buf = await page.screenshot({ type: 'png', clip });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
