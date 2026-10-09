import streamlit as st
import pandas as pd
from datetime import datetime
from database import inicializar_bd, obtener_conexion

st.set_page_config(
    page_title="Kelly Nails - Gestión Financiera",
    page_icon="💅",
    layout="wide"
)

inicializar_bd()

# Mostrar Logo y Título
# Reemplazar por:
import os

col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("💅")
with col_titulo:
    st.title("Gestor Financiero - Kelly Nails")

st.markdown("---")

# Menú lateral
st.sidebar.image("logo.png", use_container_width=True)
opcion = st.sidebar.radio(
    "Navegación",
    ["Registrar Atención", "Historial e Ingresos", "Deudas y Balance General"]
)

# --- OPCIÓN 1: REGISTRAR ATENCIÓN ---
if opcion == "Registrar Atención":
    st.header("📝 Registrar Nueva Atención")
    
    with st.form("form_atencion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            clienta = st.text_input("Nombre de la Clienta:", placeholder="Ej. María López")
            servicio = st.text_input("Servicio Realizado:", placeholder="Ej. Semipermanente + Acrílico")
        with col2:
            monto = st.number_input("Monto Cobrado ($):", min_value=0.0, step=1000.0, format="%.0f")
        
        guardar = st.form_submit_button("💾 Guardar Atención", use_container_width=True)

    if guardar:
        if not clienta or not servicio or monto <= 0:
            st.error("Por favor completa todos los campos con un monto válido.")
        else:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO atenciones (fecha, clienta, servicio, monto) VALUES (?, ?, ?, ?)",
                    (fecha_actual, clienta, servicio, monto)
                )
                conn.commit()
            st.success(f"¡Atención guardada correctamente para {clienta} por ${monto:,.0f}!")

# --- OPCIÓN 2: HISTORIAL E INGRESOS (CON EDICIÓN Y ELIMINACIÓN) ---
elif opcion == "Historial e Ingresos":
    st.header("📊 Historial de Ingresos")
    
    with obtener_conexion() as conn:
        df = pd.read_sql_query("SELECT id, fecha, clienta, servicio, monto FROM atenciones ORDER BY id DESC", conn)

    if not df.empty:
        # Calcular Totales
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        mes_str = datetime.now().strftime("%Y-%m")

        total_hoy = df[df['fecha'].str.startswith(hoy_str)]['monto'].sum()
        total_mes = df[df['fecha'].str.startswith(mes_str)]['monto'].sum()
        total_acumulado = df['monto'].sum()

        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Hoy", f"${total_hoy:,.0f}")
        m2.metric("Ingresos Este Mes", f"${total_mes:,.0f}")
        m3.metric("Total Acumulado", f"${total_acumulado:,.0f}")

        st.subheader("Tabla de Registros")
        st.dataframe(df, use_container_width=True)

        excel_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte en CSV / Excel",
            data=excel_data,
            file_name=f"Reporte_KellyNails_{hoy_str}.csv",
            mime="text/csv"
        )

        st.markdown("---")
        st.subheader("🛠️ Administrar / Eliminar Registros")
        
        col_del, col_edit = st.columns(2)

        # Panel de Eliminación
        with col_del:
            st.markdown("##### ❌ Eliminar Registro Error")
            id_eliminar = st.number_input("ID a Eliminar:", min_value=1, step=1, key="del_id")
            if st.button("🗑️ Borrar Servicio", use_container_width=True):
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM atenciones WHERE id = ?", (id_eliminar,))
                    conn.commit()
                st.success(f"Registro ID {id_eliminar} eliminado.")
                st.rerun()

        # Panel de Edición Rápida
        with col_edit:
            st.markdown("##### ✏️ Editar Registro")
            id_editar = st.number_input("ID a Modificar:", min_value=1, step=1, key="edit_id")
            
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT clienta, servicio, monto FROM atenciones WHERE id = ?", (id_editar,))
                row_edit = cursor.fetchone()

            if row_edit:
                c_edit = st.text_input("Clienta:", value=row_edit[0])
                s_edit = st.text_input("Servicio:", value=row_edit[1])
                m_edit = st.number_input("Monto ($):", value=float(row_edit[2]), step=1000.0)

                if st.button("💾 Actualizar Registro", use_container_width=True):
                    with obtener_conexion() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE atenciones SET clienta = ?, servicio = ?, monto = ? WHERE id = ?",
                            (c_edit, s_edit, m_edit, id_editar)
                        )
                        conn.commit()
                    st.success(f"Registro ID {id_editar} actualizado.")
                    st.rerun()
            else:
                st.info("Ingresa un ID válido para editar.")

    else:
        st.info("Aún no hay atenciones registradas.")

