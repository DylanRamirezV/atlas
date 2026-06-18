(function(){
  const role = localStorage.getItem('atlasUserRole');
  const userName = localStorage.getItem('atlasUserName') || 'Usuario';
  const description = document.getElementById('usuario-description');
  const content = document.getElementById('usuario-content');
  const roleLabel = document.getElementById('usuario-role');

  function createCard(title, text) {
    const card = document.createElement('article');
    card.className = 'usuario-card';
    card.innerHTML = `<h2>${title}</h2><p>${text}</p>`;
    return card;
  }

  if(!role) {
    if(description) description.textContent = 'No se encontró un rol en el almacenamiento local. Inicia sesión nuevamente.';
    return;
  }

  if(roleLabel) roleLabel.textContent = `Rol: ${role === 'professor' ? 'Profesor' : 'Estudiante'}`;
  if(description) description.textContent = `Vista de ${role === 'professor' ? 'profesor' : 'estudiante'} activada.`;

  if(role === 'student') {
    content.innerHTML = '';
    content.appendChild(createCard('Tu agenda académica', 'Revisa tus tareas, archivos y recursos sin ver opciones de administrador.'));
    content.appendChild(createCard('Novedades', 'Encuentra los contenidos más relevantes organizados en forma de revista.'));
    content.appendChild(createCard('Rutina de estudio', 'Céntrate en tus materias con un diseño limpio y directo.'));
  } else if(role === 'professor') {
    content.innerHTML = '';
    content.appendChild(createCard('Gestión docente', 'Administra clases, recursos y notas con un estilo profesional.'));
    content.appendChild(createCard('Publicaciones', 'Agrega y revisa materiales sin mezclar con el panel de administrador.'));
    content.appendChild(createCard('Análisis rápido', 'Consulta los elementos clave del curso en una única vista editorial.'));
  }
})();
