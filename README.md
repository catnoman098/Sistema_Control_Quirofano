Sistema de Control de Infecciones en Quirófanos

Este repositorio contiene el proyecto desarrollado en Python para simular y monitorear las variables
ambientales (temperatura, humedad y presión diferencial) de varios quirófanos en tiempo real,
teniendo en cuenta la problematica de las IASS en la salud. A continuación se presenta:

- Una descripción detallada del entorno
- Las librerías utilizadas
- La funcionalidad de cada sección del código
- Archivos incluidos para un repositorio completo.

1. ENTORNO DE DESARROLLO
   
  - Lenguaje y versión: Python 3.9\ (Recomendado: última versión de la serie 3.9 para garantizar compatibilidad con PyQt5 y Matplotlib).
  - Entorno virtual: creado con python3.9 -m venv venv.
  - Activación del entorno: En Windows: venv\\Scripts\\activate
  - En Linux/macOS: source venv/bin/activate
  - Instalación de dependencias: pip install -r requirements.txt

2. LIBRERIAS USADAS

Módulos estándar de Python:

- sys : Control de la ejecución de la aplicación.
- random : Generación de valores simulados aleatorios.
- datetime : Gestión de fechas y horas.

PyQt5 (Interfaz Gráfica)

- PyQt5.QtWidgets : Controles y contenedores ( QApplication , QMainWindow , QWidget , 
QLabel , QPushButton , QFrame , QTabWidget , QGroupBox , QComboBox , 
QVBoxLayout , QHBoxLayout , QGridLayout , QMessageBox ).

- PyQt5.QtCore : Clases de núcleo ( QTimer , Qt , QThread , pyqtSignal ).
- PyQt5.QtGui : Estilos y recursos gráficos ( QFont , QColor , QPalette , QIcon , 
QPixmap ).

Matplotlib (Gráficas)

- matplotlib.pyplot y matplotlib.figure.Figure : Creación de figuras y ejes.
- matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg : Lienzo para embeber
gráficos en Qt.
- matplotlib.dates : Formateo de fechas en el eje X.

3. EXPLICACICÓN DETALLADA DEL CÓDIGO
   
En primer lugar, se realiza la configuración Global de Estilos y Rangos, luego se
define paleta de colores y rangos recomendados para cada variable (temperatura, humedad y presión).
A continuación se mostrara de forma detallada el funcionamiento de cada clase dentro del código.

Clase **SensorSimulado**

Extiende QThread para simular la lectura de sensores en segundo plano.
Usa la señal actualizar_datos para enviar un diccionario con valores actuales e historiales.
Simula valores dentro o fuera de rango según el estado del quirófano y genera anomalías
ocasionales.
Mantiene históricos y emite datos cada 2 segundos.

Clase **GraficaMonitoreo**

Hereda FigureCanvas para insertar gráficos.
Crea tres subplots (temperatura, humedad, presión) y actualiza datos en tiempo real.
Configura ejes, títulos y áreas seguras.

Clase **PanelQuirofano**

Hereda QFrame , representa un módulo de control para un quirófano.
Muestra valores actuales y un indicador de estado (verde/rojo).
Incluye botón para cambiar entre “En uso” y “Disponible”.
Actualiza la interfaz al recibir nuevas mediciones y muestra alertas cuando hay anomalías.

Clase **PestañaVisualizacion**

Hereda QWidget y muestra datos detallados de un quirófano seleccionado.
Incluye encabezado con reloj, selector de quirófano, indicadores, recomendaciones y gráficas
actualizadas.
Métodos para cambiar de quirófano y refrescar datos en la gráfica.

Clase **PestañaGeneral**

Hereda QWidget y muestra una vista general de todos los quirófanos en una cuadrícula.
Registra y muestra alertas recientes en un panel dedicado.

Clase **VentanaPrincipal**

Hereda QMainWindow y contiene un QTabWidget con dos pestañas:
Vista General ( PestañaGeneral ).
Visualización Detallada ( PestañaVisualizacion ).
