import sys  
import random
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QPushButton, QComboBox,
                            QFrame, QTabWidget, QGroupBox, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Configuración global de estilos
COLOR_PRINCIPAL = "#2C3E50"
COLOR_SECUNDARIO = "#ECF0F1"
COLOR_ACENTO = "#3498DB"
COLOR_ALERTA = "#E74C3C"
COLOR_OK = "#2ECC71"
COLOR_WARNING = "#F39C12"

# Rangos seguros para las variables
RANGO_TEMPERATURA = (18.0, 24.0)  # °C
RANGO_HUMEDAD = (30.0, 60.0)      # %
RANGO_PRESION = (10.0, 20.0)      # Pa (presión positiva)

# Clase para simular sensores y generar datos
class SensorSimulado(QThread):
    actualizar_datos = pyqtSignal(dict)

    def __init__(self, quirofano_id):
        super().__init__()
        self.quirofano_id = quirofano_id
        self.running = True
        self.en_uso = False

        # Inicializar historiales con valores aleatorios dentro del rango
        self.historial_temperatura = []
        self.historial_humedad = []
        self.historial_presion = []
        self.timestamps = []

        # Generar datos iniciales
        for i in range(30):
            self.historial_temperatura.append(random.uniform(RANGO_TEMPERATURA[0] + 1, RANGO_TEMPERATURA[1] - 1))
            self.historial_humedad.append(random.uniform(RANGO_HUMEDAD[0] + 5, RANGO_HUMEDAD[1] - 5))
            self.historial_presion.append(random.uniform(RANGO_PRESION[0] + 2, RANGO_PRESION[1] - 2))
            # Añadir timestamps pasados
            self.timestamps.append(datetime.now().timestamp() - (30 - i) * 10)

    def run(self):
        while self.running:
            # Generar nuevos valores con pequeñas variaciones aleatorias
            if self.en_uso:
                # Mayor variabilidad cuando está en uso
                temp = self.historial_temperatura[-1] + random.uniform(-0.5, 0.5)
                hum = self.historial_humedad[-1] + random.uniform(-2.0, 2.0)
                pres = self.historial_presion[-1] + random.uniform(-0.8, 0.8)
            else:
                # Menor variabilidad cuando no está en uso
                temp = self.historial_temperatura[-1] + random.uniform(-0.2, 0.2)
                hum = self.historial_humedad[-1] + random.uniform(-0.5, 0.5)
                pres = self.historial_presion[-1] + random.uniform(-0.3, 0.3)

                # Tendencia a volver a valores seguros cuando no está en uso
                if temp < RANGO_TEMPERATURA[0] + 1:
                    temp += random.uniform(0, 0.3)
                elif temp > RANGO_TEMPERATURA[1] - 1:
                    temp -= random.uniform(0, 0.3)

                if hum < RANGO_HUMEDAD[0] + 5:
                    hum += random.uniform(0, 1.0)
                elif hum > RANGO_HUMEDAD[1] - 5:
                    hum -= random.uniform(0, 1.0)

                if pres < RANGO_PRESION[0] + 2:
                    pres += random.uniform(0, 0.5)
                elif pres > RANGO_PRESION[1] - 2:
                    pres -= random.uniform(0, 0.5)

            # Simular ocasionalmente valores fuera de rango (solo si está en uso)
            if self.en_uso and random.random() < 0.05:  # 5% de probabilidad de anomalías
                anomalia = random.choice(['temp', 'hum', 'pres'])
                if anomalia == 'temp':
                    temp = random.choice([
                        random.uniform(RANGO_TEMPERATURA[0] - 3, RANGO_TEMPERATURA[0] - 0.1),
                        random.uniform(RANGO_TEMPERATURA[1] + 0.1, RANGO_TEMPERATURA[1] + 3)
                    ])
                elif anomalia == 'hum':
                    hum = random.choice([
                        random.uniform(RANGO_HUMEDAD[0] - 10, RANGO_HUMEDAD[0] - 0.1),
                        random.uniform(RANGO_HUMEDAD[1] + 0.1, RANGO_HUMEDAD[1] + 10)
                    ])
                elif anomalia == 'pres':
                    pres = random.choice([
                        random.uniform(RANGO_PRESION[0] - 5, RANGO_PRESION[0] - 0.1),
                        random.uniform(RANGO_PRESION[1] + 0.1, RANGO_PRESION[1] + 5)
                    ])

            # Actualizar historiales
            self.historial_temperatura.append(temp)
            self.historial_humedad.append(hum)
            self.historial_presion.append(pres)
            self.timestamps.append(datetime.now().timestamp())

            # Mantener solo los últimos 60 registros
            if len(self.historial_temperatura) > 60:
                self.historial_temperatura.pop(0)
                self.historial_humedad.pop(0)
                self.historial_presion.pop(0)
                self.timestamps.pop(0)

            # Emitir los datos actualizados
            datos = {
                'temperatura': temp,
                'humedad': hum,
                'presion': pres,
                'historial_temperatura': self.historial_temperatura.copy(),
                'historial_humedad': self.historial_humedad.copy(),
                'historial_presion': self.historial_presion.copy(),
                'timestamps': self.timestamps.copy(),
                'en_uso': self.en_uso
            }
            self.actualizar_datos.emit(datos)

            # Esperar antes de la próxima actualización (2 segundos)
            self.msleep(2000)

    def detener(self):
        self.running = False
        self.wait()

    def cambiar_estado(self, en_uso):
        self.en_uso = en_uso

