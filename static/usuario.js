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
    { nombre: "Guia de estudio", tipo: "PDF", detalle: "Semana 4", descripcion: "Material completo de la unidad 4 con conceptos clave y ejercicios prácticos. Incluye 25 páginas con ejemplos resueltos." },
    { nombre: "Actividad 2", tipo: "Entrega", detalle: "Viernes", descripcion: "Tarea grupal que debe entregarse antes del viernes 22 de junio. Valor: 15% de la nota final." },
    { nombre: "Lectura 1", tipo: "Articulo", detalle: "12 paginas", descripcion: "Artículo académico sobre metodología de investigación. Lectura obligatoria para la siguiente clase." },
    { nombre: "Video clase", tipo: "MP4", detalle: "18 min", descripcion: "Grabación de la clase del 18 de junio. Tema: Introducción a estructuras de datos. Disponible hasta fin de mes." },
    { nombre: "Rubrica de evaluacion", tipo: "PDF", detalle: "Evaluacion", descripcion: "Criterios de calificación para el proyecto final. Contiene 8 dimensiones evaluables con puntajes específicos." },
    { nombre: "Proyecto final", tipo: "Carpeta", detalle: "Activo", descripcion: "Carpeta con todos los archivos del proyecto final. Entrega: 5 de julio. Incluye plantilla y ejemplos." },
    { nombre: "Bibliografía recomendada", tipo: "Documento", detalle: "30 referencias", descripcion: "Lista de fuentes académicas recomendadas para profundizar en los temas del curso." },
    { nombre: "Solucionario", tipo: "PDF", detalle: "Ejercicios 1-20", descripcion: "Respuestas detalladas de los ejercicios de la sección 1. Solo disponible después de la entrega." },
  ];

  const institutionalFiles = [
    { id: 1, nombre: "Calendario academico 2026", tipo: "Comunicado", detalle: "Actualizado hoy", descripcion: "Fechas importantes: Receso 15-19 julio | Exámenes finales 25 julio - 5 agosto | Graduación 10 agosto" },
    { id: 2, nombre: "Normas institucionales", tipo: "PDF", detalle: "Version vigente", descripcion: "Reglamento de convivencia, código de honor, políticas de asistencia y procedimientos disciplinarios." },
    { id: 3, nombre: "Bienestar estudiantil", tipo: "Informacion", detalle: "Servicios disponibles", descripcion: "Consejería psicológica | Asesoramiento académico | Becas y ayudas | Deporte y recreación | Acceso a biblioteca 24/7" },
    { id: 4, nombre: "Horario de clases", tipo: "Documento", detalle: "Semestre 1", descripcion: "Lunes a viernes 8:00 AM - 12:30 PM y 2:00 PM - 5:30 PM. Miércoles: tutoría de 1:00 PM - 2:00 PM" },
    { id: 5, nombre: "Politica de evaluacion", tipo: "PDF", detalle: "Criterios y procedimientos", descripcion: "Detalles sobre evaluación continua, trabajos, exámenes, y cálculo final de calificaciones." },
    { id: 6, nombre: "Contactos de profesores", tipo: "Lista", detalle: "Correos y horarios", descripcion: "Directorio completo de docentes con emails y horarios de atención para dudas y tutoría." },
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
      <p class="file-card__description">${file.descripcion}</p>
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
