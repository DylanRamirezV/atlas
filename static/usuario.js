(function(){
  const role = localStorage.getItem('atlasUserRole');
  const userName = localStorage.getItem('atlasUserName') || 'Usuario';
  const description = document.getElementById('usuario-description');
  const content = document.getElementById('usuario-content');
  const roleLabel = document.getElementById('usuario-role');
  const uploadSection = document.getElementById('upload-section');
  const searchInput = document.getElementById('search-input');

  // Datos de archivos (sincronizados con main.py)
  const uploadedFiles = [
    { nombre: "Guia de estudio", tipo: "PDF", detalle: "Semana 4" },
    { nombre: "Actividad 2", tipo: "Entrega", detalle: "Viernes" },
    { nombre: "Lectura 1", tipo: "Articulo", detalle: "12 paginas" },
    { nombre: "Video clase", tipo: "MP4", detalle: "18 min" },
    { nombre: "Rubrica", tipo: "PDF", detalle: "Evaluacion" },
    { nombre: "Proyecto final", tipo: "Carpeta", detalle: "Activo" },
  ];

  const institutionalFiles = [
    { id: 1, nombre: "Calendario academico", tipo: "Comunicado", detalle: "Actualizado hoy" },
    { id: 2, nombre: "Normas institucionales", tipo: "PDF", detalle: "Version vigente" },
    { id: 3, nombre: "Bienestar estudiantil", tipo: "Informacion", detalle: "Servicios disponibles" },
  ];

  function createFileCard(file) {
    const card = document.createElement('article');
    card.className = 'file-card';
    card.innerHTML = `
      <div class="file-card__header">
        <h3>${file.nombre}</h3>
        <span class="file-type">${file.tipo}</span>
      </div>
      <p class="file-card__detail">${file.detalle}</p>
    `;
    card.dataset.searchText = `${file.nombre} ${file.tipo} ${file.detalle}`.toLowerCase();
    return card;
  }

  function renderFiles(files, title) {
    const section = document.createElement('section');
    section.className = 'files-section';
    const heading = document.createElement('h2');
    heading.textContent = title;
    section.appendChild(heading);
    
    const container = document.createElement('div');
    container.className = 'files-container';
    files.forEach(file => {
      container.appendChild(createFileCard(file));
    });
    section.appendChild(container);
    return section;
  }

  if(!role) {
    if(description) description.textContent = 'No se encontró un rol en el almacenamiento local. Inicia sesión nuevamente.';
    return;
  }

  const normalizedRole = role === 'admin' ? 'professor' : role;
  if(roleLabel) roleLabel.textContent = `Rol: ${normalizedRole === 'professor' ? 'Profesor' : 'Estudiante'}`;
  if(description) description.textContent = `Vista de ${normalizedRole === 'professor' ? 'profesor' : 'estudiante'} activada.`;

  content.innerHTML = '';

  if(normalizedRole === 'student') {
    content.appendChild(renderFiles(uploadedFiles, 'Tus recursos académicos'));
    content.appendChild(renderFiles(institutionalFiles, 'Información institucional'));
  } else if(normalizedRole === 'professor') {
    if(uploadSection) uploadSection.style.display = 'block';
    content.appendChild(renderFiles(uploadedFiles, 'Archivos compartidos'));
    content.appendChild(renderFiles(institutionalFiles, 'Información institucional'));
  }

  // Funcionalidad de búsqueda
  if(searchInput) {
    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.toLowerCase();
      const cards = document.querySelectorAll('.file-card');
      cards.forEach(card => {
        const searchText = card.dataset.searchText;
        if(searchText.includes(query)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // Manejo de subida de archivos para profesor
  const uploadForm = document.getElementById('upload-form');
  if(uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const fileInput = document.getElementById('file-input');
      if(!fileInput.files.length) return;
      
      const formData = new FormData();
      formData.append('archivo', fileInput.files[0]);
      
      try {
        const response = await fetch('/admin/upload', {
          method: 'POST',
          body: formData
        });
        if(response.ok) {
          alert('Archivo subido exitosamente');
          fileInput.value = '';
          // Aquí se podría refrescar la lista de archivos
        } else {
          alert('Error al subir el archivo');
        }
      } catch(err) {
        console.error('Error:', err);
        alert('Error al subir el archivo');
      }
    });
  }
})();
