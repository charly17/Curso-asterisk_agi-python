# Recursos y Material de Apoyo

Listado de materiales descargables y referencias técnicas encontradas en el curso Asterisk Developer con Python.

## Documentos y Enlaces
- **Manual de Instalación de Docker (PDF):** [Abrir Recurso](https://training.techxpert.guru/mod/resource/view.php?id=1320)
- **Instalación de Docker en Ubuntu (Guía):** [Ver Guía](https://training.techxpert.guru/mod/page/view.php?id=1691)
- **Proyecto Docker en Github:** [Repositorio Base](https://training.techxpert.guru/mod/url/view.php?id=1321)
- **Asterisk Developer con Python - Diapositivas:** [Ver Diapositivas](https://training.techxpert.guru/mod/resource/view.php?id=1345)

## Resumen de Contenido: Diapositivas del Curso
A continuación, se presenta un extracto de los puntos clave tratados en las diapositivas:

### Introducción a Interfaces de Control
Asterisk permite la integración con lenguajes externos mediante tres interfaces principales:
1. **AGI (Asterisk Gateway Interface):** Ejecución de scripts externos síncronos.
2. **AMI (Asterisk Manager Interface):** Monitoreo y control de eventos del sistema.
3. **ARI (Asterisk REST Interface):** Control programático de canales y puentes mediante REST y WebSockets.

### Foco en AGI (Asterisk Gateway Interface)
- **Funcionamiento:** Actúa como una interfaz síncrona entre el Dialplan y un programa externo.
- **Capacidades:**
  - Manipulación de canales.
  - Ejecución de funciones de Asterisk desde el script.
  - Comunicación mediante STDIN/STDOUT o Sockets (FastAGI).
- **Ventajas:** Facilidad de uso y versatilidad para integrar lógica compleja que el Dialplan por sí solo no puede manejar eficientemente.

---
*Este material sirve como base para tus cuadernos de NotebookLM y práctica con Antigravity.*