# Canvas personalizado para gráficas
class GraficaMonitoreo(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)

        # Subfiguras para temperatura, humedad y presión
        self.ax1 = self.fig.add_subplot(311)  # Temperatura
        self.ax2 = self.fig.add_subplot(312)  # Humedad
        self.ax3 = self.fig.add_subplot(313)  # Presión

        # Configuración visual de los ejes
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.tick_params(labelsize=8)

        # Títulos y etiquetas
        self.ax1.set_title('Temperatura (°C)', fontsize=9, fontweight='bold')
        self.ax2.set_title('Humedad (%)', fontsize=9, fontweight='bold')
        self.ax3.set_title('Presión Diferencial (Pa)', fontsize=9, fontweight='bold')
        self.ax3.set_xlabel('Tiempo', fontsize=8)

        # Establecer colores
        self.fig.patch.set_facecolor('#f0f0f0')
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#f8f8f8')

        super().__init__(self.fig)
        self.setParent(parent)

        # Inicializar líneas vacías
        self.line_temp, = self.ax1.plot([], [], lw=2, color=COLOR_ACENTO)
        self.line_hum, = self.ax2.plot([], [], lw=2, color=COLOR_ACENTO)
        self.line_pres, = self.ax3.plot([], [], lw=2, color=COLOR_ACENTO)

        # Áreas para rangos seguros
        self.ax1.axhspan(RANGO_TEMPERATURA[0], RANGO_TEMPERATURA[1], alpha=0.2, color=COLOR_OK)
        self.ax2.axhspan(RANGO_HUMEDAD[0], RANGO_HUMEDAD[1], alpha=0.2, color=COLOR_OK)
        self.ax3.axhspan(RANGO_PRESION[0], RANGO_PRESION[1], alpha=0.2, color=COLOR_OK)

        # Inicializar límites
        self.actualizar_limites()

    def actualizar_limites(self):
        self.ax1.set_ylim(RANGO_TEMPERATURA[0] - 5, RANGO_TEMPERATURA[1] + 5)
        self.ax2.set_ylim(RANGO_HUMEDAD[0] - 15, RANGO_HUMEDAD[1] + 15)
        self.ax3.set_ylim(RANGO_PRESION[0] - 7, RANGO_PRESION[1] + 7)

    def actualizar_datos(self, timestamps, temp, hum, pres):
        # Convertir timestamps a datetime para el eje x
        fechas = [datetime.fromtimestamp(ts) for ts in timestamps]

        # Actualizar datos en las gráficas
        self.line_temp.set_data(fechas, temp)
        self.line_hum.set_data(fechas, hum)
        self.line_pres.set_data(fechas, pres)

        # Ajustar límites del eje x automáticamente
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_xlim(min(fechas), max(fechas))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Actualizar el lienzo
        self.fig.canvas.draw()

