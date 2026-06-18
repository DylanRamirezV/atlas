(function(){
  // Credenciales de ejemplo (solo cliente)
  const ADMIN_USER = 'profesor';
  const ADMIN_PASS = 'administrador uno';

  function $(sel){ return document.querySelector(sel); }

  function setLoggedIn(on){
    const panel = $('#panel-admin');
    if(!panel) return;
    if(on) {
      panel.classList.add('admin-unlocked');
      sessionStorage.setItem('adminLogged', '1');
    } else {
      panel.classList.remove('admin-unlocked');
      sessionStorage.removeItem('adminLogged');
    }
  }

  // Restaurar estado
  if(sessionStorage.getItem('adminLogged') === '1') setLoggedIn(true);

  const form = $('.admin-login-form');
  if(!form) return;

  form.addEventListener('submit', function(e){
    e.preventDefault();
    const user = (document.getElementById('admin-user')||{}).value || '';
    const pass = (document.getElementById('admin-pass')||{}).value || '';

    const note = document.querySelector('.admin-login-form .muted-note');

    if(user.trim() === ADMIN_USER && pass === ADMIN_PASS) {
      setLoggedIn(true);
      if(note) note.textContent = 'Acceso correcto. El panel de subida está activado.';
      form.querySelector('button[type="submit"]').textContent = 'Cerrrar sesión';
    } else if(user === '' && pass === '') {
      if(note) note.textContent = 'Introduce las credenciales.';
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
})();
