// Firebase simulado: la app real corre igual, pero no se conecta a ningún
// servidor ni toca datos reales. Las colecciones devuelven DEMO (si existe) o vacío.
(function () {
  window.DEMO = window.DEMO || {};
  const snapOf = (docs) => ({
    exists: false, empty: !docs.length, size: docs.length,
    docs: docs.map(d => ({ id: d.id, exists: true, data: () => d, ref: mk('ref') })),
    forEach(cb) { this.docs.forEach(cb); }, docChanges: () => [], data: () => ({}),
  });
  const docSnap = (d) => d ? { id: d.id || 'demo', exists: true, data: () => d, ref: mk('ref') } : { exists: false, data: () => undefined, id: 'demo' };
  function mk(path) {
    const fn = function () {};
    return new Proxy(fn, {
      get(t, p) {
        if (p === 'then') return undefined;
        if (p === Symbol.toPrimitive) return () => path;
        if (p === 'toString') return () => path;
        if (p === 'collection') return (name) => mk('col:' + name);
        if (p === 'doc') return (id) => mk(path.replace(/^col:/, 'doc:') + '/' + (id || 'nuevo'));
        if (p === 'id') return 'demo' + Math.floor(Math.random() * 1e6);
        if (p === 'get') return () => {
          if (path.startsWith('col:')) { const n = path.slice(4).split('/')[0]; return Promise.resolve(snapOf(DEMO[n] || [])); }
          if (path.startsWith('doc:')) { const n = path.slice(4); return Promise.resolve(docSnap(DEMO['doc:' + n])); }
          return Promise.resolve(snapOf([]));
        };
        if (p === 'onSnapshot') return (cb) => {
          setTimeout(() => {
            try {
              if (path.startsWith('col:')) { const n = path.slice(4).split('/')[0]; cb(snapOf(DEMO[n] || [])); }
              else if (path.startsWith('doc:')) cb(docSnap(DEMO['doc:' + path.slice(4)]));
              else cb(snapOf([]));
            } catch (e) { }
          }, 0);
          return () => { };
        };
        if (['add', 'set', 'update', 'delete', 'commit', 'signOut', 'requestPermission', 'deleteToken', 'enablePersistence', 'settings', 'useEmulator'].includes(p)) return () => Promise.resolve({ id: 'demo' });
        if (['where', 'orderBy', 'limit', 'startAfter', 'endBefore', 'limitToLast', 'collectionGroup'].includes(p)) return () => mk(path);
        return mk(path + '.' + String(p));
      },
      apply() { return mk(path + '()'); },
      construct() { return mk(path + '#new'); },
    });
  }
  const authCbs = [];
  const auth = new Proxy({}, {
    get(t, p) {
      if (p === 'currentUser') return window.__demoUser || null;
      if (p === 'onAuthStateChanged') return (cb) => { authCbs.push(cb); setTimeout(() => cb(window.__demoUser || null), 0); return () => { }; };
      if (p === 'then') return undefined;
      return mk('auth.' + String(p));
    },
  });
  window.__fireAuth = (user) => { window.__demoUser = user; authCbs.forEach(cb => { try { cb(user); } catch (e) { } }); };
  const firebase = new Proxy(function () { }, {
    get(t, p) {
      if (p === 'auth') return Object.assign(() => auth, { RecaptchaVerifier: function () { return mk('recaptcha'); }, GoogleAuthProvider: function () { return mk('gp'); }, PhoneAuthProvider: mk('PhoneAuthProvider') });
      if (p === 'firestore') return Object.assign(() => mk('db'), { FieldValue: mk('FieldValue'), Timestamp: { now: () => ({ toDate: () => new Date(), toMillis: () => Date.now(), seconds: Date.now() / 1000 }), fromDate: (d) => ({ toDate: () => d, toMillis: () => +d, seconds: +d / 1000 }) }, GeoPoint: function (a, b) { return { latitude: a, longitude: b }; } });
      if (p === 'messaging') return Object.assign(() => mk('messaging'), { isSupported: () => false });
      if (p === 'initializeApp') return () => mk('app');
      if (p === 'apps') return [mk('app')];
      if (p === 'then') return undefined;
      return mk('firebase.' + String(p));
    },
  });
  window.firebase = firebase;
})();