# Panel que muestra el estado de un quirófano
class PanelQuirofano(QFrame):
    def __init__(self, quirofano_id, parent=None, ventana_principal=None):
        super().__init__(parent)
        self.quirofano_id = quirofano_id
        self.en_uso = False
        self.alertas_activas = {'temperatura': False, 'humedad': False, 'presion': False}
        self.ventana_principal = ventana_principal # Referencia a la ventana principal

        # Crear sensor simulado
        self.sensor = SensorSimulado(quirofano_id)
        self.sensor.actualizar_datos.connect(self.actualizar_panel)
        self.sensor.start()

        # Configurar apariencia del marco
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet(f"""
            PanelQuirofano {{
                background-color: {COLOR_SECUNDARIO};
                border: 2px solid {COLOR_PRINCIPAL};
                border-radius: 5px;
            }}
        """)

        # Crear layout
        layout = QVBoxLayout(self)

        # Título del quirófano
        self.titulo = QLabel(f"Quirófano {quirofano_id}")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setFont(QFont("Arial", 14, QFont.Bold))
        self.titulo.setStyleSheet(f"color: {COLOR_PRINCIPAL};")
        layout.addWidget(self.titulo)

        # Estado del quirófano
        estado_layout = QHBoxLayout()
        estado_layout.addWidget(QLabel("Estado:"))
        self.lbl_estado = QLabel("Disponible")
        self.lbl_estado.setStyleSheet(f"font-weight: bold; color: {COLOR_OK};")
        estado_layout.addWidget(self.lbl_estado)
        estado_layout.addStretch()

        # Botón para cambiar estado
        self.btn_cambiar_estado = QPushButton("En uso")
        self.btn_cambiar_estado.setCheckable(True)
        self.btn_cambiar_estado.clicked.connect(self.cambiar_estado)
        self.btn_cambiar_estado.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRINCIPAL};
                color: white;
                border-radius: 3px;
                padding: 5px;
            }}
            QPushButton:checked {{
                background-color: {COLOR_ALERTA};
            }}
        """)
        estado_layout.addWidget(self.btn_cambiar_estado)
        layout.addLayout(estado_layout)

        # Separador
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setFrameShadow(QFrame.Sunken)
        layout.addWidget(linea)

        # Variables monitoreadas
        variables_layout = QGridLayout()

        # Temperatura
        variables_layout.addWidget(QLabel("Temperatura:"), 0, 0)
        self.lbl_temperatura = QLabel("22.0 °C")
        self.lbl_temperatura.setFont(QFont("Arial", 10, QFont.Bold))
        variables_layout.addWidget(self.lbl_temperatura, 0, 1)

        # Humedad
        variables_layout.addWidget(QLabel("Humedad:"), 1, 0)
        self.lbl_humedad = QLabel("45.0 %")
        self.lbl_humedad.setFont(QFont("Arial", 10, QFont.Bold))
        variables_layout.addWidget(self.lbl_humedad, 1, 1)

        # Presión
        variables_layout.addWidget(QLabel("Presión:"), 2, 0)
        self.lbl_presion = QLabel("15.0 Pa")
        self.lbl_presion.setFont(QFont("Arial", 10, QFont.Bold))
        variables_layout.addWidget(self.lbl_presion, 2, 1)

        layout.addLayout(variables_layout)

        # Círculo indicador de estado general
        self.indicador_layout = QHBoxLayout()
        self.indicador_layout.addStretch()
        self.lbl_indicador = QLabel()
        self.lbl_indicador.setFixedSize(15, 15)
        self.lbl_indicador.setStyleSheet(f"""
            background-color: {COLOR_OK};
            border-radius: 7px;
        """)
        self.indicador_layout.addWidget(self.lbl_indicador)
        self.indicador_layout.addStretch()
        layout.addLayout(self.indicador_layout)

        # Ajustar espaciados
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

    def cambiar_estado(self):
        self.en_uso = self.btn_cambiar_estado.isChecked()
        if self.en_uso:
            self.lbl_estado.setText("En uso")
            self.lbl_estado.setStyleSheet(f"font-weight: bold; color: {COLOR_ALERTA};")
            self.btn_cambiar_estado.setText("Liberar")
        else:
            self.lbl_estado.setText("Disponible")
            self.lbl_estado.setStyleSheet(f"font-weight: bold; color: {COLOR_OK};")
            self.btn_cambiar_estado.setText("En uso")

        # Actualizar sensor
        self.sensor.cambiar_estado(self.en_uso)

    def actualizar_panel(self, datos):
        temperatura = datos['temperatura']
        humedad = datos['humedad']
        presion = datos['presion']

        # Formatear valores con 1 decimal
        self.lbl_temperatura.setText(f"{temperatura:.1f} °C")
        self.lbl_humedad.setText(f"{humedad:.1f} %")
        self.lbl_presion.setText(f"{presion:.1f} Pa")

        # Verificar rangos y actualizar colores
        self.alertas_activas = {
            'temperatura': not (RANGO_TEMPERATURA[0] <= temperatura <= RANGO_TEMPERATURA[1]),
            'humedad': not (RANGO_HUMEDAD[0] <= humedad <= RANGO_HUMEDAD[1]),
            'presion': not (RANGO_PRESION[0] <= presion <= RANGO_PRESION[1])
        }

        # Actualizar color de los valores
        self.lbl_temperatura.setStyleSheet(
            f"color: {'red' if self.alertas_activas['temperatura'] else 'black'}; font-weight: bold;"
        )
        self.lbl_humedad.setStyleSheet(
            f"color: {'red' if self.alertas_activas['humedad'] else 'black'}; font-weight: bold;"
        )
        self.lbl_presion.setStyleSheet(
            f"color: {'red' if self.alertas_activas['presion'] else 'black'}; font-weight: bold;"
        )

        # Actualizar indicador general
        if any(self.alertas_activas.values()):
            self.lbl_indicador.setStyleSheet(f"""
                background-color: {COLOR_ALERTA};
                border-radius: 7px;
            """)

            # Mostrar alerta si hay algún problema
            if self.en_uso and any(self.alertas_activas.values()):
                variables_problema = []
                if self.alertas_activas['temperatura']:
                    variables_problema.append("temperatura")
                if self.alertas_activas['humedad']:
                    variables_problema.append("humedad")
                if self.alertas_activas['presion']:
                    variables_problema.append("presión")

                # Usar la referencia a la ventana principal para mostrar la alerta
                if self.ventana_principal:
                    self.ventana_principal.mostrar_alerta(
                        self.quirofano_id,
                        ", ".join(variables_problema)
                    )
        else:
            self.lbl_indicador.setStyleSheet(f"""
                background-color: {COLOR_OK};
                border-radius: 7px;
            """)

# Pestaña de visualización detallada
class PestañaVisualizacion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # La referencia a los paneles de quirófanos se asignará después de la inicialización
        self.paneles_quirofano = None

        # Layout principal
        layout = QVBoxLayout(self)

        # Encabezado
        header_layout = QHBoxLayout()

        # Ícono médico (simulado con un label)
        icono_label = QLabel()
        icono_label.setFixedSize(64, 64)
        icono_label.setStyleSheet(f"""
            background-color: {COLOR_ACENTO};
            border-radius: 32px;
            color: white;
            font-size: 30px;
            font-weight: bold;
        """)
        icono_label.setAlignment(Qt.AlignCenter)
        icono_label.setText("🏥")
        header_layout.addWidget(icono_label)

        # Título principal
        titulo_principal = QLabel("Sistema de Control de Infecciones en Quirófano")
        titulo_principal.setFont(QFont("Arial", 18, QFont.Bold))
        titulo_principal.setStyleSheet(f"color: {COLOR_PRINCIPAL};")
        titulo_principal.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo_principal, 1)

        # Fecha y hora
        self.lbl_datetime = QLabel()
        self.actualizar_datetime()
        self.lbl_datetime.setFont(QFont("Arial", 10))
        self.lbl_datetime.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.lbl_datetime)

        # Timer para actualizar fecha y hora
        self.timer_datetime = QTimer(self)
        self.timer_datetime.timeout.connect(self.actualizar_datetime)
        self.timer_datetime.start(1000)  # actualiza cada segundo

        layout.addLayout(header_layout)

        # Panel de control
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_frame.setStyleSheet(f"""
            background-color: {COLOR_SECUNDARIO};
            border-radius: 5px;
            padding: 10px;
        """)
        control_layout = QHBoxLayout(control_frame)

        # Selector de quirófano
        control_layout.addWidget(QLabel("Seleccionar Quirófano:"))
        self.combo_quirofano = QComboBox()
        self.combo_quirofano.addItems([f"Quirófano {i+1}" for i in range(6)])
        self.combo_quirofano.setCurrentIndex(0)
        self.combo_quirofano.currentIndexChanged.connect(self.cambiar_quirofano)
        self.combo_quirofano.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLOR_PRINCIPAL};
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
        """)
        control_layout.addWidget(self.combo_quirofano)

        # Estado y botones
        self.lbl_estado_actual = QLabel("Estado: Disponible")
        self.lbl_estado_actual.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout.addWidget(self.lbl_estado_actual)

        control_layout.addStretch()

        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_graficas)
        self.btn_actualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACENTO};
                color: white;
                border-radius: 3px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background-color: #2980B9;
            }}
        """)
        control_layout.addWidget(self.btn_actualizar)

        layout.addWidget(control_frame)

        # Panel de información
        info_layout = QHBoxLayout()

        # Resumen de variables
        panel_valores = QGroupBox("Valores Actuales")
        panel_valores.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLOR_PRINCIPAL};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)

        valores_layout = QGridLayout(panel_valores)

        # Indicadores de variables
        self.indicadores = {}
        for i, (var, unidad) in enumerate([("Temperatura", "°C"), ("Humedad", "%"), ("Presión", "Pa")]):
            valores_layout.addWidget(QLabel(f"{var}:"), i, 0)

            # Valor actual
            clave_variable = var.lower()
            if 'presión' in clave_variable:
                clave_variable = 'presion'
            self.indicadores[clave_variable] = QLabel("--")
            self.indicadores[clave_variable].setFont(QFont("Arial", 12, QFont.Bold))
            self.indicadores[clave_variable].setAlignment(Qt.AlignCenter)
            self.indicadores[clave_variable].setStyleSheet(f"""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            """)
            valores_layout.addWidget(self.indicadores[clave_variable], i, 1)

            # Unidad
            valores_layout.addWidget(QLabel(unidad), i, 2)

            # Estado
            estado_label = QLabel()
            estado_label.setFixedSize(20, 20)
            estado_label.setStyleSheet(f"""
                background-color: gray;
                border-radius: 10px;
            """)
            clave_estado = clave_variable + "_estado"
            self.indicadores[clave_estado] = estado_label
            valores_layout.addWidget(estado_label, i, 3)

        # Ajustar espaciado
        valores_layout.setContentsMargins(15, 15, 15, 15)
        valores_layout.setVerticalSpacing(15)

        info_layout.addWidget(panel_valores)

        # Información adicional y recomendaciones
        panel_info = QGroupBox("Información y Recomendaciones")
        panel_info.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLOR_PRINCIPAL};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)

        info_content_layout = QVBoxLayout(panel_info)

        # Texto de información
        self.lbl_info = QLabel(
            """<p><b>Rangos recomendados:</b></p>
            <p>• <b>Temperatura:</b> 18-24 °C</p>
            <p>• <b>Humedad:</b> 30-60 %</p>
            <p>• <b>Presión diferencial:</b> 10-20 Pa</p>
            <p><b>Recomendaciones:</b> Mantener estos valores dentro del rango
            previene la proliferación de microorganismos y reduce el riesgo
            de infecciones del sitio quirúrgico.</p>"""
        )
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setStyleSheet("padding: 10px;")
        info_content_layout.addWidget(self.lbl_info)

        info_layout.addWidget(panel_info)

        layout.addLayout(info_layout)

        # Panel de gráficas
        panel_graficas = QFrame()
        panel_graficas.setFrameShape(QFrame.StyledPanel)
        panel_graficas.setStyleSheet(f"""
            background-color: white;
            border: 1px solid {COLOR_PRINCIPAL};
            border-radius: 5px;
        """)
        graficas_layout = QVBoxLayout(panel_graficas)

        # Título de las gráficas
        titulo_graficas = QLabel("Monitoreo en Tiempo Real")
        titulo_graficas.setFont(QFont("Arial", 12, QFont.Bold))
        titulo_graficas.setAlignment(Qt.AlignCenter)
        titulo_graficas.setStyleSheet(f"color: {COLOR_PRINCIPAL};")
        graficas_layout.addWidget(titulo_graficas)

        # Canvas para las gráficas
        self.canvas = GraficaMonitoreo(self, width=6, height=6)
        graficas_layout.addWidget(self.canvas)

        layout.addWidget(panel_graficas)

        # Quirófano seleccionado actualmente (índice base 0)
        self.quirofano_actual = 0

        # Proporciones del layout
        layout.setStretch(0, 0)  # Encabezado
        layout.setStretch(1, 0)  # Panel de control
        layout.setStretch(2, 1)  # Panel de información
        layout.setStretch(3, 3)  # Panel de gráficas

    def set_paneles_quirofano(self, paneles):
        self.paneles_quirofano = paneles

    def actualizar_datetime(self):
        ahora = datetime.now()
        self.lbl_datetime.setText(ahora.strftime("%d/%m/%Y %H:%M:%S"))

    def cambiar_quirofano(self, index):
        self.quirofano_actual = index

        # Verificar que paneles_quirofano esté configurado
        if self.paneles_quirofano is None:
            return

        # Obtener panel del quirófano actual
        quirofano = self.paneles_quirofano[index]

        # Actualizar estado mostrado
        if quirofano.en_uso:
            self.lbl_estado_actual.setText("Estado: En uso")
            self.lbl_estado_actual.setStyleSheet(f"font-weight: bold; color: {COLOR_ALERTA};")
        else:
            self.lbl_estado_actual.setText("Estado: Disponible")
            self.lbl_estado_actual.setStyleSheet(f"font-weight: bold; color: {COLOR_OK};")

        # Actualizar gráficas e indicadores
        self.actualizar_graficas()

    def actualizar_graficas(self):
        if self.paneles_quirofano is None:
            return

        # Obtener datos del sensor del quirófano seleccionado
        panel = self.paneles_quirofano[self.quirofano_actual]
        sensor = panel.sensor

        # Obtener datos actuales
        timestamps = sensor.timestamps
        temp = sensor.historial_temperatura
        hum = sensor.historial_humedad
        pres = sensor.historial_presion

        # Actualizar gráficas
        self.canvas.actualizar_datos(timestamps, temp, hum, pres)

        # Actualizar indicadores
        if len(temp) > 0:
            temp_actual = temp[-1]
            hum_actual = hum[-1]
            pres_actual = pres[-1]

            # Actualizar valores
            self.indicadores['temperatura'].setText(f"{temp_actual:.1f}")
            self.indicadores['humedad'].setText(f"{hum_actual:.1f}")
            self.indicadores['presion'].setText(f"{pres_actual:.1f}")

            # Actualizar indicadores de estado
            self.actualizar_indicador_estado('temperatura', temp_actual, RANGO_TEMPERATURA)
            self.actualizar_indicador_estado('humedad', hum_actual, RANGO_HUMEDAD)
            self.actualizar_indicador_estado('presion', pres_actual, RANGO_PRESION)

    def actualizar_indicador_estado(self, variable, valor, rango):
        estado_label = self.indicadores[f"{variable}_estado"]
        valor_label = self.indicadores[variable]

        if rango[0] <= valor <= rango[1]:
            # Valor dentro del rango
            estado_label.setStyleSheet(f"""
                background-color: {COLOR_OK};
                border-radius: 10px;
            """)
            valor_label.setStyleSheet(f"""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                color: black;
                min-width: 80px;
            """)
        else:
            # Valor fuera del rango
            estado_label.setStyleSheet(f"""
                background-color: {COLOR_ALERTA};
                border-radius: 10px;
            """)
            valor_label.setStyleSheet(f"""
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                color: {COLOR_ALERTA};
                font-weight: bold;
                min-width: 80px;
            """)

# Pestaña con la vista general de todos los quirófanos
class PestañaGeneral(QWidget):
    def __init__(self, ventana_principal, parent=None):
        super().__init__(parent)
        self.ventana_principal = ventana_principal # Guardar referencia
        # Layout principal
        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("Vista General de Quirófanos")
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(f"color: {COLOR_PRINCIPAL}; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Grid para los paneles de quirófanos
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # Crear paneles para 6 quirófanos
        self.paneles_quirofano = []
        for i in range(6):
            fila = i // 3
            col = i % 3
            # Pasar la referencia a la ventana principal al crear PanelQuirofano
            panel = PanelQuirofano(i+1, self, self.ventana_principal)
            grid_layout.addWidget(panel, fila, col)

            # Guardar referencia al panel
            self.paneles_quirofano.append(panel)

        layout.addLayout(grid_layout)

        # Panel de alertas recientes
        alertas_group = QGroupBox("Alertas Recientes")
        alertas_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLOR_PRINCIPAL};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)

        alertas_layout = QVBoxLayout(alertas_group)

        # Lista de alertas (placeholder)
        self.lista_alertas = QLabel(
            "<p><i>No hay alertas recientes</i></p>"
        )
        self.lista_alertas.setStyleSheet(f"""
            background-color: {COLOR_SECUNDARIO};
            padding: 10px;
            border-radius: 5px;
        """)
        self.lista_alertas.setWordWrap(True)
        alertas_layout.addWidget(self.lista_alertas)

        # Lista de alertas (historial)
        self.historial_alertas = []

        layout.addWidget(alertas_group)

        # Proporciones del layout
        layout.setStretch(0, 0)  # Título
        layout.setStretch(1, 3)  # Grid de quirófanos
        layout.setStretch(2, 1)  # Panel de alertas

    def mostrar_alerta(self, quirofano_id, variables):
        # Crear mensaje de alerta
        timestamp = datetime.now().strftime("%H:%M:%S")
        mensaje = f"<p><b>[{timestamp}]</b> <font color='{COLOR_ALERTA}'>Alerta</font> - <b>Quirófano {quirofano_id}</b>: Variables fuera de rango: {variables}</p>"

        # Añadir al historial
        self.historial_alertas.insert(0, mensaje)

        # Mantener solo las últimas 10 alertas
        if len(self.historial_alertas) > 10:
            self.historial_alertas.pop()

        # Actualizar la lista mostrada
        if self.historial_alertas:
            self.lista_alertas.setText("".join(self.historial_alertas))
        else:
            self.lista_alertas.setText("<p><i>No hay alertas recientes</i></p>")

# Ventana principal
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurar ventana
        self.setWindowTitle("Sistema de Control de Infecciones en Quirófanos")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(f"background-color: {COLOR_SECUNDARIO};")

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Tab widget para las pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ /* The frame around the page */
                border-top: 2px solid {COLOR_PRINCIPAL};
                background: {COLOR_SECUNDARIO};
            }}

            QTabWidget::tab-bar {{
                left: 5px; /* move to the right by 5px */
            }}

            QTabBar::tab {{
                background: {COLOR_PRINCIPAL};
                color: white;
                border: 1px solid {COLOR_PRINCIPAL};
                border-bottom: none;
                padding: 8px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}

            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: {COLOR_ACENTO};
            }}
        """)
        main_layout.addWidget(self.tabs)

        # Crear pestañas
        self.pestaña_general = PestañaGeneral(self) # Pasar la instancia de VentanaPrincipal
        self.pestaña_visualizacion = PestañaVisualizacion(self)

        # Añadir pestañas al tab widget
        self.tabs.addTab(self.pestaña_general, "Vista General")
        self.tabs.addTab(self.pestaña_visualizacion, "Visualización Detallada")

        # Pasar la referencia de los paneles de quirófano a la pestaña de visualización
        self.pestaña_visualizacion.set_paneles_quirofano(self.pestaña_general.paneles_quirofano)

    def mostrar_alerta(self, quirofano_id, variables):
        # Llama al método de la pestaña general para mostrar la alerta
        self.pestaña_general.mostrar_alerta(quirofano_id, variables)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
