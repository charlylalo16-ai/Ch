// Ajusta cada SVG a su contenido (viewBox justo + margen) y exporta PNG transparente en alta resolución.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  fs.mkdirSync('dist/png', { recursive: true });
  for (const f of fs.readdirSync('dist/svg').filter(x => x.endsWith('.svg'))) {
    const svgTxt = fs.readFileSync(path.join('dist/svg', f), 'utf8');
    await p.setContent(`<html><body style="margin:0;background:transparent">${svgTxt}</body></html>`);
    const vb = await p.evaluate(() => { const s = document.querySelector('svg'); const bb = s.getBBox();
      // getBBox ignora el grosor de trazo: medir con los rectángulos en pantalla
      s.setAttribute('width', 2000); const r = s.getBoundingClientRect(); const ctm = s.getScreenCTM().inverse();
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      s.querySelectorAll('path,polygon,rect,circle,ellipse').forEach(el => { if (el.closest('mask,clipPath,defs')) return; const q = el.getBoundingClientRect(); if (!q.width && !q.height) return;
        for (const [px, py] of [[q.left, q.top], [q.right, q.bottom]]) { const pt = new DOMPoint(px, py).matrixTransform(ctm); x0 = Math.min(x0, pt.x); y0 = Math.min(y0, pt.y); x1 = Math.max(x1, pt.x); y1 = Math.max(y1, pt.y); } });
      const pad = Math.max(x1 - x0, y1 - y0) * 0.03; return [x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad]; });
    const fixed = svgTxt.replace(/viewBox="[^"]+"/, `viewBox="${vb.map(v => v.toFixed(2)).join(' ')}"`);
    fs.writeFileSync(path.join('dist/svg', f), fixed);
    const Wpx = 4000, Hpx = Math.round(Wpx * vb[3] / vb[2]);
    await p.setViewportSize({ width: Wpx, height: Hpx });
    await p.setContent(`<html><body style="margin:0;background:transparent">${fixed.replace('<svg ', `<svg width="${Wpx}" height="${Hpx}" style="display:block" `)}</body></html>`);
    await p.locator('svg').screenshot({ path: path.join('dist/png', f.replace('.svg', '.png')), omitBackground: true });
    console.log(f, Wpx + 'x' + Hpx);
  }
  await b.close();
})();
