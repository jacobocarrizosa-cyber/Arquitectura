import tkinter as tk
import re

class VonNeumannSimV7:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador CPU Von Neumann v7.0 (Operaciones Lógicas de Bits)")
        self.root.geometry("1150x660")
        self.root.configure(bg="#f0f2f5")

        # ---- ESTADO DEL HARDWARE ----
        self.PC = 0
        self.MAR = 0
        self.MDR = ""
        self.IR = ""
        self.AC = 0
        self.ALU = "---"
        self.FLAG_Z = False 
        self.FLAG_N = False 
        self.memory = [""] * 16

        self.cycle_state = 0 
        self.current_opcode = ""
        self.current_operand = None
        self.is_running = False
        
        self.display_mode = tk.StringVar(value="DEC")

        self.create_widgets()
        
        # PROGRAMA POR DEFECTO: Demuestra AND (Máscara), OR, XOR y NOT
        default_program = """LOAD DATO1
AND MASCARA
STORE R_AND
LOAD DATO1
OR DATO2
STORE R_OR
LOAD DATO1
XOR DATO2
STORE R_XOR
NOT
STORE R_NOT
HALT
DATO1: 12
DATO2: 5
MASCARA: 14
R_AND: 0"""
        self.code_text.insert("1.0", default_program)
        self.highlight_syntax()
        self.load_code_to_ram()

    def create_widgets(self):
        title = tk.Label(self.root, text="💻 Simulador Von Neumann V7.0 - ALU Lógica", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#1e293b")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10)

        # ================= COLUMNA 1: EDITOR =================
        editor_frame = tk.LabelFrame(main_frame, text=" Editor de Código ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        editor_frame.pack(side="left", fill="y", padx=5)

        tk.Label(editor_frame, text="Nuevos comandos: AND, OR, XOR, NOT", font=("Arial", 8, "italic"), bg="white", fg="#64748b", justify="left").pack(anchor="w", pady=(0, 5))
        
        text_container = tk.Frame(editor_frame, bg="white", bd=1, relief="solid")
        text_container.pack(fill="both", expand=True, pady=5)

        self.line_numbers = tk.Text(text_container, width=3, bg="#e2e8f0", fg="#64748b", font=("Consolas", 11), state="disabled", bd=0, padx=3)
        self.line_numbers.pack(side="left", fill="y")
        self.update_line_numbers()

        self.code_text = tk.Text(text_container, font=("Consolas", 11), width=18, bg="#f8fafc", fg="#0f172a", bd=0, insertbackground="black")
        self.code_text.pack(side="left", fill="both", expand=True)
        
        self.code_text.tag_config("keyword", foreground="#2563eb", font=("Consolas", 11, "bold")) 
        self.code_text.tag_config("label", foreground="#059669", font=("Consolas", 11, "italic")) 
        self.code_text.tag_config("number", foreground="#9333ea") 

        self.code_text.bind("<KeyRelease>", self.highlight_syntax)

        tk.Button(editor_frame, text="⚙️ Ensamblar a RAM", font=("Arial", 10, "bold"), bg="#0ea5e9", fg="white", command=self.load_code_to_ram).pack(fill="x", pady=(5,0))

        # ================= COLUMNA 2: CPU =================
        cpu_frame = tk.LabelFrame(main_frame, text=" CPU ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        cpu_frame.pack(side="left", fill="both", expand=True, padx=5)

        flags_container = tk.Frame(cpu_frame, bg="white")
        flags_container.pack(fill="x", pady=(0, 10))
        tk.Label(flags_container, text="Flags:", font=("Arial", 9, "bold"), bg="white").pack(side="left")
        
        self.led_z = tk.Label(flags_container, text="Z (Zero)", font=("Arial", 8, "bold"), bg="#fca5a5", fg="white", width=8, relief="ridge")
        self.led_z.pack(side="left", padx=5)
        self.led_n = tk.Label(flags_container, text="N (Neg)", font=("Arial", 8, "bold"), bg="#fca5a5", fg="white", width=8, relief="ridge")
        self.led_n.pack(side="left", padx=5)

        self.reg_labels = {}
        registers = [("PC", "PC"), ("MAR", "MAR"), ("MDR", "MDR"), ("IR", "IR"), ("AC", "AC")]

        for label_text, key in registers:
            frame = tk.Frame(cpu_frame, bg="white", pady=4)
            frame.pack(fill="x")
            tk.Label(frame, text=label_text, font=("Arial", 10, "bold"), bg="white", width=5, anchor="w").pack(side="left")
            val_lbl = tk.Label(frame, text="0", font=("Consolas", 11, "bold"), bg="#e2e8f0", width=14, relief="sunken", bd=1)
            val_lbl.pack(side="right")
            self.reg_labels[key] = val_lbl

        alu_frame = tk.LabelFrame(cpu_frame, text=" ALU ", font=("Arial", 9, "bold"), bg="#fff1f2", fg="#be123c", pady=5, padx=5)
        alu_frame.pack(fill="x", pady=10)
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

        # ================= COLUMNA 4: RAM =================
        right_frame = tk.Frame(main_frame, bg="#f0f2f5")
        right_frame.pack(side="left", fill="both", padx=5)

        view_frame = tk.LabelFrame(right_frame, text=" Vista de Datos ", font=("Arial", 9, "bold"), bg="white", padx=5, pady=2)
        view_frame.pack(fill="x", pady=(0, 10))
        
        for text, mode in [("Dec", "DEC"), ("Hex", "HEX"), ("Bin", "BIN")]:
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

        # ================= CONTROLES =================
        btn_frame = tk.Frame(self.root, bg="#f0f2f5", pady=10)
        btn_frame.pack(fill="x")

        self.btn_play = tk.Button(btn_frame, text="▶️ Auto", font=("Arial", 10, "bold"), bg="#10b981", fg="white", command=self.play_sim, width=8)
        self.btn_play.pack(side="left", padx=(20, 5))
        self.btn_pause = tk.Button(btn_frame, text="⏸️ Pausa", font=("Arial", 10, "bold"), bg="#f59e0b", fg="white", command=self.pause_sim, state="disabled", width=8)
        self.btn_pause.pack(side="left", padx=5)
        self.speed_slider = tk.Scale(btn_frame, from_=0.2, to_=2.5, resolution=0.1, orient="horizontal", label="Velocidad (Seg)", bg="#f0f2f5", font=("Arial", 8))
        self.speed_slider.set(0.8)
        self.speed_slider.pack(side="left", padx=15)
        self.btn_step = tk.Button(btn_frame, text="Siguiente Paso ⏭️", font=("Arial", 10, "bold"), bg="#3b82f6", fg="white", command=self.step_cycle, padx=10)
        self.btn_step.pack(side="left", padx=15)
        tk.Button(btn_frame, text="Reiniciar 🔄", font=("Arial", 10), bg="#ef4444", fg="white", command=self.reset_sim, padx=10).pack(side="right", padx=20)

    def update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        for i in range(16): self.line_numbers.insert(tk.END, f"{i:02d}\n")
        self.line_numbers.config(state="disabled")

    def highlight_syntax(self, event=None):
        for tag in ["keyword", "label", "number"]: self.code_text.tag_remove(tag, "1.0", tk.END)
        
        # Añadidos AND, OR, XOR y NOT a las palabras clave
        keywords = ["LOAD", "STORE", "ADD", "SUB", "JUMP", "JZ", "JN", "AND", "OR", "XOR", "NOT", "HALT"]
        for kw in keywords:
            start_idx = "1.0"
            while True:
                start_idx = self.code_text.search(rf"\b{kw}\b", start_idx, tk.END, regexp=True)
                if not start_idx: break
                end_idx = f"{start_idx}+{len(kw)}c"
                self.code_text.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

        # Etiquetas
        start_idx = "1.0"
        while True:
            start_idx = self.code_text.search(r"^\s*[A-Za-z0-9_]+:", start_idx, tk.END, regexp=True)
            if not start_idx: break
            line_text = self.code_text.get(start_idx, f"{start_idx} lineend")
            match_len = len(line_text.split(":")[0]) + 1
            self.code_text.tag_add("label", start_idx, f"{start_idx}+{match_len}c")
            start_idx = f"{start_idx}+{match_len}c"

        # Números
        start_idx = "1.0"
        while True:
            start_idx = self.code_text.search(r"\b\d+\b", start_idx, tk.END, regexp=True)
            if not start_idx: break
            match = re.match(r"\d+", self.code_text.get(start_idx, f"{start_idx} wordend"))
            if match:
                end_idx = f"{start_idx}+{len(match.group())}c"
                self.code_text.tag_add("number", start_idx, end_idx)
                start_idx = end_idx
            else: start_idx = f"{start_idx}+1c"

    def load_code_to_ram(self):
        raw_lines = self.code_text.get("1.0", tk.END).strip().split("\n")
        self.memory = [""] * 16
        labels = {}
        clean_lines = []
        mem_idx = 0
        
        for line in raw_lines:
            line = line.strip()
            if not line: continue
            if ":" in line:
                parts = line.split(":", 1)
                labels[parts[0].strip()] = mem_idx
                if parts[1].strip():
                    clean_lines.append(parts[1].strip())
                    mem_idx += 1
            else:
                clean_lines.append(line)
                mem_idx += 1

        for i in range(min(16, len(clean_lines))):
            inst = clean_lines[i]
            parts = inst.split()
            if len(parts) == 2 and parts[1] in labels:
                inst = f"{parts[0]} {labels[parts[1]]}" 
            self.memory[i] = inst
            
        self.reset_sim()

    def format_num(self, val):
        try:
            num = int(val)
            mode = self.display_mode.get()
            if mode == "HEX": return f"0x{num & 0xFF:02X}"
            elif mode == "BIN": return f"{num & 0xFF:08b}"
            return str(num)
        except ValueError:
            parts = str(val).split()
            if len(parts) == 2:
                try: return f"{parts[0]} {self.format_num(parts[1])}"
                except ValueError: pass
            return str(val)

    def check_flags(self):
        # NOTA: En Python los números negativos son infinitos a la izquierda.
        # Simulamos 8 bits aplicando una máscara antes de chequear el signo.
        val_8bit = self.AC & 0xFF
        self.FLAG_Z = (val_8bit == 0)
        self.FLAG_N = (val_8bit & 0x80) != 0 # Verifica si el bit 7 está encendido

    def update_gui_values(self):
        self.reg_labels["PC"].config(text=self.format_num(self.PC))
        self.reg_labels["MAR"].config(text=self.format_num(self.MAR))
        self.reg_labels["MDR"].config(text=self.format_num(self.MDR))
        self.reg_labels["IR"].config(text=self.format_num(self.IR))
        self.reg_labels["AC"].config(text=self.format_num(self.AC))
        self.alu_val_lbl.config(text=self.ALU)

        self.led_z.config(bg="#22c55e" if self.FLAG_Z else "#fca5a5") 
        self.led_n.config(bg="#ef4444" if self.FLAG_N else "#fca5a5") 

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

    def step_cycle(self):
        if self.cycle_state == 3: return
        self.reset_highlights()

        if self.cycle_state == 0: # FETCH
            self.status_lbl.config(text="FETCH (Buscando instrucción...)", fg="#b45309")
            self.MAR = self.PC
            if self.MAR < 16: self.MDR = self.memory[self.MAR]
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

            if op in ["LOAD", "ADD", "SUB", "JZ", "JN", "JUMP", "AND", "OR", "XOR"]:
                self.bus_canvas.itemconfig(self.bus_address, fill="#10b981")
                self.bus_canvas.itemconfig(self.bus_data, fill="#10b981")
            elif op == "STORE":
                self.bus_canvas.itemconfig(self.bus_address, fill="#ef4444")
                self.bus_canvas.itemconfig(self.bus_data, fill="#ef4444")

            if op == "LOAD":
                self.AC = self.safe_get_mem(addr)
                self.check_flags()
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
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")

            elif op == "SUB":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} - {val}"
                self.AC -= val
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca") 

            # ---- NUEVAS OPERACIONES DE BITS ----
            elif op == "AND":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} AND {val}"
                self.AC = self.AC & val
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")

            elif op == "OR":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} OR {val}"
                self.AC = self.AC | val
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")

            elif op == "XOR":
                val = self.safe_get_mem(addr)
                self.ALU = f"{self.AC} XOR {val}"
                self.AC = self.AC ^ val
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")

            elif op == "NOT":
                # NOT no lee de RAM, solo invierte los bits del Acumulador.
                # Aplicamos la inversión nativa a nivel de bits en Python (~)
                self.ALU = f"NOT {self.AC}"
                self.AC = ~self.AC
                self.check_flags()
                self.reg_labels["AC"].config(bg="#dcfce7")
                self.alu_val_lbl.config(bg="#fecaca")

            elif op in ["JUMP", "JZ", "JN"]:
                do_jump = (op == "JUMP") or (op == "JZ" and self.FLAG_Z) or (op == "JN" and self.FLAG_N)
                
                if do_jump:
                    if addr is not None and 0 <= addr < 16:
                        self.ALU = f"Salto a {addr}"
                        self.PC = addr
                        self.reg_labels["PC"].config(bg="#dcfce7")
                    else: self.ALU = f"{op} Error"
                else:
                    self.ALU = "No salta"

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
        self.FLAG_Z = False
        self.FLAG_N = False
        self.cycle_state = 0
        self.status_lbl.config(text="Estado: LISTO", fg="#2563eb")
        self.reset_highlights()
        self.update_gui_values()

if __name__ == "__main__":
    root = tk.Tk()
    app = VonNeumannSimV7(root)
    root.mainloop()