import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import os

st.set_page_config(
    page_title="Kelly Nails - Gestión Financiera",
    page_icon="💅",
    layout="wide"
)

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar datos
def cargar_atenciones():
    try:
        df = conn.read(worksheet="atenciones", ttl="0s")
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["id", "fecha", "clienta", "servicio", "monto"])

def cargar_deudas():
    try:
        df = conn.read(worksheet="deudas", ttl="0s")
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["id", "acreedor", "monto_total", "cuotas_totales", "cuotas_pagadas", "valor_cuota", "estado"])

# Mostrar Logo y Título
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.PNG"):
        st.image("logo.PNG", width=100)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=100)
    else:
        st.write("💅")
with col_titulo:
    st.title("Gestor Financiero - Kelly Nails")

st.markdown("---")

# Menú lateral
if os.path.exists("logo.PNG"):
    st.sidebar.image("logo.PNG")
elif os.path.exists("logo.png"):
    st.sidebar.image("logo.png")

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
            df_existing = cargar_atenciones()
            nuevo_id = 1 if df_existing.empty else int(df_existing["id"].max()) + 1
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            nuevo_registro = pd.DataFrame([{
                "id": nuevo_id,
                "fecha": fecha_actual,
                "clienta": clienta,
                "servicio": servicio,
                "monto": monto
            }])
            
            df_updated = pd.concat([df_existing, nuevo_registro], ignore_index=True)
            conn.update(worksheet="atenciones", data=df_updated)
            st.success(f"¡Atención guardada en la nube para {clienta} por ${monto:,.0f}!")

# --- OPCIÓN 2: HISTORIAL E INGRESOS ---
elif opcion == "Historial e Ingresos":
    st.header("📊 Historial de Ingresos")
    
    df = cargar_atenciones()

    if not df.empty:
        df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)
        df["fecha"] = df["fecha"].astype(str)
        df = df.sort_values(by="id", ascending=False)

        hoy_str = datetime.now().strftime("%Y-%m-%d")
        mes_str = datetime.now().strftime("%Y-%m")

        total_hoy = df[df['fecha'].str.startswith(hoy_str)]['monto'].sum()
        total_mes = df[df['fecha'].str.startswith(mes_str)]['monto'].sum()
        total_acumulado = df['monto'].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Hoy", f"${total_hoy:,.0f}")
        m2.metric("Ingresos Este Mes", f"${total_mes:,.0f}")
        m3.metric("Total Acumulado", f"${total_acumulado:,.0f}")

        st.subheader("Tabla de Registros")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("🛠️ Administrar / Eliminar Registros")
        
        col_del, col_edit = st.columns(2)

        with col_del:
            st.markdown("##### ❌ Eliminar Registro Error")
            id_eliminar = st.number_input("ID a Eliminar:", min_value=1, step=1, key="del_id")
            if st.button("🗑️ Borrar Servicio", use_container_width=True):
                df_filtrado = df[df["id"] != id_eliminar]
                conn.update(worksheet="atenciones", data=df_filtrado)
                st.success(f"Registro ID {id_eliminar} eliminado permanentemente.")
                st.rerun()

        with col_edit:
            st.markdown("##### ✏️ Editar Registro")
            id_editar = st.number_input("ID a Modificar:", min_value=1, step=1, key="edit_id")
            row_edit = df[df["id"] == id_editar]

            if not row_edit.empty:
                r = row_edit.iloc[0]
                c_edit = st.text_input("Clienta:", value=str(r["clienta"]))
                s_edit = st.text_input("Servicio:", value=str(r["servicio"]))
                m_edit = st.number_input("Monto ($):", value=float(r["monto"]), step=1000.0)

                if st.button("💾 Actualizar Registro", use_container_width=True):
                    df.loc[df["id"] == id_editar, ["clienta", "servicio", "monto"]] = [c_edit, s_edit, m_edit]
                    conn.update(worksheet="atenciones", data=df)
                    st.success(f"Registro ID {id_editar} actualizado.")
                    st.rerun()
            else:
                st.info("Ingresa un ID válido para editar.")
    else:
        st.info("Aún no hay atenciones registradas.")

# --- OPCIÓN 3: DEUDAS Y BALANCE GENERAL ---
elif opcion == "Deudas y Balance General":
    st.header("⚖️ Control de Deudas y Balance General")
    
    df_atenciones = cargar_atenciones()
    total_ingresos = pd.to_numeric(df_atenciones["monto"], errors="coerce").sum() if not df_atenciones.empty else 0.0

    df_deudas = cargar_deudas()

    if not df_deudas.empty:
        df_deudas["monto_total"] = pd.to_numeric(df_deudas["monto_total"], errors="coerce").fillna(0)
        df_deudas["cuotas_totales"] = pd.to_numeric(df_deudas["cuotas_totales"], errors="coerce").fillna(1)
        df_deudas["cuotas_pagadas"] = pd.to_numeric(df_deudas["cuotas_pagadas"], errors="coerce").fillna(0)
        df_deudas["valor_cuota"] = pd.to_numeric(df_deudas["valor_cuota"], errors="coerce").fillna(0)
        
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
                nuevo_id = 1 if df_deudas.empty else int(df_deudas["id"].max()) + 1
                valor_cuota = monto_deuda / cuotas
                nueva_deuda = pd.DataFrame([{
                    "id": nuevo_id,
                    "acreedor": acreedor,
                    "monto_total": monto_deuda,
                    "cuotas_totales": cuotas,
                    "cuotas_pagadas": 0,
                    "valor_cuota": valor_cuota,
                    "estado": "PENDIENTE"
                }])
                df_updated_deudas = pd.concat([df_deudas, nueva_deuda], ignore_index=True)
                conn.update(worksheet="deudas", data=df_updated_deudas)
                st.success(f"Deuda guardada para {acreedor}.")
                st.rerun()

        st.subheader("Abonar Cuota")
        with st.form("form_abono", clear_on_submit=True):
            id_deuda = st.number_input("ID de Deuda:", min_value=1, step=1)
            pagar_c = st.form_submit_button("💳 Pagar 1 Cuota", use_container_width=True)

        if pagar_c:
            if not df_deudas.empty and id_deuda in df_deudas["id"].values:
                row_idx = df_deudas[df_deudas["id"] == id_deuda].index[0]
                c_tot = df_deudas.loc[row_idx, "cuotas_totales"]
                c_pag = df_deudas.loc[row_idx, "cuotas_pagadas"]

                if c_pag >= c_tot:
                    st.info("Esta deuda ya está cancelada en su totalidad.")
                else:
                    nuevas_pag = c_pag + 1
                    estado = "PAGADA" if nuevas_pag == c_tot else "PENDIENTE"
                    df_deudas.loc[row_idx, ["cuotas_pagadas", "estado"]] = [nuevas_pag, estado]
                    conn.update(worksheet="deudas", data=df_deudas)
                    st.success(f"¡Cuota {nuevas_pag}/{c_tot} registrada con éxito!")
                    st.rerun()
            else:
                st.error("No existe una deuda con ese ID.")

    with col_tabla:
        st.subheader("Listado de Deudas")
        if not df_deudas.empty:
            st.dataframe(
                df_deudas[['id', 'acreedor', 'cuotas_pagadas', 'cuotas_totales', 'valor_cuota', 'saldo_pendiente', 'estado']],
                use_container_width=True
            )
        else:
            st.info("No hay deudas registradas.")