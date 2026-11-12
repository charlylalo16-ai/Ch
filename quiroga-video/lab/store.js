// Capturas para Google Play: 6 pantallas reales de la app con una cuenta de prueba inventada.
const fs = require('fs'), path = require('path');
module.exports = async (page) => {
  const OUT = process.argv[3];
  const ev = (fn, a) => page.evaluate(fn, a);
  const shot = async (name) => { await page.waitForTimeout(500); await page.screenshot({ path: path.join(OUT, name + '.png') }); };
  await ev(() => {
    const hoy = Date.now(), d = (h) => new Date(hoy - h * 3600e3).toISOString();
    window.DEMO = {
      avisos: [
        { id: 'a1', titulo: 'Jornada de vacunación en la plaza principal', texto: 'Este sábado de 9:00 a 14:00 h. Lleva tu cartilla de vacunación.', categoria: 'salud', destacado: true, fecha: d(3) },
        { id: 'a2', titulo: 'Mantenimiento de alumbrado público', texto: 'Se realizarán trabajos de mantenimiento en luminarias del primer cuadro.', categoria: 'obras', fecha: d(26) },
        { id: 'a3', titulo: 'Horario de atención en Presidencia', texto: 'Lunes a viernes de 9:00 a 15:00 h.', categoria: 'tramites', fecha: d(50) },
      ],
      reportes: [
        { id: 'r1', uid: 'demo', folio: 'REP-EJEMPLO1', titulo: 'Luminaria apagada (ejemplo)', desc: 'Reporte de ejemplo.', area: 'obras', estado: 'atendido', ubicacion: 'Ejemplo', fecha: d(72) },
      ],
      'doc:rutas_camion/camion_1': { nombre: 'Camión 1', colonias: [
        { nombre: 'Centro', hora: '08:00', lat: 19.6640, lng: -101.5260 },
        { nombre: 'Col. Ejemplo Norte', hora: '08:30', lat: 19.6685, lng: -101.5215 },
        { nombre: 'Col. Ejemplo Oriente', hora: '09:00', lat: 19.6655, lng: -101.5165 },
        { nombre: 'Col. Ejemplo Sur', hora: '09:30', lat: 19.6600, lng: -101.5200 } ] },
    };
    window._direccionDeCoords = async () => 'Quiroga, Mich.'; window.confirm = () => true;
  });
  await page.waitForTimeout(400);
  await ev(() => {
    document.getElementById('splash').style.display = 'none'; document.getElementById('geocercaGate').style.display = 'none'; document.getElementById('app').style.display = 'block';
    currentUser = { uid: 'demo', email: 'prueba@ejemplo.com', phoneNumber: '+520000000000' };
    currentUserData = { nombre: 'María Prueba', rol: 'ciudadano', genero: 'mujer', localidad: 'Quiroga', telefono: '0000000000', telefonoVerificado: true };
    window.__demoUser = currentUser; mostrarMainApp();
  });
  await page.waitForTimeout(1200);
  const clean = () => ev(() => { document.querySelectorAll('[id*=nuncio], .anuncio-overlay, .toast').forEach(m => m.remove()); window.scrollTo(0, 0); });
  await clean(); await shot('01_inicio');
  await ev(() => showSection('emergencias')); await clean(); await shot('02_alerta_mujer');
  await ev(() => showSection('reportes')); await clean();
  await ev(() => { const s = document.querySelector('#repArea'); s.value = 'obras'; s.dispatchEvent(new Event('change', { bubbles: true })); document.querySelector('#repTitulo').value = 'Bache en la calle'; });
  await shot('03_nuevo_reporte');
  await ev(() => showSection('avisos')); await page.waitForTimeout(400); await clean(); await shot('04_avisos');
  await ev(() => showSection('camion')); await page.waitForTimeout(2500); await clean(); await shot('05_camion');
  await ev(() => showSection('mensajes')); await clean(); await shot('06_mensajes');
};
