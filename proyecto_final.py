import tkinter as tk
from tkinter import messagebox

class VonNeumannSimV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador CPU Von Neumann v2.0 (Con Editor y ALU)")
        self.root.geometry("980x580")
        self.root.configure(bg="#f0f2f5")

        # ---- ESTADO DEL HARDWARE ----
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        self.ALU = "---" # Estado visual de la ALU
        
        # Memoria RAM de 16 celdas compartida (Datos + Instrucciones)
        self.memory = [""] * 16

        # Control del ciclo: 0=FETCH, 1=DECODE, 2=EXECUTE, 3=HALTED
        self.cycle_state = 0 
        self.current_opcode = ""
        self.current_operand = None

        # ---- CREAR INTERFAZ GRÁFICA ----
        self.create_widgets()
        
        # Cargar programa por defecto en el Editor y en la RAM
        default_program = "LOAD 6\nSUB 7\nJUMP 4\nHALT\nSTORE 8\nHALT\n20\n8\n0"
        self.code_text.insert("1.0", default_program)
        self.load_code_to_ram()

    def create_widgets(self):
        # Título principal
        title = tk.Label(self.root, text="💻 Simulador Avanzado CPU Von Neumann", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#1e293b")
        title.pack(pady=10)

        # Contenedor Principal de 3 Columnas
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=15)

        # ================= COLUMNA 1: EDITOR DE CÓDIGO =================
        editor_frame = tk.LabelFrame(main_frame, text=" Editor de Código (RAM 0-15) ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        editor_frame.pack(side="left", fill="both", expand=True, padx=5)

        instructions_help = tk.Label(editor_frame, text="Set: LOAD, STORE, ADD, SUB, JUMP, HALT\n(Escribe una instrucción o dato por línea)", 
                                     font=("Arial", 8, "italic"), bg="white", fg="#64748b", justify="left")
        instructions_help.pack(anchor="w", pady=(0, 5))

        self.code_text = tk.Text(editor_frame, font=("Consolas", 11), width=22, bg="#f8fafc", fg="#0f172a", bd=1, relief="solid")
        self.code_text.pack(fill="both", expand=True, pady=5)

        btn_load = tk.Button(editor_frame, text="📥 Cargar Código a RAM", font=("Arial", 10, "bold"), bg="#0ea5e9", fg="white", command=self.load_code_to_ram)
        btn_load.pack(fill="x", pady=2)


        # ================= COLUMNA 2: PROCESADOR (CPU) =================
        cpu_frame = tk.LabelFrame(main_frame, text=" Unidad Central de Procesamiento (CPU) ", font=("Arial", 11, "bold"), bg="white", padx=15, pady=10)
        cpu_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Subpanel de Registros
        self.reg_labels = {}
        registers = [("PC (Program Counter)", "PC"), ("MAR (Mem. Address Reg)", "MAR"), 
                     ("MDR (Mem. Data Reg)", "MDR"), ("IR (Instruction Reg)", "IR"), 
                     ("AC (Accumulator)", "AC")]

        for label_text, key in registers:
            frame = tk.Frame(cpu_frame, bg="white", pady=4)
            frame.pack(fill="x")
            lbl = tk.Label(frame, text=label_text, font=("Arial", 10), bg="white", width=20, anchor="w")
            lbl.pack(side="left")
            val_lbl = tk.Label(frame, text="0", font=("Consolas", 11, "bold"), bg="#e2e8f0", width=12, relief="sunken", bd=1)
            val_lbl.pack(side="right")
            self.reg_labels[key] = val_lbl

        # --- COMPONENTE NUEVO: VISUALIZACIÓN DE ALU ---
        alu_frame = tk.LabelFrame(cpu_frame, text=" ALU (Unidad Aritmética Lógica) ", font=("Arial", 10, "bold"), bg="#fff1f2", fg="#be123c", pady=8, padx=10)
        alu_frame.pack(fill="x", pady=15)
        
        self.alu_val_lbl = tk.Label(alu_frame, text="---", font=("Consolas", 14, "bold"), bg="white", fg="#e11d48", relief="solid", bd=1, pady=4)
        self.alu_val_lbl.pack(fill="x")

        # Estado del Ciclo actual
        self.status_lbl = tk.Label(cpu_frame, text="Estado: LISTO", font=("Arial", 11, "bold"), fg="#2563eb", bg="white", pady=10)
        self.status_lbl.pack()


        # ================= COLUMNA 3: MEMORIA RAM =================
        mem_frame = tk.LabelFrame(main_frame, text=" Memoria Principal (RAM) ", font=("Arial", 11, "bold"), bg="white", padx=15, pady=10)
        mem_frame.pack(side="left", fill="both", padx=5)

        self.mem_labels = []
        for i in range(16):
            frame = tk.Frame(mem_frame, bg="white")
            frame.pack(fill="x")
            lbl = tk.Label(frame, text=f"[{i:02d}]", font=("Consolas", 9, "bold"), bg="white", fg="#94a3b8")
            lbl.pack(side="left", padx=2)
            val_lbl = tk.Label(frame, text="", font=("Consolas", 10), bg="#f8fafc", width=14, relief="solid", bd=1, anchor="w", padx=5)
            val_lbl.pack(side="left", pady=1)
            self.mem_labels.append(val_lbl)


        # --- PANEL INFERIOR DE BOTONES DE CONTROL ---
        btn_frame = tk.Frame(self.root, bg="#f0f2f5", pady=10)
        btn_frame.pack(fill="x")

        self.btn_step = tk.Button(btn_frame, text="Siguiente Paso ➡️", font=("Arial", 11, "bold"), bg="#22c55e", fg="white", command=self.step_cycle, padx=15)
        self.btn_step.pack(side="left", padx=20)

        btn_reset = tk.Button(btn_frame, text="Reiniciar Simulación 🔄", font=("Arial", 11), bg="#ef4444", fg="white", command=self.reset_sim, padx=15)
        btn_reset.pack(side="right", padx=20)

    def load_code_to_ram(self):
        """Lee el editor de texto y mapea línea por línea a las 16 celdas de la RAM."""
        lines = self.code_text.get("1.0", tk.END).strip().split("\n")
        
        for i in range(16):
            self.memory[i] = ""

        idx = 0
        for line in lines:
            cleaned = line.strip()
            if cleaned and idx < 16:
                self.memory[idx] = cleaned
                idx += 1
        
        self.reset_sim()

    def update_gui_values(self):
        """Sincroniza variables lógicas con los componentes gráficos."""
        self.reg_labels["PC"].config(text=str(self.PC))
        self.reg_labels["MAR"].config(text=str(self.MAR))
        self.reg_labels["MDR"].config(text=str(self.MDR))
        self.reg_labels["IR"].config(text=str(self.IR))
        self.reg_labels["AC"].config(text=str(self.AC))
        self.alu_val_lbl.config(text=str(self.ALU))

        for i in range(16):
            self.mem_labels[i].config(text=self.memory[i], bg="#f8fafc")

    def reset_highlights(self):
        """Limpia colores de alerta o animación."""
        for lbl in self.reg_labels.values():
            lbl.config(bg="#e2e8f0")
        self.alu_val_lbl.config(bg="white")

    def safe_get_mem(self, addr):
        """Intenta obtener el valor numérico de una celda de memoria de forma segura."""
        if addr is not None and 0 <= addr < 16:
            try:
                return int(self.memory[addr])
            except ValueError:
                return 0
        return 0

    def step_cycle(self):
        if self.cycle_state == 3:
            messagebox.showinfo("HALT", "Simulación terminada. Re-carga el código o reinicia.")
            return

        self.reset_highlights()

        # ====== 1. FETCH ======
        if self.cycle_state == 0:
            self.status_lbl.config(text="Fase: FETCH (Captación)", fg="#b45309")
            
            self.MAR = self.PC
            if self.MAR < 16:
                self.MDR = self.memory[self.MAR]
                self.mem_labels[self.MAR].config(bg="#fef3c7") # Iluminar RAM investigada
            else:
                self.MDR = "HALT"
            
            self.IR = self.MDR
            
            # Iluminar registros de transferencia de datos
            for k in ["PC", "MAR", "MDR", "IR"]:
                self.reg_labels[k].config(bg="#fef3c7")

            self.PC += 1
            self.cycle_state = 1

        # ====== 2. DECODE ======
        elif self.cycle_state == 1:
            self.status_lbl.config(text="Fase: DECODE (Decodificación)", fg="#1d4ed8")
            self.reg_labels["IR"].config(bg="#dbeafe")

            parts = self.IR.split()
            if len(parts) > 0:
                self.current_opcode = parts[0].upper()
                try:
                    self.current_operand = int(parts[1]) if len(parts) > 1 else None
                except ValueError:
                    self.current_operand = None
            else:
                self.current_opcode = "NOP"
                self.current_operand = None

            self.cycle_state = 2

        # ====== 3. EXECUTE ======
        elif self.cycle_state == 2:
            self.status_lbl.config(text=f"Fase: EXECUTE ({self.current_opcode})", fg="#15803d")
            
            op = self.current_opcode
            addr = self.current_operand

            if op == "LOAD":
                self.AC = self.safe_get_mem(addr)
                self.reg_labels["AC"].config(bg="#dcfce7")
                if addr is not None and addr < 16: self.mem_labels[addr].config(bg="#dcfce7")
                self.ALU = "--- (Passthrough)"

            elif op == "STORE":
                if addr is not None and 0 <= addr < 16:
                    self.memory[addr] = str(self.AC)
                    self.mem_labels[addr].config(bg="#bbf7d0")
                self.reg_labels["AC"].config(bg="#bbf7d0")
                self.ALU = "---"

            elif op == "ADD":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} + {val}" # Se activa la ALU
                self.AC += val
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca") # Alerta visual ALU activa
                if addr is not None and addr < 16: self.mem_labels[addr].config(bg="#dcfce7")

            elif op == "SUB":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} - {val}" # Se activa la ALU para restar
                self.AC -= val
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca") 
                if addr is not None and addr < 16: self.mem_labels[addr].config(bg="#dcfce7")

            elif op == "JUMP":
                if addr is not None and 0 <= addr < 16:
                    self.ALU = f"Modifica PC -> {addr}"
                    self.PC = addr # Forzamos el destino alterando el flujo natural
                    self.reg_labels["PC"].config(bg="#dcfce7")
                    self.alu_val_lbl.config(bg="#fecaca")
                else:
                    self.ALU = "JUMP Inválido"

            elif op == "HALT":
                self.cycle_state = 3
                self.status_lbl.config(text="Estado: HALTED (Ejecución Completada)", fg="#b91c1c")
                self.ALU = "---"
                self.update_gui_values()
                return
            else:
                self.ALU = "NOP (No Operación)"

            if self.cycle_state != 3:
                self.cycle_state = 0 # Volver a FETCH en el siguiente click

        self.update_gui_values()

    def reset_sim(self):
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        self.ALU = "---"
        self.cycle_state = 0
        self.status_lbl.config(text="Estado: LISTO", fg="#2563eb")
        self.reset_highlights()
        self.update_gui_values()

if __name__ == "__main__":
    root = tk.Tk()
    app = VonNeumannSimV2(root)
    root.mainloop()