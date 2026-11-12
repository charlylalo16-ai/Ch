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
        { id: 'r1', uid: 'demo', folio: 'REP-EJEMPLO1', titulo: 'Luminaria apagada', desc: 'La luminaria de la esquina no enciende por las noches.', area: 'obras', estado: 'atendido', nota: 'Luminaria reparada. ¡Gracias por reportar!', ubicacion: 'Calle de ejemplo', fecha: d(72) },
        { id: 'r2', uid: 'demo', folio: 'REP-EJEMPLO2', titulo: 'Fuga de agua en la banqueta', desc: 'Hay una fuga de agua constante frente a la tienda.', area: 'oapas', estado: 'pendiente', ubicacion: 'Calle de ejemplo', fecha: d(5) },
      ],
      directorio: [
        { id: 'd1', orden: 1, nombre: 'Presidencia Municipal', icono: 'fa-landmark', color: '#002068', telefono: '000 000 0000', horario: 'Lunes a viernes, 9:00 a 15:00 h' },
        { id: 'd2', orden: 2, nombre: 'Seguridad Pública', icono: 'fa-shield-alt', color: '#ba1a1a', telefono: '000 000 0000', horario: 'Las 24 horas' },
        { id: 'd3', orden: 3, nombre: 'OAPAS (Agua Potable)', icono: 'fa-tint', color: '#0077c8', telefono: '000 000 0000', horario: 'Lunes a viernes, 9:00 a 15:00 h' },
        { id: 'd4', orden: 4, nombre: 'Obras Públicas', icono: 'fa-hard-hat', color: '#a86a00', telefono: '000 000 0000', horario: 'Lunes a viernes, 9:00 a 15:00 h' },
        { id: 'd5', orden: 5, nombre: 'DIF Municipal', icono: 'fa-heart', color: '#e2007c', telefono: '000 000 0000', horario: 'Lunes a viernes, 9:00 a 15:00 h' },
        { id: 'd6', orden: 6, nombre: 'Tránsito Municipal', icono: 'fa-car', color: '#f6a800', telefono: '000 000 0000', horario: 'Lunes a domingo, 8:00 a 20:00 h' },
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
  await ev(() => { const s = document.querySelector('#repArea'); s.value = 'obras'; s.dispatchEvent(new Event('change', { bubbles: true })); document.querySelector('#repTitulo').value = 'Bache en la calle'; document.querySelector('#repUbicacion').value = 'Calle Morelos, Centro'; });
  await shot('03_nuevo_reporte');
  await ev(() => showSection('camion')); await page.waitForTimeout(2500); await clean(); await shot('04_camion');
  await ev(() => showSection('mensajes')); await clean(); await shot('05_mensajes');
  await ev(() => showSection('avisos')); await page.waitForTimeout(400); await clean(); await shot('06_avisos');
  await ev(() => { showSection('reportes'); document.querySelector('#repTitulo').value = ''; document.querySelector('#repUbicacion').value = ''; }); await page.waitForTimeout(500); await clean();
  await ev(() => { const el = document.getElementById('misReportes'); const card = el.closest('.card') || el; window.scrollTo(0, card.getBoundingClientRect().top + window.scrollY - 70); });
  await shot('07_seguimiento');
  await ev(() => { showSection('directorio'); if (typeof cargarDirectorio === 'function') cargarDirectorio(); }); await page.waitForTimeout(600); await clean(); await shot('08_directorio');
};