# --- OPCIÓN 3: DEUDAS Y BALANCE GENERAL ---
elif opcion == "Deudas y Balance General":
    st.header("⚖️ Control de Deudas y Balance General")
    
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(monto) FROM atenciones")
        total_ingresos = cursor.fetchone()[0] or 0.0

        df_deudas = pd.read_sql_query(
            "SELECT id, acreedor, monto_total, cuotas_totales, cuotas_pagadas, valor_cuota, estado FROM deudas", 
            conn
        )

    if not df_deudas.empty:
        df_deudas['monto_pagado'] = df_deudas['cuotas_pagadas'] * df_deudas['valor_cuota']
        df_deudas['saldo_pendiente'] = df_deudas['monto_total'] - df_deudas['monto_pagado']
        total_deuda_pendiente = df_deudas[df_deudas['estado'] == 'PENDIENTE']['saldo_pendiente'].sum()
    else:
        total_deuda_pendiente = 0.0

    balance_neto = total_ingresos - total_deuda_pendiente

    b1, b2, b3 = st.columns(3)
    b1.metric("Total Ingresos", f"${total_ingresos:,.0f}")
    b2.metric("Deudas Pendientes", f"${total_deuda_pendiente:,.0f}")
    
    if balance_neto >= 0:
        b3.metric("Balance Neto", f"+${balance_neto:,.0f}", delta="POSITIVO 🟢")
    else:
        b3.metric("Balance Neto", f"-${abs(balance_neto):,.0f}", delta="-DÉFICIT 🔴", delta_color="inverse")

    st.markdown("---")

    col_form, col_tabla = st.columns([1, 1.5])

    with col_form:
        st.subheader("Registrar Deuda")
        with st.form("form_deuda", clear_on_submit=True):
            acreedor = st.text_input("A quién le debe:", placeholder="Ej. Proveedor Esmaltes")
            monto_deuda = st.number_input("Monto Total ($):", min_value=0.0, step=10000.0)
            cuotas = st.number_input("Número de Cuotas:", min_value=1, step=1, value=1)
            guardar_d = st.form_submit_button("📌 Registrar Deuda", use_container_width=True)

        if guardar_d:
            if not acreedor or monto_deuda <= 0:
                st.error("Completa los datos de la deuda correctamente.")
            else:
                valor_cuota = monto_deuda / cuotas
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO deudas (acreedor, monto_total, cuotas_totales, cuotas_pagadas, valor_cuota, estado) VALUES (?, ?, ?, 0, ?, 'PENDIENTE')",
                        (acreedor, monto_deuda, cuotas, valor_cuota)
                    )
                    conn.commit()
                st.success(f"Deuda guardada para {acreedor}.")
                st.rerun()

        st.subheader("Abonar Cuota")
        with st.form("form_abono", clear_on_submit=True):
            id_deuda = st.number_input("ID de Deuda:", min_value=1, step=1)
            pagar_c = st.form_submit_button("💳 Pagar 1 Cuota", use_container_width=True)

        if pagar_c:
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT cuotas_totales, cuotas_pagadas FROM deudas WHERE id = ?", (id_deuda,))
                row = cursor.fetchone()

                if not row:
                    st.error("No existe una deuda con ese ID.")
                else:
                    c_tot, c_pag = row
                    if c_pag >= c_tot:
                        st.info("Esta deuda ya está cancelada en su totalidad.")
                    else:
                        nuevas_pag = c_pag + 1
                        estado = "PAGADA" if nuevas_pag == c_tot else "PENDIENTE"
                        cursor.execute(
                            "UPDATE deudas SET cuotas_pagadas = ?, estado = ? WHERE id = ?",
                            (nuevas_pag, estado, id_deuda)
                        )
                        conn.commit()
                        st.success(f"¡Cuota {nuevas_pag}/{c_tot} registrada con éxito!")
                        st.rerun()

    with col_tabla:
        st.subheader("Listado de Deudas")
        if not df_deudas.empty:
            st.dataframe(
                df_deudas[['id', 'acreedor', 'cuotas_pagadas', 'cuotas_totales', 'valor_cuota', 'saldo_pendiente', 'estado']],
                use_container_width=True
            )
        else:
            st.info("No hay deudas registradas.")