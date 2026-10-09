import customtkinter as ctk
from datetime import datetime
from database import inicializar_bd, obtener_conexion
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppGestion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control de Ingresos y Deudas - Kelly Nails")
        self.geometry("980x700")

        # Inicializar la base de datos
        inicializar_bd()

        # Título principal
        self.lbl_titulo = ctk.CTkLabel(
            self, 
            text="💅 Gestor Financiero - Kelly Nails 💅", 
            font=("Arial", 22, "bold")
        )
        self.lbl_titulo.pack(pady=10)

        # Panel de Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.tab_registro = self.tabview.add("Registrar Atención")
        self.tab_historial = self.tabview.add("Historial e Ingresos")
        self.tab_deudas = self.tabview.add("Deudas y Balance General")

        self.setup_tab_registro()
        self.setup_tab_historial()
        self.setup_tab_deudas()

    # --- PESTAÑA 1: REGISTRAR ATENCIÓN ---
    def setup_tab_registro(self):
        f = ctk.CTkFrame(self.tab_registro)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(f, text="Nueva Atención / Trabajo Realizado", font=("Arial", 16, "bold")).pack(pady=15)

        f_form = ctk.CTkFrame(f, fg_color="transparent")
        f_form.pack(pady=10)

        # Nombre Clienta
        ctk.CTkLabel(f_form, text="Nombre de la Clienta:", font=("Arial", 13)).grid(row=0, column=0, sticky="w", pady=8, padx=10)
        self.txt_clienta = ctk.CTkEntry(f_form, width=250, placeholder_text="Ej. Maria Lopez")
        self.txt_clienta.grid(row=0, column=1, pady=8, padx=10)

        # Servicio
        ctk.CTkLabel(f_form, text="Servicio Realizado:", font=("Arial", 13)).grid(row=1, column=0, sticky="w", pady=8, padx=10)
        self.txt_servicio = ctk.CTkEntry(f_form, width=250, placeholder_text="Ej. Semipermanente + Acrílico")
        self.txt_servicio.grid(row=1, column=1, pady=8, padx=10)

        # Monto
        ctk.CTkLabel(f_form, text="Monto Cobrado ($):", font=("Arial", 13)).grid(row=2, column=0, sticky="w", pady=8, padx=10)
        self.txt_monto = ctk.CTkEntry(f_form, width=250, placeholder_text="Ej. 45000")
        self.txt_monto.grid(row=2, column=1, pady=8, padx=10)

        btn_guardar = ctk.CTkButton(
            f, 
            text="GUARDAR ATENCIÓN", 
            font=("Arial", 13, "bold"),
            fg_color="#D63384", 
            hover_color="#B8256F",
            command=self.guardar_atencion
        )
        btn_guardar.pack(pady=20)

    def guardar_atencion(self):
        clienta = self.txt_clienta.get().strip()
        servicio = self.txt_servicio.get().strip()
        monto_str = self.txt_monto.get().strip()

        if not clienta or not servicio or not monto_str:
            messagebox.showerror("Error", "Por favor completa todos los campos.")
            return

        try:
            monto = float(monto_str.replace(",", "").replace(".", ""))
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO atenciones (fecha, clienta, servicio, monto) VALUES (?, ?, ?, ?)",
                    (fecha_actual, clienta, servicio, monto)
                )
                conn.commit()

            messagebox.showinfo("Éxito", f"¡Atención guardada correctamente para {clienta}!")
            self.txt_clienta.delete(0, "end")
            self.txt_servicio.delete(0, "end")
            self.txt_monto.delete(0, "end")
            
            self.cargar_historial_e_ingresos()
            self.actualizar_balance_general()

        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido en el monto.")

    # --- PESTAÑA 2: HISTORIAL E INGRESOS ---
    def setup_tab_historial(self):
        f = ctk.CTkFrame(self.tab_historial)
        f.pack(fill="both", expand=True, padx=15, pady=15)

        f_totales = ctk.CTkFrame(f)
        f_totales.pack(fill="x", padx=10, pady=10)

        self.lbl_hoy = ctk.CTkLabel(f_totales, text="Hoy: $0", font=("Arial", 14, "bold"))
        self.lbl_hoy.pack(side="left", expand=True, pady=10)

        self.lbl_mes = ctk.CTkLabel(f_totales, text="Este Mes: $0", font=("Arial", 14, "bold"))
        self.lbl_mes.pack(side="left", expand=True, pady=10)

        self.lbl_total = ctk.CTkLabel(f_totales, text="Total Acumulado: $0", font=("Arial", 14, "bold"))
        self.lbl_total.pack(side="left", expand=True, pady=10)

        self.txt_historial = ctk.CTkTextbox(f, font=("Consolas", 11))
        self.txt_historial.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_historial_e_ingresos()

    def cargar_historial_e_ingresos(self):
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, clienta, servicio, monto FROM atenciones ORDER BY id DESC")
            registros = cursor.fetchall()

        hoy_str = datetime.now().strftime("%Y-%m-%d")
        mes_str = datetime.now().strftime("%Y-%m")

        total_hoy = 0
        total_mes = 0
        total_acumulado = 0

        texto_historial = f"{'FECHA/HORA':<20} | {'CLIENTA':<20} | {'SERVICIO':<30} | {'MONTO':>10}\n"
        texto_historial += "="*88 + "\n"

        for fecha, clienta, servicio, monto in registros:
            total_acumulado += monto
            if fecha.startswith(hoy_str):
                total_hoy += monto
            if fecha.startswith(mes_str):
                total_mes += monto

            texto_historial += f"{fecha:<20} | {clienta[:18]:<20} | {servicio[:28]:<30} | ${monto:>9,.0f}\n"

        self.lbl_hoy.configure(text=f"Hoy: ${total_hoy:,.0f}")
        self.lbl_mes.configure(text=f"Este Mes: ${total_mes:,.0f}")
        self.lbl_total.configure(text=f"Total Acumulado: ${total_acumulado:,.0f}")

        self.txt_historial.configure(state="normal")
        self.txt_historial.delete("1.0", "end")
        self.txt_historial.insert("1.0", texto_historial)
        self.txt_historial.configure(state="disabled")

    # --- PESTAÑA 3: DEUDAS Y BALANCE ---
    def setup_tab_deudas(self):
        grid_frame = ctk.CTkFrame(self.tab_deudas, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel Izquierdo: Formulario de Nueva Deuda
        f_left = ctk.CTkFrame(grid_frame)
        f_left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(f_left, text="Registrar Nueva Deuda / Crédito", font=("Arial", 14, "bold")).pack(pady=10)

        f_form = ctk.CTkFrame(f_left, fg_color="transparent")
        f_form.pack(pady=5, padx=10)

        ctk.CTkLabel(f_form, text="A quién le debe:").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_acreedor = ctk.CTkEntry(f_form, width=180, placeholder_text="Ej. Proveedor Esmaltes")
        self.txt_acreedor.grid(row=0, column=1, pady=5, padx=5)

        ctk.CTkLabel(f_form, text="Monto Total ($):").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_monto_deuda = ctk.CTkEntry(f_form, width=180, placeholder_text="Ej. 300000")
        self.txt_monto_deuda.grid(row=1, column=1, pady=5, padx=5)

        ctk.CTkLabel(f_form, text="Nº de Cuotas:").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_cuotas = ctk.CTkEntry(f_form, width=180, placeholder_text="Ej. 6")
        self.txt_cuotas.grid(row=2, column=1, pady=5, padx=5)

        btn_guardar_deuda = ctk.CTkButton(
            f_left, 
            text="GUARDAR DEUDA", 
            fg_color="#C9302C", 
            hover_color="#A9221F",
            command=self.guardar_deuda
        )
        btn_guardar_deuda.pack(pady=15)

        # Panel de Pagar Cuota Rápida
        ctk.CTkLabel(f_left, text="Abonar / Pagar Cuota", font=("Arial", 13, "bold")).pack(pady=(10, 5))
        f_abono = ctk.CTkFrame(f_left, fg_color="transparent")
        f_abono.pack(pady=5)

        ctk.CTkLabel(f_abono, text="ID Deuda:").grid(row=0, column=0, padx=5)
        self.txt_id_deuda = ctk.CTkEntry(f_abono, width=60)
        self.txt_id_deuda.grid(row=0, column=1, padx=5)

        btn_pagar_cuota = ctk.CTkButton(f_abono, text="PAGAR 1 CUOTA", fg_color="#28A745", hover_color="#218838", command=self.pagar_cuota)
        btn_pagar_cuota.grid(row=0, column=2, padx=5)

        # Panel Derecho: Balance General y Lista
        f_right = ctk.CTkFrame(grid_frame)
        f_right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Tarjeta de Estado / Balance
        self.frame_balance = ctk.CTkFrame(f_right, fg_color="#1E1E1E")
        self.frame_balance.pack(fill="x", padx=10, pady=10)

        self.lbl_balance_estado = ctk.CTkLabel(
            self.frame_balance, 
            text="BALANCE GENERAL: $0", 
            font=("Arial", 15, "bold")
        )
        self.lbl_balance_estado.pack(pady=10)

        self.txt_deudas = ctk.CTkTextbox(f_right, font=("Consolas", 10))
        self.txt_deudas.pack(fill="both", expand=True, padx=10, pady=10)

        self.actualizar_balance_general()

    def guardar_deuda(self):
        acreedor = self.txt_acreedor.get().strip()
        monto_str = self.txt_monto_deuda.get().strip()
        cuotas_str = self.txt_cuotas.get().strip()

        if not acreedor or not monto_str or not cuotas_str:
            messagebox.showerror("Error", "Completa todos los campos de la deuda.")
            return

        try:
            monto_total = float(monto_str.replace(",", "").replace(".", ""))
            cuotas_totales = int(cuotas_str)
            valor_cuota = monto_total / cuotas_totales

            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO deudas (acreedor, monto_total, cuotas_totales, cuotas_pagadas, valor_cuota, estado) VALUES (?, ?, ?, 0, ?, 'PENDIENTE')",
                    (acreedor, monto_total, cuotas_totales, valor_cuota)
                )
                conn.commit()

            messagebox.showinfo("Éxito", f"Deuda registrada con {acreedor}.")
            self.txt_acreedor.delete(0, "end")
            self.txt_monto_deuda.delete(0, "end")
            self.txt_cuotas.delete(0, "end")

            self.actualizar_balance_general()
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos en Monto y Cuotas.")

    def pagar_cuota(self):
        id_str = self.txt_id_deuda.get().strip()
        if not id_str:
            messagebox.showerror("Error", "Ingresa el ID de la deuda a abonar.")
            return

        try:
            id_deuda = int(id_str)
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cuotas_totales, cuotas_pagadas FROM deudas WHERE id = ?", (id_deuda,))
                row = cursor.fetchone()

                if not row:
                    messagebox.showerror("Error", "No existe ninguna deuda con ese ID.")
                    return

                cuotas_totales, cuotas_pagadas = row
                if cuotas_pagadas >= cuotas_totales:
                    messagebox.showinfo("Información", "Esta deuda ya está totalmente pagada.")
                    return

                nuevas_pagadas = cuotas_pagadas + 1
                nuevo_estado = "PAGADA" if nuevas_pagadas == cuotas_totales else "PENDIENTE"

                cursor.execute(
                    "UPDATE deudas SET cuotas_pagadas = ?, estado = ? WHERE id = ?",
                    (nuevas_pagadas, nuevo_estado, id_deuda)
                )
                conn.commit()

            messagebox.showinfo("Éxito", f"¡Cuota {nuevas_pagadas}/{cuotas_totales} registrada con éxito!")
            self.txt_id_deuda.delete(0, "end")
            self.actualizar_balance_general()

        except ValueError:
            messagebox.showerror("Error", "Ingresa un ID numérico válido.")

    def actualizar_balance_general(self):
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Suma de Ingresos
            cursor.execute("SELECT SUM(monto) FROM atenciones")
            total_ingresos = cursor.fetchone()[0] or 0.0

            # Consultar Deudas
            cursor.execute("SELECT id, acreedor, monto_total, cuotas_totales, cuotas_pagadas, valor_cuota, estado FROM deudas")
            deudas = cursor.fetchall()

        total_deuda_pendiente = 0.0
        texto_deudas = f"{'ID':<3} | {'ACREEDOR':<18} | {'PAGADO/TOTAL':<12} | {'VALOR CUOTA':<12} | {'PENDIENTE':>10}\n"
        texto_deudas += "="*68 + "\n"

        for id_d, acreedor, monto_total, c_totales, c_pagadas, val_cuota, estado in deudas:
            saldo_pendiente = monto_total - (c_pagadas * val_cuota)
            if estado == "PENDIENTE":
                total_deuda_pendiente += saldo_pendiente

            cuotas_str = f"{c_pagadas}/{c_totales}"
            texto_deudas += f"{id_d:<3} | {acreedor[:16]:<18} | {cuotas_str:<12} | ${val_cuota:>10,.0f} | ${saldo_pendiente:>9,.0f}\n"

        balance_neto = total_ingresos - total_deuda_pendiente

        if balance_neto >= 0:
            txt_balance = f"🟢 BALANCE EN POSITIVO: +${balance_neto:,.0f}\n(Ingresos: ${total_ingresos:,.0f} | Deudas Pendientes: ${total_deuda_pendiente:,.0f})"
            color_balance = "#28A745"
        else:
            txt_balance = f"🔴 BALANCE EN DÉFICIT: -${abs(balance_neto):,.0f}\n(Ingresos: ${total_ingresos:,.0f} | Deudas Pendientes: ${total_deuda_pendiente:,.0f})"
            color_balance = "#D9534F"

        self.lbl_balance_estado.configure(text=txt_balance, text_color=color_balance)

        self.txt_deudas.configure(state="normal")
        self.txt_deudas.delete("1.0", "end")
        self.txt_deudas.insert("1.0", texto_deudas)
        self.txt_deudas.configure(state="disabled")

if __name__ == "__main__":
    app = AppGestion()
    app.mainloop()