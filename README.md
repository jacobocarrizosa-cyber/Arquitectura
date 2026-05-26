#  Simulador CPU Von Neumann v7.0 (ALU Lógica Avanzada)

Un simulador interactivo construido en Python que visualiza el funcionamiento interno de una CPU basada en la clásica Arquitectura de Von Neumann. Este proyecto permite observar en tiempo real cómo interactúan la memoria, los registros y una Unidad Aritmético Lógica (ALU) avanzada.

##  Características Principales

* **Ciclo de Instrucción Interactivo:** Permite visualizar paso a paso las fases del procesador: Búsqueda (Fetch), Decodificación (Decode) y Ejecución (Execute).
* **ALU Lógica Avanzada:** No solo realiza operaciones aritméticas básicas (suma, resta), sino que incluye procesamiento de compuertas lógicas (AND, OR, XOR, NOT, etc.).
* **Monitor de Registros:** Visualización en tiempo real del estado de los registros clave de la CPU:
  * **PC (Program Counter):** Contador de programa.
  * **AC (Accumulator):** Acumulador para resultados de la ALU.
  * **IR (Instruction Register):** Registro de instrucción actual.
  * **MAR & MDR:** Registros de direcciones y datos de memoria.
* **Interfaz Gráfica Didáctica:** Construida con la librería Tkinter para ofrecer una representación visual clara de la memoria RAM y el flujo de datos.

##  Tecnologías y Requisitos

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica:** Tkinter (Incluido por defecto en la instalación estándar de Python, no requiere descargas adicionales).

##  Cómo ejecutar el simulador

1. Asegúrate de tener Python instalado en tu sistema.
2. Clona este repositorio o descarga el archivo principal `proyecto_final.py`.
3. Abre una terminal en la carpeta del proyecto.
4. Ejecuta el siguiente comando:
   ```bash
   python proyecto_final.py
