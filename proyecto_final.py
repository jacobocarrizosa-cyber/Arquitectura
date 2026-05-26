import tkinter as tk
from tkinter import messagebox

class VonNeumannSimV4:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador CPU Von Neumann v4.0 (Ensamblador y Bases Numéricas)")
        self.root.geometry("1100x640")
        self.root.configure(bg="#f0f2f5")

        # ---- ESTADO DEL HARDWARE ----
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        self.ALU = "---"
        self.memory = [""] * 16

        self.cycle_state = 0 
        self.current_opcode = ""
        self.current_operand = None
        self.is_running = False
        
        # Variable para la vista de datos
        self.display_mode = tk.StringVar(value="DEC")

        self.create_widgets()
        
        # Programa por defecto usando ETIQUETAS
        default_program = """LOAD DATO1
SUB DATO2
JUMP SALTAR
HALT
SALTAR: STORE RES
HALT
DATO1: 20
DATO2: 8
RES: 0"""
        self.code_text.insert("1.0", default_program)
        self.load_code_to_ram()

    def create_widgets(self):
        title = tk.Label(self.root, text="💻 Simulador Von Neumann - Ensamblador Pro", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#1e293b")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10)

        # ================= COLUMNA 1: EDITOR =================
        editor_frame = tk.LabelFrame(main_frame, text=" Editor (Soporta Etiquetas) ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        editor_frame.pack(side="left", fill="y", padx=5)

        tk.Label(editor_frame, text="Usa 'ETIQUETA:' para marcar líneas.", font=("Arial", 8, "italic"), bg="white", fg="#64748b", justify="left").pack(anchor="w", pady=(0, 5))
        self.code_text = tk.Text(editor_frame, font=("Consolas", 11), width=18, bg="#f8fafc", fg="#0f172a", bd=1, relief="solid")
        self.code_text.pack(fill="both", expand=True, pady=5)
        tk.Button(editor_frame, text="⚙️ Ensamblar a RAM", font=("Arial", 10, "bold"), bg="#0ea5e9", fg="white", command=self.load_code_to_ram).pack(fill="x")

        # ================= COLUMNA 2: CPU =================
        cpu_frame = tk.LabelFrame(main_frame, text=" CPU ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        cpu_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.reg_labels = {}
        registers = [("PC", "PC"), ("MAR", "MAR"), ("MDR", "MDR"), ("IR", "IR"), ("AC", "AC")]

        for label_text, key in registers:
            frame = tk.Frame(cpu_frame, bg="white", pady=6)
            frame.pack(fill="x")
            tk.Label(frame, text=label_text, font=("Arial", 10, "bold"), bg="white", width=5, anchor="w").pack(side="left")
            val_lbl = tk.Label(frame, text="0", font=("Consolas", 11, "bold"), bg="#e2e8f0", width=14, relief="sunken", bd=1)
            val_lbl.pack(side="right")
            self.reg_labels[key] = val_lbl

        alu_frame = tk.LabelFrame(cpu_frame, text=" ALU ", font=("Arial", 9, "bold"), bg="#fff1f2", fg="#be123c", pady=5, padx=5)
        alu_frame.pack(fill="x", pady=15)
        self.alu_val_lbl = tk.Label(alu_frame, text="---", font=("Consolas", 12, "bold"), bg="white", fg="#e11d48", relief="solid", bd=1, pady=4)
        self.alu_val_lbl.pack(fill="x")

        self.status_lbl = tk.Label(cpu_frame, text="Estado: LISTO", font=("Arial", 10, "bold"), fg="#2563eb", bg="white")
        self.status_lbl.pack(pady=5)

        # ================= COLUMNA 3: BUSES =================
        self.bus_canvas = tk.Canvas(main_frame, width=120, bg="#f0f2f5", highlightthickness=0)
        self.bus_canvas.pack(side="left", fill="y", padx=5)

        self.bus_canvas.create_text(60, 80, text="Bus Direcciones", font=("Arial", 8, "bold"), fill="#64748b")
        self.bus_address = self.bus_canvas.create_line(10, 100, 110, 100, width=5, fill="#cbd5e1", arrow=tk.LAST)

        self.bus_canvas.create_text(60, 150, text="Bus de Datos", font=("Arial", 8, "bold"), fill="#64748b")
        self.bus_data = self.bus_canvas.create_line(10, 170, 110, 170, width=5, fill="#cbd5e1", arrow=tk.BOTH)

        # ================= COLUMNA 4: RAM Y CONTROLES VISUALES =================
        right_frame = tk.Frame(main_frame, bg="#f0f2f5")
        right_frame.pack(side="left", fill="both", padx=5)

        # Selector de Base Numérica
        view_frame = tk.LabelFrame(right_frame, text=" Vista de Datos ", font=("Arial", 9, "bold"), bg="white", padx=5, pady=2)
        view_frame.pack(fill="x", pady=(0, 10))
        
        for text, mode in [("Dec (10)", "DEC"), ("Hex (16)", "HEX"), ("Bin (2)", "BIN")]:
            tk.Radiobutton(view_frame, text=text, variable=self.display_mode, value=mode, bg="white", font=("Arial", 8), command=self.update_gui_values).pack(side="left", expand=True)

        mem_frame = tk.LabelFrame(right_frame, text=" RAM ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=5)
        mem_frame.pack(fill="both", expand=True)

        self.mem_index_labels = []
        self.mem_val_labels = []
        for i in range(16):
            frame = tk.Frame(mem_frame, bg="white")
            frame.pack(fill="x", pady=1)
            idx_lbl = tk.Label(frame, text=f" [{i:02d}] ", font=("Consolas", 9, "bold"), bg="white", fg="#94a3b8")
            idx_lbl.pack(side="left", padx=2)
            val_lbl = tk.Label(frame, text="", font=("Consolas", 10), bg="#f8fafc", width=14, relief="solid", bd=1, anchor="w", padx=5)
            val_lbl.pack(side="left")
            self.mem_index_labels.append(idx_lbl)
            self.mem_val_labels.append(val_lbl)

        # ================= CONTROLES INFERIORES =================
        btn_frame = tk.Frame(self.root, bg="#f0f2f5", pady=10)
        btn_frame.pack(fill="x")

        self.btn_play = tk.Button(btn_frame, text="▶️ Auto", font=("Arial", 10, "bold"), bg="#10b981", fg="white", command=self.play_sim, width=8)
        self.btn_play.pack(side="left", padx=(20, 5))

        self.btn_pause = tk.Button(btn_frame, text="⏸️ Pausa", font=("Arial", 10, "bold"), bg="#f59e0b", fg="white", command=self.pause_sim, state="disabled", width=8)
        self.btn_pause.pack(side="left", padx=5)

        self.speed_slider = tk.Scale(btn_frame, from_=0.2, to_=2.5, resolution=0.1, orient="horizontal", label="Velocidad (Seg)", bg="#f0f2f5", font=("Arial", 8))
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=15)

        self.btn_step = tk.Button(btn_frame, text="Siguiente Paso ⏭️", font=("Arial", 10, "bold"), bg="#3b82f6", fg="white", command=self.step_cycle, padx=10)
        self.btn_step.pack(side="left", padx=15)

        tk.Button(btn_frame, text="Reiniciar 🔄", font=("Arial", 10), bg="#ef4444", fg="white", command=self.reset_sim, padx=10).pack(side="right", padx=20)

    # --- LOGICA DEL ENSAMBLADOR (TWO-PASS) ---
    def load_code_to_ram(self):
        raw_lines = self.code_text.get("1.0", tk.END).strip().split("\n")
        self.memory = [""] * 16
        
        labels = {}
        clean_lines = []
        mem_idx = 0
        
        # PASO 1: Buscar etiquetas y limpiar código
        for line in raw_lines:
            line = line.strip()
            if not line: continue
            
            if ":" in line:
                parts = line.split(":", 1)
                label_name = parts[0].strip()
                instruction = parts[1].strip()
                labels[label_name] = mem_idx
                if instruction:
                    clean_lines.append(instruction)
                    mem_idx += 1
            else:
                clean_lines.append(line)
                mem_idx += 1

        # PASO 2: Reemplazar etiquetas por direcciones de memoria
        for i in range(min(16, len(clean_lines))):
            inst = clean_lines[i]
            parts = inst.split()
            if len(parts) == 2:
                op, operand = parts[0], parts[1]
                if operand in labels:
                    inst = f"{op} {labels[operand]}" # Reemplaza el texto por el número
            self.memory[i] = inst
            
        self.reset_sim()

    # --- FORMATEO NUMERICO (DEC/HEX/BIN) ---
    def format_num(self, val):
        try:
            num = int(val)
            mode = self.display_mode.get()
            # Se aplica máscara 0xFF para simular 8-bits reales (y manejar negativos)
            if mode == "HEX": return f"0x{num & 0xFF:02X}"
            elif mode == "BIN": return f"{num & 0xFF:08b}"
            return str(num)
        except ValueError:
            # Si no es un número puro, vemos si es una instrucción como "LOAD 10"
            parts = str(val).split()
            if len(parts) == 2:
                try:
                    operand = int(parts[1])
                    return f"{parts[0]} {self.format_num(operand)}"
                except ValueError:
                    pass
            return str(val)

    def update_gui_values(self):
        self.reg_labels["PC"].config(text=self.format_num(self.PC))
        self.reg_labels["MAR"].config(text=self.format_num(self.MAR))
        
        # MDR e IR pueden ser texto (instrucciones) o números
        self.reg_labels["MDR"].config(text=self.format_num(self.MDR))
        self.reg_labels["IR"].config(text=self.format_num(self.IR))
        
        self.reg_labels["AC"].config(text=self.format_num(self.AC))
        
        if self.ALU != "---" and "->" not in self.ALU:
            # Simple limpieza visual si hay ALU
            self.alu_val_lbl.config(text=self.ALU)
        else:
            self.alu_val_lbl.config(text=self.ALU)

        for i in range(16):
            self.mem_val_labels[i].config(text=self.format_num(self.memory[i]), bg="#f8fafc")
            if i == self.PC and self.cycle_state != 3:
                self.mem_index_labels[i].config(text=f"▶[{i:02d}]", fg="#b45309", bg="#fef08a")
            else:
                self.mem_index_labels[i].config(text=f" [{i:02d}] ", fg="#94a3b8", bg="white")

    def reset_highlights(self):
        for lbl in self.reg_labels.values(): lbl.config(bg="#e2e8f0")
        self.alu_val_lbl.config(bg="white")
        self.bus_canvas.itemconfig(self.bus_address, fill="#cbd5e1")
        self.bus_canvas.itemconfig(self.bus_data, fill="#cbd5e1")

    def safe_get_mem(self, addr):
        if addr is not None and 0 <= addr < 16:
            try: return int(self.memory[addr])
            except ValueError: return 0
        return 0

    # --- CONTROL AUTO-RUN ---
    def play_sim(self):
        if self.cycle_state == 3: return
        self.is_running = True
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_step.config(state="disabled")
        self.auto_step()

    def pause_sim(self):
        self.is_running = False
        self.btn_play.config(state="normal")
        self.btn_pause.config(state="disabled")
        self.btn_step.config(state="normal")

    def auto_step(self):
        if not self.is_running: return
        self.step_cycle()
        if self.cycle_state == 3: 
            self.pause_sim()
            return
        self.root.after(int(self.speed_slider.get() * 1000), self.auto_step)

    # --- CICLO PRINCIPAL ---
    def step_cycle(self):
        if self.cycle_state == 3: return
        self.reset_highlights()

        if self.cycle_state == 0: # FETCH
            self.status_lbl.config(text="FETCH (Buscando instrucción...)", fg="#b45309")
            self.MAR = self.PC
            if self.MAR < 16:
                self.MDR = self.memory[self.MAR]
                self.mem_val_labels[self.MAR].config(bg="#fef3c7")
            else: self.MDR = "HALT"
            
            self.IR = self.MDR
            for k in ["PC", "MAR", "MDR", "IR"]: self.reg_labels[k].config(bg="#fef3c7")
            self.bus_canvas.itemconfig(self.bus_address, fill="#f59e0b")
            self.bus_canvas.itemconfig(self.bus_data, fill="#f59e0b")
            self.PC += 1
            self.cycle_state = 1

        elif self.cycle_state == 1: # DECODE
            self.status_lbl.config(text="DECODE (Descifrando Comando)", fg="#1d4ed8")
            self.reg_labels["IR"].config(bg="#dbeafe")
            parts = self.IR.split()
            self.current_opcode = parts[0].upper() if parts else "NOP"
            try: self.current_operand = int(parts[1]) if len(parts) > 1 else None
            except ValueError: self.current_operand = None
            self.cycle_state = 2

        elif self.cycle_state == 2: # EXECUTE
            self.status_lbl.config(text=f"EXECUTE ({self.current_opcode})", fg="#15803d")
            op, addr = self.current_opcode, self.current_operand

            if op in ["LOAD", "ADD", "SUB"]:
                self.bus_canvas.itemconfig(self.bus_address, fill="#10b981")
                self.bus_canvas.itemconfig(self.bus_data, fill="#10b981")
            elif op == "STORE":
                self.bus_canvas.itemconfig(self.bus_address, fill="#ef4444")
                self.bus_canvas.itemconfig(self.bus_data, fill="#ef4444")

            if op == "LOAD":
                self.AC = self.safe_get_mem(addr)
                self.reg_labels["AC"].config(bg="#dcfce7")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")
                self.ALU = "---"

            elif op == "STORE":
                if addr is not None and 0 <= addr < 16:
                    self.memory[addr] = str(self.AC)
                    self.mem_val_labels[addr].config(bg="#fca5a5")
                self.reg_labels["AC"].config(bg="#fca5a5")
                self.ALU = "---"

            elif op == "ADD":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} + {val}"
                self.AC += val
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")

            elif op == "SUB":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} - {val}"
                self.AC -= val
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca") 
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")

            elif op == "JUMP":
                if addr is not None and 0 <= addr < 16:
                    self.ALU = f"PC -> {addr}"
                    self.PC = addr
                    self.reg_labels["PC"].config(bg="#dcfce7")
                    self.alu_val_lbl.config(bg="#fecaca")
                else: self.ALU = "JUMP Error"

            elif op == "HALT":
                self.cycle_state = 3
                self.status_lbl.config(text="HALTED (Programa Terminado)", fg="#b91c1c")
                self.ALU = "---"
                self.update_gui_values()
                return

            if self.cycle_state != 3: self.cycle_state = 0

        self.update_gui_values()

    def reset_sim(self):
        self.pause_sim()
        self.PC, self.MAR, self.AC = 0, 0, 0
        self.MDR, self.IR, self.ALU = "", "", "---"
        self.cycle_state = 0
        self.status_lbl.config(text="Estado: LISTO", fg="#2563eb")
        self.reset_highlights()
        self.update_gui_values()

if __name__ == "__main__":
    root = tk.Tk()
    app = VonNeumannSimV4(root)
    root.mainloop()