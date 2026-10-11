import sqlite3
import os
from datetime import datetime

DB_PATH = "data/proyecto_audio.db"

def asegurar_directorios():
    os.makedirs("data", exist_ok=True)
    os.makedirs("audio_uploads", exist_ok=True)

def inicializar_base_datos():
    asegurar_directorios()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comentarios_audios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cliente_id INTEGER NOT NULL,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            archivo_audio TEXT NOT NULL,
            transcripcion TEXT,
            sentimiento TEXT NOT NULL,
            analisis TEXT NOT NULL,
            fecha_procesamiento TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    conn.commit()
    conn.close()

def obtener_o_crear_producto(nombre_producto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM productos WHERE nombre = ?", (nombre_producto,))
    row = cursor.fetchone()
    if row:
        prod_id = row[0]
    else:
        cursor.execute("INSERT INTO productos (nombre) VALUES (?)", (nombre_producto,))
        conn.commit()
        prod_id = cursor.lastrowid
    conn.close()
    return prod_id

def obtener_o_crear_cliente(nombre_cliente):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clientes WHERE nombre_usuario = ?", (nombre_cliente,))
    row = cursor.fetchone()
    if row:
        cli_id = row[0]
    else:
        cursor.execute("INSERT INTO clientes (nombre_usuario) VALUES (?)", (nombre_cliente,))
        conn.commit()
        cli_id = cursor.lastrowid
    conn.close()
    return cli_id

def guardar_comentario_audio(producto, cliente, likes, dislikes, archivo_audio, transcripcion, sentimiento, analisis, estado):
    prod_id = obtener_o_crear_producto(producto)
    cli_id = obtener_o_crear_cliente(cliente)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO comentarios_audios 
        (producto_id, cliente_id, likes, dislikes, archivo_audio, transcripcion, sentimiento, analisis, fecha_procesamiento, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (prod_id, cli_id, likes, dislikes, archivo_audio, transcripcion, sentimiento, analisis, fecha_actual, estado))
    conn.commit()
    conn.close()

def obtener_historial_completo():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, p.nombre, cl.nombre_usuario, c.likes, c.dislikes, c.archivo_audio, 
               c.transcripcion, c.sentimiento, c.analisis, c.fecha_procesamiento, c.estado
        FROM comentarios_audios c
        JOIN productos p ON c.producto_id = p.id
        JOIN clientes cl ON c.cliente_id = cl.id
        ORDER BY c.id DESC
    """)
    registros = cursor.fetchall()
    conn.close()
    return registros