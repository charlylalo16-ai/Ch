// Guion de grabación: recorre la app REAL con datos de demostración y guarda cada estado.
// Cada captura guarda también la posición (en px CSS) de los elementos que se van a "tocar".
const fs = require('fs'), path = require('path');
module.exports = async (page, shotRaw) => {
  const OUT = process.argv[3];
  const meta = {};
  let idx = 0;
  const shot = async (name, sels = {}) => {
    await page.waitForTimeout(140);
    const rects = await page.evaluate((sels) => {
      const r = {};
      for (const [k, s] of Object.entries(sels)) {
        const el = typeof s === 'string' ? document.querySelector(s) : null;
        if (el) { const b = el.getBoundingClientRect(); r[k] = [b.left + b.width / 2, b.top + b.height / 2, b.width, b.height]; }
      }
      return r;
    }, sels);
    const file = `${String(++idx).padStart(3, '0')}_${name}.png`;
    await page.screenshot({ path: path.join(OUT, file) });
    meta[name] = { file, rects };
  };
  const ev = (fn, arg) => page.evaluate(fn, arg);
  const typeInto = async (sel, text, name, every = 1, extra = {}) => {
    for (let i = 1; i <= text.length; i++) {
      await ev(([s, v]) => { const el = document.querySelector(s); el.value = v; el.focus(); el.dispatchEvent(new Event('input', { bubbles: true })); }, [sel, text.slice(0, i)]);
      if (i % every === 0 || i === text.length) await shot(`${name}_${String(i).padStart(2, '0')}`, Object.assign({ field: sel }, extra));
    }
  };

  // ---------- demo data (ficticia) ----------
  await ev(() => {
    const hoy = new Date(), d = (h) => new Date(hoy.getTime() - h * 3600e3).toISOString();
    window.DEMO = {
      avisos: [
        { id: 'a1', titulo: 'Jornada de vacunación en la plaza principal', texto: 'Este sábado de 9:00 a 14:00 h. Lleva tu cartilla de vacunación.', categoria: 'salud', destacado: true, fecha: d(3) },
        { id: 'a2', titulo: 'Mantenimiento de alumbrado en el Centro', texto: 'Se realizarán trabajos de mantenimiento en luminarias del primer cuadro de la ciudad.', categoria: 'obras', fecha: d(26) },
        { id: 'a3', titulo: 'Horario de atención en Presidencia', texto: 'Lunes a viernes de 9:00 a 15:00 h. ¡Te esperamos!', categoria: 'tramites', fecha: d(50) },
      ],
      reportes: [
        { id: 'r1', uid: 'demo', folio: 'REP-M1Q7', titulo: 'Luminaria apagada', desc: 'La luminaria de la esquina no enciende desde hace 3 días.', area: 'obras', estado: 'atendido', ubicacion: 'Centro, Quiroga', fecha: d(72) },
        { id: 'r2', uid: 'demo', folio: 'REP-M2B4', titulo: 'Fuga de agua', desc: 'Fuga en la banqueta frente al mercado.', area: 'oapas', estado: 'revision', ubicacion: 'Centro, Quiroga', fecha: d(30) },
      ],
      mensajes: [
        { de: 'ciudadano', texto: 'Hola, buenas tardes. ¿Cuándo pasa el camión de la basura por la colonia Centro?', fecha: d(1.2) },
        { de: 'area', texto: '¡Hola María! Pasa lunes, miércoles y viernes a partir de las 8:00 a.m. 🚛', fecha: d(1.1) },
        { de: 'ciudadano', texto: '¡Muchas gracias! 🙌', fecha: d(1.0) },
      ],
      'doc:config/emergencias': null,
    };
    // Dirección de demostración (la app usa Nominatim; aquí no hay red).
    window._direccionDeCoords = async () => 'Centro, Quiroga, Mich.';
    try { _direccionDeCoords = window._direccionDeCoords; } catch (e) { }
    window.confirm = () => true;
  });

  // ---------- splash ----------
  await page.waitForTimeout(600);
  await shot('splash', { card: '.splash-video-wrap' });
  await ev(() => { document.getElementById('splash').style.display = 'none'; document.getElementById('geocercaGate').style.display = 'none'; document.getElementById('app').style.display = 'block'; mostrarAuth(); });
  await page.waitForTimeout(900);
  await shot('login', { tabReg: '.auth-tab:nth-child(2)' });

  // ---------- registro ----------
  await ev(() => switchAuthTab('registro', document.querySelectorAll('.auth-tab')[1]));
  await shot('reg_empty', { name: '#regNombre' });
  await typeInto('#regNombre', 'María López', 'reg_nombre', 2);
  await typeInto('#regPass', 'quiroga24', 'reg_pass', 3);
  await typeInto('#regPassConfirm', 'quiroga24', 'reg_pass2', 3);
  await ev(() => { document.querySelector('#regTelefono').scrollIntoView({ block: 'center' }); });
  await typeInto('#regTelefono', '4431234567', 'reg_tel', 2);
  await ev(() => { const s = document.querySelector('#regGenero'); s.value = 'mujer'; s.scrollIntoView({ block: 'center' }); });
  await shot('reg_genero', { field: '#regGenero' });
  await ev(() => { const s = document.querySelector('#regLocalidad'); s.value = 'Quiroga'; });
  await shot('reg_localidad', { field: '#regLocalidad' });
  await ev(() => { document.querySelector('#btnCrearCuenta').scrollIntoView({ block: 'center' }); });
  await typeInto('#regDireccion', 'Calle Morelos, Centro', 'reg_dir', 4);
  await ev(() => { document.querySelector('#aceptaTerminos').checked = true; });
  await shot('reg_terminos', { field: '#aceptaTerminos', btn: '#btnCrearCuenta' });
  await ev(() => { const b = document.querySelector('#btnCrearCuenta'); b.style.transform = 'scale(0.97)'; b.style.filter = 'brightness(0.9)'; });
  await shot('reg_press', { btn: '#btnCrearCuenta' });
  await ev(() => { const b = document.querySelector('#btnCrearCuenta'); b.style.transform = ''; b.style.filter = ''; b.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando cuenta…'; });
  await shot('reg_creando', { btn: '#btnCrearCuenta' });

  // ---------- verificación SMS ----------
  await ev(() => {
    document.getElementById('registroForm').style.display = 'none';
    const tabs = document.querySelector('.auth-tabs'); if (tabs) tabs.style.display = 'none';
    document.getElementById('verificarTelefonoForm').style.display = 'block';
    document.getElementById('verifTelTexto').textContent = 'Te enviamos un código por SMS al 443 123 4567 para confirmar que tu número es real.';
    window.scrollTo(0, 0);
  });
  await shot('sms_empty', { field: '#codigoSMS', btn: '#btnVerificarCodigo' });
  await typeInto('#codigoSMS', '482916', 'sms', 1, { btn: '#btnVerificarCodigo' });
  await ev(() => { const b = document.querySelector('#btnVerificarCodigo'); b.innerHTML = '<i class="fas fa-check-circle"></i> ¡Teléfono verificado!'; b.style.background = '#1a7f37'; });
  await shot('sms_ok', { btn: '#btnVerificarCodigo' });

  // ---------- app: inicio ----------
  await ev(() => {
    currentUser = { uid: 'demo', email: 'maria@demo.mx', phoneNumber: '+524431234567' };
    currentUserData = { nombre: 'María López', rol: 'ciudadano', genero: 'mujer', localidad: 'Quiroga', telefono: '4431234567', telefonoVerificado: true };
    window.__demoUser = currentUser;
    mostrarMainApp();
  });
  await page.waitForTimeout(900);
  await ev(() => { document.querySelectorAll('[id*=nuncio], .anuncio-overlay').forEach(m => m.remove()); window.scrollTo(0, 0); });
  await shot('inicio_0', { sos: '#inicioSOSCard .btn-sos', navEmerg: '.nav-tab:nth-child(5)' });
  for (const y of [220, 440, 660]) { await ev((y) => window.scrollTo(0, y), y); await shot(`inicio_${y}`, { sos: '#inicioSOSCard .btn-sos' }); }

  // ---------- Alerta Mujer ----------
  await ev(() => { showSection('emergencias'); window.scrollTo(0, 0); });
  await page.waitForTimeout(400);
  await shot('emerg', { sos: '#sec-emergencias .btn-sos' });
  for (let i = 1; i <= 10; i++) {
    await ev((p) => { document.documentElement.style.setProperty('--hold-pct', p); const b = document.querySelector('#sec-emergencias .btn-sos'); b.style.transform = 'scale(0.98)'; }, i / 10);
    await shot(`hold_${String(i).padStart(2, '0')}`, { sos: '#sec-emergencias .btn-sos' });
  }
  await ev(() => { document.documentElement.style.setProperty('--hold-pct', 0); document.querySelector('#sec-emergencias .btn-sos').style.transform = ''; mostrarOverlayEnviando(); });
  await shot('alerta_enviando');
  const alerta = (estado, tipo) => ev(([estado, tipo]) => mostrarOverlayAlerta('demoAlerta', { estado, tipo, folio: 'AM-2611-0042', lat: 19.665, lng: -101.524, fecha: new Date().toISOString(), nombre: 'María López' }), [estado, tipo]);
  await alerta('enviada'); await page.waitForTimeout(300); await shot('alerta_enviada', { chip: '#alertaTipoChips .tipo-chip' });
  await alerta('recibida', 'peligro'); await page.waitForTimeout(300); await shot('alerta_recibida');
  await alerta('asignada', 'peligro'); await ev(() => toast('🚓 Personal de seguridad asignado a tu alerta')); await page.waitForTimeout(400); await shot('alerta_asignada');
  await alerta('en_atencion', 'peligro'); await ev(() => toast('🚨 Tu alerta está en atención')); await page.waitForTimeout(400); await shot('alerta_atencion');
  await ev(() => { document.getElementById('alertaActivaOverlay').classList.remove('active'); document.querySelectorAll('.toast').forEach(t => t.remove()); });

  // ---------- Reportes ----------
  await ev(() => { showSection('reportes'); window.scrollTo(0, 0); });
  await page.waitForTimeout(400);
  await shot('rep_empty', { area: '#repArea' });
  await ev(() => { const s = document.querySelector('#repArea'); s.value = s.querySelector('option[value=obras]') ? 'obras' : s.options[1].value; s.dispatchEvent(new Event('change', { bubbles: true })); });
  await shot('rep_area', { field: '#repArea' });
  await typeInto('#repTitulo', 'Bache en calle Morelos', 'rep_titulo', 4);
  await typeInto('#repDesc', 'Bache grande frente a la escuela, es peligroso para los autos y las motos.', 'rep_desc', 12);
  await typeInto('#repUbicacion', 'Calle Morelos, Centro', 'rep_ubic', 7);
  await ev(() => document.querySelector('#btnEnviarReporte').scrollIntoView({ block: 'center' }));
  await shot('rep_listo', { btn: '#btnEnviarReporte' });
  await ev(() => { const b = document.querySelector('#btnEnviarReporte'); b.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...'; });
  await shot('rep_enviando', { btn: '#btnEnviarReporte' });
  await ev(() => { const b = document.querySelector('#btnEnviarReporte'); b.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Reporte'; toast('✅ Reporte enviado · Folio REP-M3K9'); });
  await page.waitForTimeout(300);
  await shot('rep_ok');
  await ev(() => document.querySelectorAll('.toast').forEach(t => t.remove()));

  // ---------- Avisos ----------
  await ev(() => { showSection('avisos'); window.scrollTo(0, 0); });
  await page.waitForTimeout(500);
  await shot('avisos_0');
  await ev(() => window.scrollTo(0, 260)); await shot('avisos_260');

  // ---------- Camión ----------
  const pts = [[19.66305, -101.52690], [19.66380, -101.52560], [19.66455, -101.52430], [19.66530, -101.52300]];
  for (let i = 0; i < pts.length; i++) {
    await ev(([lat, lng, first]) => {
      DEMO['doc:camiones/camion_1'] = { activo: true, lat, lng, timestamp: Date.now() };
      if (first) { showSection('camion'); window.scrollTo(0, 0); }
      else escucharUbicacionCamion(1);
    }, [pts[i][0], pts[i][1], i === 0]);
    await page.waitForTimeout(i === 0 ? 1600 : 500);
    await shot(`camion_${i}`);
  }

  // ---------- Mensajes ----------
  await ev(() => { showSection('mensajes'); window.scrollTo(0, 0); });
  await page.waitForTimeout(400);
  await shot('mensajes', { seg: '#sec-mensajes [onclick*="seguridad"], #sec-mensajes .depto-btn' });
  await ev(() => { const d = (typeof DEPTOS !== 'undefined' && DEPTOS.find(x => x.id === 'obras')) || { icono: 'fa-hard-hat', color: '#002068', bg: 'rgba(0,32,104,0.1)' }; abrirChat('obras', 'Obras Públicas', d.icono, d.color, d.bg); });
  await page.waitForTimeout(500);
  await shot('chat');

  fs.writeFileSync(path.join(OUT, 'meta.json'), JSON.stringify(meta, null, 1));
  console.log('estados:', Object.keys(meta).length);
};
