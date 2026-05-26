import tkinter as tk
from tkinter import messagebox

class VonNeumannSim:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Arquitectura Von Neumann")
        self.root.geometry("750x500")
        self.root.configure(bg="#f0f2f5")

        # ---- ESTADO DEL HARDWARE ----
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        
        # Memoria de 16 celdas (Programa + Datos)
        self.memory = [""] * 16
        # Pre-cargar un programa educativo: Sumar dos números (5 + 3)
        self.memory[0] = "LOAD 10"   # Carga el valor de la dirección 10 en AC
        self.memory[1] = "ADD 11"    # Suma el valor de la dirección 11 al AC
        self.memory[2] = "STORE 12"  # Guarda el AC en la dirección 12
        self.memory[3] = "HALT"      # Termina la ejecución
        self.memory[10] = "5"        # Dato 1
        self.memory[11] = "3"        # Dato 2
        self.memory[12] = "0"        # Espacio para el resultado

        # Control del ciclo: 0=FETCH, 1=DECODE, 2=EXECUTE, 3=HALTED
        self.cycle_state = 0 
        self.current_opcode = ""
        self.current_operand = None

        # ---- CREAR INTERFAZ GRÁFICA ----
        self.create_widgets()
        self.update_gui_values()

    def create_widgets(self):
        # Título principal
        title = tk.Label(self.root, text="💻 Simulador CPU Von Neumann", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#333")
        title.pack(pady=10)

        # Contenedor Principal (Izquierda: Registros, Derecha: Memoria)
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20)

        # --- PANEL DE REGISTROS ---
        reg_frame = tk.LabelFrame(main_frame, text=" Unidad Central de Procesamiento (CPU) ", font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
        reg_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.reg_labels = {}
        registers = [("PC (Program Counter)", "PC"), ("MAR (Mem. Address Reg)", "MAR"), 
                     ("MDR (Mem. Data Reg)", "MDR"), ("IR (Instruction Reg)", "IR"), 
                     ("AC (Accumulator)", "AC")]

        for label_text, key in registers:
            frame = tk.Frame(reg_frame, bg="white", pady=5)
            frame.pack(fill="x")
            lbl = tk.Label(frame, text=label_text, font=("Arial", 10), bg="white", width=22, anchor="w")
            lbl.pack(side="left")
            val_lbl = tk.Label(frame, text="0", font=("Consolas", 11, "bold"), bg="#e9ecef", width=12, relief="sunken", bd=1)
            val_lbl.pack(side="right")
            self.reg_labels[key] = val_lbl

        # Estado del Ciclo actual
        self.status_lbl = tk.Label(reg_frame, text="Estado: LISTO (Presiona 'Siguiente Paso')", font=("Arial", 11, "bold"), fg="blue", bg="white", pady=15)
        self.status_lbl.pack()

        # --- PANEL DE MEMORIA ---
        mem_frame = tk.LabelFrame(main_frame, text=" Memoria Principal (RAM) ", font=("Arial", 11, "bold"), bg="white", padx=15, pady=15)
        mem_frame.pack(side="right", fill="both", padx=10)

        self.mem_labels = []
        for i in range(16):
            frame = tk.Frame(mem_frame, bg="white")
            frame.pack(fill="x")
            lbl = tk.Label(frame, text=f"[{i:02d}]", font=("Consolas", 9), bg="white", fg="gray")
            lbl.pack(side="left", padx=2)
            val_lbl = tk.Label(frame, text=self.memory[i], font=("Consolas", 9), bg="#f8f9fa", width=12, relief="solid", bd=1, anchor="w", padx=5)
            val_lbl.pack(side="left", pady=1)
            self.mem_labels.append(val_lbl)

        # --- PANEL DE CONTROL (BOTONES) ---
        btn_frame = tk.Frame(self.root, bg="#f0f2f5", pady=15)
        btn_frame.pack(fill="x")

        self.btn_step = tk.Button(btn_frame, text="Siguiente Paso ➡️", font=("Arial", 11, "bold"), bg="#0d6efd", fg="white", command=self.step_cycle, padx=10)
        self.btn_step.pack(side="left", padx=20)

        btn_reset = tk.Button(btn_frame, text="Reiniciar 🔄", font=("Arial", 11), bg="#dc3545", fg="white", command=self.reset_sim, padx=10)
        btn_reset.pack(side="right", padx=20)

    def update_gui_values(self):
        """Actualiza los textos en pantalla basándose en el estado de las variables."""
        self.reg_labels["PC"].config(text=str(self.PC))
        self.reg_labels["MAR"].config(text=str(self.MAR))
        self.reg_labels["MDR"].config(text=str(self.MDR))
        self.reg_labels["IR"].config(text=str(self.IR))
        self.reg_labels["AC"].config(text=str(self.AC))

        for i in range(16):
            self.mem_labels[i].config(text=self.memory[i], bg="#f8f9fa")

    def reset_highlights(self):
        """Limpia los colores de animación de los registros."""
        for lbl in self.reg_labels.values():
            lbl.config(bg="#e9ecef")

    def step_cycle(self):
        """Manejador del ciclo Fetch-Decode-Execute paso a paso."""
        if self.cycle_state == 3:
            messagebox.showinfo("Fin", "El programa ha finalizado (HALT). Reinicia para volver a empezar.")
            return

        self.reset_highlights()

        # --- 1. FETCH ---
        if self.cycle_state == 0:
            self.status_lbl.config(text="Fase: FETCH (Captación)", fg="#d97706")
            
            self.MAR = self.PC
            self.MDR = self.memory[self.MAR]
            self.IR = self.MDR
            
            # Iluminar lo involucrado en Fetch
            self.reg_labels["PC"].config(bg="#fef3c7")
            self.reg_labels["MAR"].config(bg="#fef3c7")
            self.reg_labels["MDR"].config(bg="#fef3c7")
            self.reg_labels["IR"].config(bg="#fef3c7")
            if self.MAR < 16:
                self.mem_labels[self.MAR].config(bg="#fef3c7")

            self.PC += 1 # Incrementar PC para la siguiente instrucción
            self.cycle_state = 1 # Pasar a Decode

        # --- 2. DECODE ---
        elif self.cycle_state == 1:
            self.status_lbl.config(text="Fase: DECODE (Decodificación)", fg="#2563eb")
            self.reg_labels["IR"].config(bg="#dbeafe")

            parts = self.IR.split()
            self.current_opcode = parts[0]
            self.current_operand = int(parts[1]) if len(parts) > 1 else None

            self.cycle_state = 2 # Pasar a Execute

        # --- 3. EXECUTE ---
        elif self.cycle_state == 2:
            self.status_lbl.config(text=f"Fase: EXECUTE ({self.current_opcode})", fg="#16a34a")
            
            op = self.current_opcode
            addr = self.current_operand

            if op == "LOAD":
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.mem_labels[addr].config(bg="#dcfce7")
                self.AC = int(self.memory[addr])
            elif op == "ADD":
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.mem_labels[addr].config(bg="#dcfce7")
                self.AC += int(self.memory[addr])
            elif op == "STORE":
                self.memory[addr] = str(self.AC)
                self.mem_labels[addr].config(bg="#bbf7d0")
                self.reg_labels["AC"].config(bg="#bbf7d0")
            elif op == "HALT":
                self.cycle_state = 3
                self.status_lbl.config(text="Estado: HALTED (Simulación Terminada)", fg="red")
                self.update_gui_values()
                return

            if self.cycle_state != 3:
                self.cycle_state = 0 # Volver a empezar el ciclo para la siguiente instrucción

        self.update_gui_values()

    def reset_sim(self):
        """Restablece el simulador al estado inicial."""
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        self.cycle_state = 0
        self.memory[12] = "0" # Limpiar el resultado
        self.status_lbl.config(text="Estado: LISTO (Presiona 'Siguiente Paso')", fg="blue")
        self.reset_highlights()
        self.update_gui_values()

if __name__ == "__main__":
    root = tk.Tk()
    app = VonNeumannSim(root)
    root.mainloop()