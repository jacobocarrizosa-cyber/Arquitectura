import tkinter as tk
from tkinter import messagebox

class VonNeumannSimV3:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador CPU Von Neumann v3.0 (UX & Animación)")
        self.root.geometry("1100x600")
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
        
        # Estado de Auto-Ejecución
        self.is_running = False

        self.create_widgets()
        
        # Cargar programa por defecto
        default_program = "LOAD 6\nSUB 7\nJUMP 4\nHALT\nSTORE 8\nHALT\n20\n8\n0"
        self.code_text.insert("1.0", default_program)
        self.load_code_to_ram()

    def create_widgets(self):
        title = tk.Label(self.root, text="💻 Simulador Von Neumann - Animación de Buses", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#1e293b")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10)

        # ================= COLUMNA 1: EDITOR =================
        editor_frame = tk.LabelFrame(main_frame, text=" Editor (RAM) ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        editor_frame.pack(side="left", fill="y", padx=5)

        tk.Label(editor_frame, text="LOAD, STORE, ADD,\nSUB, JUMP, HALT", font=("Arial", 8, "italic"), bg="white", fg="#64748b", justify="left").pack(anchor="w", pady=(0, 5))
        self.code_text = tk.Text(editor_frame, font=("Consolas", 11), width=18, bg="#f8fafc", fg="#0f172a", bd=1, relief="solid")
        self.code_text.pack(fill="both", expand=True, pady=5)
        tk.Button(editor_frame, text="📥 Cargar", font=("Arial", 10, "bold"), bg="#0ea5e9", fg="white", command=self.load_code_to_ram).pack(fill="x")

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

        # ================= COLUMNA 3: BUSES (CANVAS ANIMADO) =================
        self.bus_canvas = tk.Canvas(main_frame, width=120, bg="#f0f2f5", highlightthickness=0)
        self.bus_canvas.pack(side="left", fill="y", padx=5)

        # Dibujar líneas estáticas que representen los buses
        self.bus_canvas.create_text(60, 80, text="Bus Direcciones", font=("Arial", 8, "bold"), fill="#64748b")
        self.bus_address = self.bus_canvas.create_line(10, 100, 110, 100, width=5, fill="#cbd5e1", arrow=tk.LAST)

        self.bus_canvas.create_text(60, 150, text="Bus de Datos", font=("Arial", 8, "bold"), fill="#64748b")
        self.bus_data = self.bus_canvas.create_line(10, 170, 110, 170, width=5, fill="#cbd5e1", arrow=tk.BOTH)

        # ================= COLUMNA 4: RAM =================
        mem_frame = tk.LabelFrame(main_frame, text=" RAM ", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        mem_frame.pack(side="left", fill="both", padx=5)

        self.mem_index_labels = []
        self.mem_val_labels = []
        for i in range(16):
            frame = tk.Frame(mem_frame, bg="white")
            frame.pack(fill="x", pady=1)
            idx_lbl = tk.Label(frame, text=f" [{i:02d}] ", font=("Consolas", 9, "bold"), bg="white", fg="#94a3b8")
            idx_lbl.pack(side="left", padx=2)
            val_lbl = tk.Label(frame, text="", font=("Consolas", 10), bg="#f8fafc", width=12, relief="solid", bd=1, anchor="w", padx=5)
            val_lbl.pack(side="left")
            self.mem_index_labels.append(idx_lbl)
            self.mem_val_labels.append(val_lbl)

        # ================= CONTROLES INFERIORES =================
        btn_frame = tk.Frame(self.root, bg="#f0f2f5", pady=10)
        btn_frame.pack(fill="x")

        # Controles de reproducción automática
        self.btn_play = tk.Button(btn_frame, text="▶️ Auto", font=("Arial", 10, "bold"), bg="#10b981", fg="white", command=self.play_sim, width=8)
        self.btn_play.pack(side="left", padx=(20, 5))

        self.btn_pause = tk.Button(btn_frame, text="⏸️ Pausa", font=("Arial", 10, "bold"), bg="#f59e0b", fg="white", command=self.pause_sim, state="disabled", width=8)
        self.btn_pause.pack(side="left", padx=5)

        self.speed_slider = tk.Scale(btn_frame, from_=0.2, to_=2.5, resolution=0.1, orient="horizontal", label="Velocidad (Seg/Paso)", bg="#f0f2f5", font=("Arial", 8))
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=15)

        # Botón clásico paso a paso
        self.btn_step = tk.Button(btn_frame, text="Siguiente Paso ⏭️", font=("Arial", 10, "bold"), bg="#3b82f6", fg="white", command=self.step_cycle, padx=10)
        self.btn_step.pack(side="left", padx=15)

        btn_reset = tk.Button(btn_frame, text="Reiniciar 🔄", font=("Arial", 10), bg="#ef4444", fg="white", command=self.reset_sim, padx=10)
        btn_reset.pack(side="right", padx=20)

    def load_code_to_ram(self):
        lines = self.code_text.get("1.0", tk.END).strip().split("\n")
        self.memory = [""] * 16
        idx = 0
        for line in lines:
            if line.strip() and idx < 16:
                self.memory[idx] = line.strip()
                idx += 1
        self.reset_sim()

    def update_gui_values(self):
        self.reg_labels["PC"].config(text=str(self.PC))
        self.reg_labels["MAR"].config(text=str(self.MAR))
        self.reg_labels["MDR"].config(text=str(self.MDR))
        self.reg_labels["IR"].config(text=str(self.IR))
        self.reg_labels["AC"].config(text=str(self.AC))
        self.alu_val_lbl.config(text=str(self.ALU))

        for i in range(16):
            self.mem_val_labels[i].config(text=self.memory[i], bg="#f8fafc")
            # Puntero dinámico del PC en la RAM
            if i == self.PC and self.cycle_state != 3:
                self.mem_index_labels[i].config(text=f"▶[{i:02d}]", fg="#b45309", bg="#fef08a")
            else:
                self.mem_index_labels[i].config(text=f" [{i:02d}] ", fg="#94a3b8", bg="white")

    def reset_highlights(self):
        for lbl in self.reg_labels.values():
            lbl.config(bg="#e2e8f0")
        self.alu_val_lbl.config(bg="white")
        # Apagar buses
        self.bus_canvas.itemconfig(self.bus_address, fill="#cbd5e1")
        self.bus_canvas.itemconfig(self.bus_data, fill="#cbd5e1")

    def safe_get_mem(self, addr):
        if addr is not None and 0 <= addr < 16:
            try: return int(self.memory[addr])
            except ValueError: return 0
        return 0

    # --- CONTROL DE AUTO-EJECUCIÓN ---
    def play_sim(self):
        if self.cycle_state == 3: return # HALTED
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
        
        # Calcular milisegundos desde el slider
        delay_ms = int(self.speed_slider.get() * 1000)
        self.root.after(delay_ms, self.auto_step)
    # ---------------------------------

    def step_cycle(self):
        if self.cycle_state == 3: return
        self.reset_highlights()

        # ====== 1. FETCH ======
        if self.cycle_state == 0:
            self.status_lbl.config(text="FETCH (Buscando instrucción...)", fg="#b45309")
            self.MAR = self.PC
            if self.MAR < 16:
                self.MDR = self.memory[self.MAR]
                self.mem_val_labels[self.MAR].config(bg="#fef3c7")
            else:
                self.MDR = "HALT"
            
            self.IR = self.MDR
            for k in ["PC", "MAR", "MDR", "IR"]: self.reg_labels[k].config(bg="#fef3c7")
            
            # Animación de Buses para Fetch (Naranja)
            self.bus_canvas.itemconfig(self.bus_address, fill="#f59e0b")
            self.bus_canvas.itemconfig(self.bus_data, fill="#f59e0b")

            self.PC += 1
            self.cycle_state = 1

        # ====== 2. DECODE ======
        elif self.cycle_state == 1:
            self.status_lbl.config(text="DECODE (Descifrando Comando)", fg="#1d4ed8")
            self.reg_labels["IR"].config(bg="#dbeafe")

            parts = self.IR.split()
            self.current_opcode = parts[0].upper() if parts else "NOP"
            try: self.current_operand = int(parts[1]) if len(parts) > 1 else None
            except ValueError: self.current_operand = None
            self.cycle_state = 2

        # ====== 3. EXECUTE ======
        elif self.cycle_state == 2:
            self.status_lbl.config(text=f"EXECUTE ({self.current_opcode})", fg="#15803d")
            op, addr = self.current_opcode, self.current_operand

            # Animación de Buses para Execute (Verde o Rojo según flujo)
            if op in ["LOAD", "ADD", "SUB"]:
                self.bus_canvas.itemconfig(self.bus_address, fill="#10b981") # Verde
                self.bus_canvas.itemconfig(self.bus_data, fill="#10b981")    # Verde
            elif op == "STORE":
                self.bus_canvas.itemconfig(self.bus_address, fill="#ef4444") # Rojo (escritura)
                self.bus_canvas.itemconfig(self.bus_data, fill="#ef4444")    # Rojo (escritura)

            if op == "LOAD":
                self.AC = self.safe_get_mem(addr)
                self.reg_labels["AC"].config(bg="#dcfce7")
                if addr is not None and addr < 16: self.mem_val_labels[addr].config(bg="#dcfce7")
                self.ALU = "---"

            elif op == "STORE":
                if addr is not None and 0 <= addr < 16:
                    self.memory[addr] = str(self.AC)
                    self.mem_val_labels[addr].config(bg="#fca5a5") # Rojo suave
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
    app = VonNeumannSimV3(root)
    root.mainloop()