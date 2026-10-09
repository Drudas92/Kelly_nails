import sqlite3

DB_NAME = "gestion_negocio.db"

def obtener_conexion():
    return sqlite3.connect(DB_NAME)

def inicializar_bd():
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # Tabla de Atenciones / Servicios cobrados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atenciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                clienta TEXT NOT NULL,
                servicio TEXT NOT NULL,
                monto REAL NOT NULL
            )
        """)
        
        # Tabla de Deudas / Cuentas por Pagar
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deudas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acreedor TEXT NOT NULL,
                monto_total REAL NOT NULL,
                cuotas_totales INTEGER NOT NULL,
                cuotas_pagadas INTEGER DEFAULT 0,
                valor_cuota REAL NOT NULL,
                estado TEXT DEFAULT 'PENDIENTE'
            )
        """)
        
        conn.commit()

if __name__ == "__main__":
    inicializar_bd()
    print("Base de datos inicializada correctamente.")