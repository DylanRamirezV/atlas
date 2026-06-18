(function(){
  // Credenciales de ejemplo (solo cliente)
  const USERS = {
    profesor: { role: 'admin', password: '123456789', displayName: 'Profesor' },
    estudiante: { role: 'student', password: '123456789', displayName: 'Estudiante' }
  };

  function $(sel){ return document.querySelector(sel); }

  function setLoggedIn(info){
    const panel = $('#panel-admin');
    if(!panel) return;
    if(info && info.role === 'admin') {
      panel.classList.add('admin-unlocked');
      sessionStorage.setItem('adminLogged', 'admin');
      sessionStorage.setItem('user', info.user);
    } else if(info && info.role === 'student') {
      panel.classList.remove('admin-unlocked');
      sessionStorage.setItem('adminLogged', 'student');
      sessionStorage.setItem('user', info.user);
    } else {
      panel.classList.remove('admin-unlocked');
      sessionStorage.removeItem('adminLogged');
      sessionStorage.removeItem('user');
    }
    updateTopbar();
  }

  // Restaurar estado
  // Restaurar estado si existe
  const saved = sessionStorage.getItem('adminLogged');
  const savedUser = sessionStorage.getItem('user');
  if(saved && savedUser) {
    if(saved === 'admin') setLoggedIn({ role: 'admin', user: savedUser });
    else setLoggedIn({ role: 'student', user: savedUser });
  }

  const form = $('.admin-login-form');
  if(!form) return;

  form.addEventListener('submit', function(e){
    e.preventDefault();
    const user = (document.getElementById('admin-user')||{}).value.trim().toLowerCase() || '';
    const pass = (document.getElementById('admin-pass')||{}).value || '';

    const note = document.querySelector('.admin-login-form .muted-note');

    if(!user || !pass) {
      if(note) note.textContent = 'Introduce usuario y contraseña.';
      return;
    }

    const entry = USERS[user];
    if(entry && pass === entry.password) {
      setLoggedIn({ role: entry.role, user: user });
      if(note) note.textContent = entry.role === 'admin' ? 'Acceso correcto. El panel de subida está activado.' : 'Acceso correcto. Sesión de estudiante iniciada.';
      form.querySelector('button[type="submit"]').textContent = 'Cerrar sesión';
    } else {
      if(note) note.textContent = 'Credenciales incorrectas.';
    }
  });

  // Permitir cerrar sesión usando el mismo botón de submit cuando ya autenticado
  const uploadForm = document.getElementById('upload-form');
  if(uploadForm){
    uploadForm.addEventListener('submit', function(e){
      const panel = document.getElementById('panel-admin');
      if(panel && !panel.classList.contains('admin-unlocked')){
        e.preventDefault();
        alert('Debes iniciar sesión como administrador para subir archivos.');
      }
    });
  }
  
  // Actualiza la etiqueta del topbar y nombre mostrado
  function updateTopbar(){
    const tag = document.querySelector('.session-tag');
    const studentDataName = document.querySelector('.student-data span');
    const savedUser = sessionStorage.getItem('user');
    const savedRole = sessionStorage.getItem('adminLogged');
    if(savedRole === 'student'){
      if(tag) tag.textContent = 'Sesión 11-3';
      if(studentDataName) studentDataName.textContent = 'Estudiante';
    } else if(savedRole === 'admin'){
      if(tag) tag.textContent = 'Admin';
      if(studentDataName) studentDataName.textContent = 'Profesor';
    } else {
      // restaurar por si hay variables de template
      // no hacemos nada más
    }
  }
  
  // Permitir cerrar sesión si ya autenticado mediante el mismo botón
  form.addEventListener('click', function(e){
    const btn = e.target.closest('button');
    if(!btn) return;
    if(btn.textContent.trim().toLowerCase().includes('cerrar')){
      e.preventDefault();
      setLoggedIn(null);
      form.querySelector('button[type="submit"]').textContent = 'Iniciar sesión';
      const note = document.querySelector('.admin-login-form .muted-note');
      if(note) note.textContent = '';
      document.getElementById('admin-user').value = '';
      document.getElementById('admin-pass').value = '';
    }
  });
})();
