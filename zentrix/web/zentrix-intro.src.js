/*!
 * ZENTRIX SYSTEMS · animación de intro (versión web, tiempo real)
 * Uso:
 *   <div id="intro" style="width:100%;height:100vh"></div>
 *   <script src="zentrix-intro.js"></script>
 *   <script>
 *     ZentrixIntro.mount(document.getElementById('intro'), {
 *       background: '#07080B',   // color de fondo, o 'transparent'
 *       hold: false,             // true = se queda en el logo final (no se desvanece)
 *       loop: false,             // true = se repite
 *       speed: 1,                // 1 = velocidad normal
 *       sound: null,             // ruta a zentrix-intro.mp3 (el navegador solo lo deja sonar tras un clic/toque)
 *       onEnd: () => {}          // se llama al terminar
 *     });
 *   </script>
 * mount() regresa { play(), pause(), restart(), seek(segundos), destroy() }.
 */
(function (root) {
  'use strict';
  var SVGTXT = __SVG__;
  var DUR = 12.0;
  var T = { ring0: 0.8, ring1: 3.4, z0: 2.6, zf: 3.5, s0: 3.2, sf: 4.1, acc: 4.55, hit: 4.9, word0: 5.9, word1: 7.5, stu0: 7.5, stu1: 8.8, end: 11.2 };
  var NS = 'http://www.w3.org/2000/svg';
  var clamp = function (x, a, b) { a = a === undefined ? 0 : a; b = b === undefined ? 1 : b; return Math.min(b, Math.max(a, x)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var prog = function (t, a, b) { return clamp((t - a) / (b - a)); };
  var E = { outC: function (t) { return 1 - Math.pow(1 - t, 3); }, inOutS: function (t) { return -(Math.cos(Math.PI * t) - 1) / 2; },
            outBack: function (t) { var s = 1.6; return 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); } };
  function hash(n) { var x = (Math.floor(n) | 0) ^ 0x9E3779B9; x = Math.imul(x ^ (x >>> 16), 0x85EBCA6B); x = Math.imul(x ^ (x >>> 13), 0xC2B2AE35); x ^= x >>> 16; return (x >>> 0) / 4294967296; }

  function mount(host, opt) {
    opt = opt || {};
    var BG = opt.background === undefined ? '#07080B' : opt.background, HOLD = !!opt.hold, LOOP = !!opt.loop, SPEED = opt.speed || 1;
    var reduce = root.matchMedia && root.matchMedia('(prefers-reduced-motion: reduce)').matches;
    // Shadow DOM: los ids internos del SVG no chocan con los de tu página
    var sr = host.shadowRoot || host.attachShadow({ mode: 'open' });
    sr.innerHTML = '<style>:host{display:block;position:relative;overflow:hidden}' +
      '.w{position:absolute;inset:0}canvas{position:absolute;left:0;top:0;width:100%;height:100%}' +
      '#logo{position:absolute;will-change:transform,opacity}#logo svg{width:100%;height:100%;overflow:visible;display:block}</style>' +
      '<div class="w"><canvas id="bg"></canvas><div id="logo"></div><canvas id="fx"></canvas></div>';
    var bg = sr.getElementById('bg'), fx = sr.getElementById('fx'), box = sr.getElementById('logo');
    var bc = bg.getContext('2d'), fc = fx.getContext('2d');
    box.innerHTML = SVGTXT; var svg = box.querySelector('svg'); svg.removeAttribute('width'); svg.removeAttribute('height');
    svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'ZENTRIX SYSTEMS');
    var VB = svg.viewBox.baseVal, AR = VB.width / VB.height;
    var $ = function (id) { return svg.querySelector('[id="' + id + '"]'); };
    var L = { back: $('01-orbita-atras'), S: $('02-S'), Z: $('03-Z'), acc: $('04-acento'), front: $('05-orbita-frente'),
              word: $('06-ZENTRIX'), stu: $('07-SYSTEMS') || $('07-STUDIO'), lines: $('08-lineas') };
    var backPath = L.back.querySelector('path'), frontPath = L.front.querySelector('path');
    var lenB = backPath.getTotalLength(), lenF = frontPath.getTotalLength();
    function outline(src, col, w) { var o = src.cloneNode(); o.removeAttribute('id'); o.setAttribute('fill', 'none'); o.setAttribute('stroke', col); o.setAttribute('stroke-width', w); o.setAttribute('stroke-linejoin', 'round'); src.parentNode.appendChild(o); return o; }
    var zPoly = L.Z.querySelector('polygon'), sPath = L.S.querySelector('path');
    var zOut = outline(zPoly, '#EAF2FF', 2.4), sOut = outline(sPath, '#7CC8FF', 2.4);
    var lenZ = zOut.getTotalLength ? zOut.getTotalLength() : 2000, lenS = sOut.getTotalLength();
    var defs = svg.querySelector('defs');
    defs.insertAdjacentHTML('beforeend', '<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="200" y2="120"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>');
    var shineG = defs.querySelector('#shine');
    function shineCopy(src) { var o = src.cloneNode(); o.removeAttribute('id'); o.setAttribute('fill', 'url(#shine)'); o.style.mixBlendMode = 'screen'; src.parentNode.appendChild(o); return o; }
    var zSh = shineCopy(zPoly), sSh = shineCopy(sPath);
    function comet(g) { var c = document.createElementNS(NS, 'circle'); c.setAttribute('r', 9); c.setAttribute('fill', '#ffffff'); c.style.filter = 'drop-shadow(0 0 6px #fff) drop-shadow(0 0 18px #3FB4FF) drop-shadow(0 0 40px #1E6BFF)'; g.appendChild(c); return c; }
    var cB = comet(backPath.parentNode), cF = comet(frontPath.parentNode);
    var letters = [].slice.call(L.word.children);
    var linesBB = L.lines.getBBox(), STB = L.stu.getBBox(), midX = VB.x + VB.width / 2;
    var PARTS = []; for (var i = 0; i < 160; i++) PARTS.push([hash(i * 3 + 1), hash(i * 5 + 2), hash(i * 7 + 3), hash(i * 11 + 4)]);

    // ---- tamaño: se adapta al contenedor (horizontal o vertical)
    var W = 1, H = 1, DPR = 1, VERT = false;
    function layout() {
      var r = host.getBoundingClientRect(); W = Math.max(1, r.width); H = Math.max(1, r.height); VERT = H > W;
      DPR = Math.min(2, root.devicePixelRatio || 1);
      [bg, fx].forEach(function (c) { c.width = Math.round(W * DPR); c.height = Math.round(H * DPR); });
      bc.setTransform(DPR, 0, 0, DPR, 0, 0); fc.setTransform(DPR, 0, 0, DPR, 0, 0);
      var lw = VERT ? W * 0.86 : Math.min(H * 0.84 * AR, W * 0.9), lh = lw / AR;
      box.style.width = lw + 'px'; box.style.height = lh + 'px';
      box.style.left = (W - lw) / 2 + 'px'; box.style.top = (H - lh) / 2 + (VERT ? -H * 0.03 : 0) + 'px';
      draw(cur);
    }
    var ro = root.ResizeObserver ? new ResizeObserver(layout) : null; if (ro) ro.observe(host); else root.addEventListener('resize', layout);

    function draw(t) {
      var fade = HOLD ? 1 : 1 - E.inOutS(prog(t, T.end, DUR));
      bc.clearRect(0, 0, W, H);
      if (BG !== 'transparent') { bc.fillStyle = BG; bc.fillRect(0, 0, W, H); }
      var amb = prog(t, 0.2, 2.0) * fade, gl = prog(t, T.hit - 0.2, T.hit + 1.2) * fade, M = Math.max(W, H);
      var g = bc.createRadialGradient(W / 2, H / 2, 10, W / 2, H / 2, M * 0.75); g.addColorStop(0, 'rgba(30,107,255,' + (0.08 * amb + 0.14 * gl) + ')'); g.addColorStop(1, 'rgba(0,0,0,0)'); bc.fillStyle = g; bc.fillRect(0, 0, W, H);
      var k_ = M / 1920;   // partículas a la misma densidad que el video
      for (var i = 0; i < PARTS.length; i++) { var a = PARTS[i][0], b = PARTS[i][1], s = PARTS[i][2], k = PARTS[i][3];
        var x = ((a * W + t * (10 + 34 * k) * k_) % (W + 40)) - 20, y = ((b * H - t * (5 + 22 * s) * k_) % H + H) % H;
        bc.fillStyle = 'rgba(90,160,255,' + ((0.1 + 0.4 * s) * amb * (0.6 + 0.4 * Math.sin(t * 2 + k * 9))) + ')'; bc.beginPath(); bc.arc(x, y, (1 + 2 * s) * Math.max(0.6, k_), 0, 7); bc.fill(); }
      var zoom = 1 + 0.05 * E.inOutS(prog(t, 0, DUR)), sh = t > T.hit ? 6 * Math.exp(-(t - T.hit) * 6) * (M / 1920) : 0, fr = Math.floor(t * 60);
      box.style.transform = 'translate(' + sh * (hash(fr) - .5) + 'px,' + sh * (hash(fr + 7) - .5) + 'px) scale(' + zoom + ')'; box.style.opacity = fade;
      var rp = E.inOutS(prog(t, T.ring0, T.ring1)), pb = clamp(rp * 2), pf = clamp(rp * 2 - 1);
      [[pb, backPath, lenB, cB], [pf, frontPath, lenF, cF]].forEach(function (o) { var p = o[0], path = o[1], len = o[2], c = o[3];
        path.style.strokeDasharray = len + ' ' + len; path.style.strokeDashoffset = len * (1 - p);
        if (p > 0 && p < 1) { var q = path.getPointAtLength(len * p); c.setAttribute('cx', q.x); c.setAttribute('cy', q.y); c.style.opacity = 1; } else c.style.opacity = 0; });
      var glow = t > T.hit ? 0.5 + 0.25 * Math.sin((t - T.hit) * 2.2) : 0.35 * clamp(rp * 3);
      L.front.style.filter = L.back.style.filter = 'drop-shadow(0 0 ' + (4 + 10 * glow) + 'px rgba(30,107,255,' + 0.9 * glow + '))';
      var zd = E.inOutS(prog(t, T.z0, T.z0 + 1.2)), zfp = E.outC(prog(t, T.zf, T.zf + 0.8));
      zOut.style.strokeDasharray = lenZ + ' ' + lenZ; zOut.style.strokeDashoffset = lenZ * (1 - zd); zOut.style.opacity = zd > 0 ? 1 - zfp * 0.9 : 0; zPoly.style.opacity = zfp;
      var sd = E.inOutS(prog(t, T.s0, T.s0 + 1.2)), sfp = E.outC(prog(t, T.sf, T.sf + 0.8));
      sOut.style.strokeDasharray = lenS + ' ' + lenS; sOut.style.strokeDashoffset = lenS * (1 - sd); sOut.style.opacity = sd > 0 ? 1 - sfp * 0.9 : 0; sPath.style.opacity = sfp;
      var ap = E.outBack(prog(t, T.acc, T.acc + 0.45)); L.acc.style.opacity = clamp(ap); L.acc.style.transformBox = 'fill-box'; L.acc.style.transformOrigin = 'center'; L.acc.style.transform = 'scale(' + Math.max(0.01, ap) + ')';
      var shx = -9999; [T.hit + 0.4, 9.3].forEach(function (s0) { var p = prog(t, s0, s0 + 1.5); if (p > 0 && p < 1) shx = lerp(VB.x - 400, VB.x + VB.width + 200, E.inOutS(p)); });
      shineG.setAttribute('x1', shx); shineG.setAttribute('x2', shx + 260); shineG.setAttribute('y1', 150); shineG.setAttribute('y2', 330);
      zSh.style.opacity = zfp; sSh.style.opacity = sfp;
      var n = letters.length, slot = (T.word1 - T.word0) / (n + 1.5);
      letters.forEach(function (el, i) { var p = E.outC(prog(t, T.word0 + i * slot, T.word0 + i * slot + slot * 2.5));
        el.style.opacity = p; el.style.transform = 'translate(0px,' + (1 - p) * 34 + 'px)'; el.style.filter = p < 1 ? 'drop-shadow(0 0 ' + 10 * (1 - p) + 'px #3FB4FF)' : 'none'; });
      var lp = E.inOutS(prog(t, T.stu0, T.stu1));
      L.lines.style.transformOrigin = midX + 'px ' + (linesBB.y + linesBB.height / 2) + 'px'; L.lines.style.transform = 'scaleX(' + Math.max(0.001, lp) + ')'; L.lines.style.opacity = clamp(lp * 3);
      var sp = E.outC(prog(t, T.stu0 + 0.3, T.stu1 + 0.3)); L.stu.style.opacity = sp; L.stu.style.transformOrigin = midX + 'px ' + (STB.y + STB.height / 2) + 'px'; L.stu.style.transform = 'scale(' + lerp(1.07, 1, sp) + ',1)';
      fc.clearRect(0, 0, W, H);
      if (t >= T.hit - 0.15) {
        var e = t - T.hit, hr = host.getBoundingClientRect(), r = box.getBoundingClientRect(), cx = r.left - hr.left + r.width / 2, cy = r.top - hr.top + r.height * 0.36, u = r.width / 1600;
        fc.save(); fc.globalCompositeOperation = 'lighter';
        var fl = e < 0 ? (e + 0.15) / 0.15 : Math.exp(-e * 4);
        if (fl > 0.01) { var gg = fc.createRadialGradient(cx, cy, 0, cx, cy, W * 0.55); gg.addColorStop(0, 'rgba(190,225,255,' + 0.55 * fl + ')'); gg.addColorStop(1, 'rgba(0,60,255,0)'); fc.fillStyle = gg; fc.fillRect(0, 0, W, H); }
        if (e > 0) { var rr = (60 + e * 900) * u, al = Math.max(0, 0.5 - e * 0.45); if (al > 0) { fc.strokeStyle = 'rgba(110,180,255,' + al + ')'; fc.lineWidth = (3 + 12 * Math.exp(-e * 3)) * Math.max(0.5, u); fc.beginPath(); fc.ellipse(cx, cy, rr, rr * 0.32, -0.31, 0, 7); fc.stroke(); } }
        fc.restore();
      }
    }

    // ---- reloj
    var END = HOLD ? T.end : DUR, cur = 0, playing = false, last = 0, raf = 0, ended = false;
    var audio = null; if (opt.sound) { audio = new Audio(opt.sound); audio.preload = 'auto'; }
    function syncAudio() { if (!audio) return; try { audio.currentTime = cur / SPEED; audio.playbackRate = SPEED; if (playing) { var p = audio.play(); if (p && p.catch) p.catch(function () {}); } else audio.pause(); } catch (e) {} }
    function tick(now) {
      if (!playing) return;
      cur += Math.min(0.1, (now - last) / 1000) * SPEED; last = now;
      if (cur >= END) {
        if (LOOP) { cur = 0; syncAudio(); }
        else { cur = END; draw(cur); playing = false; if (audio && !HOLD) audio.pause(); if (!ended) { ended = true; if (opt.onEnd) opt.onEnd(); } return; }
      }
      draw(cur); raf = requestAnimationFrame(tick);
    }
    var api = {
      play: function () { if (playing) return; if (cur >= END) { cur = 0; ended = false; } playing = true; last = performance.now(); syncAudio(); raf = requestAnimationFrame(tick); },
      pause: function () { playing = false; cancelAnimationFrame(raf); syncAudio(); },
      restart: function () { cur = 0; ended = false; playing = false; api.play(); },
      seek: function (s) { cur = clamp(s, 0, END); draw(cur); syncAudio(); },
      destroy: function () { api.pause(); if (ro) ro.disconnect(); else root.removeEventListener('resize', layout); sr.innerHTML = ''; },
      duration: END
    };
    layout();
    if (reduce) { cur = T.end; draw(cur); }                 // accesibilidad: sin animación, logo final
    else if (opt.autoplay !== false) api.play();
    return api;
  }
  root.ZentrixIntro = { mount: mount, duration: DUR };
})(typeof window !== 'undefined' ? window : this);
