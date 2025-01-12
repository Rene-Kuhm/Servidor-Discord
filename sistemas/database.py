import aiosqlite
import asyncio
import os
from typing import Dict, Any

class DatabaseManager:
    def __init__(self, db_path='d:/SERVIDOR DE DISCORD PROFECIONAL/discord_bot.db'):
        self.db_path = db_path
    
    async def connect(self):
        """Establecer conexión con la base de datos"""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
    
    async def close(self):
        """Cerrar conexión con la base de datos"""
        await self.conn.close()
    
    async def init_tables(self):
        """Crear tablas necesarias para el bot"""
        await self.connect()
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id INTEGER PRIMARY KEY,
                nombre TEXT,
                experiencia INTEGER DEFAULT 0,
                nivel INTEGER DEFAULT 1,
                insignias TEXT DEFAULT '[]',
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS roles_personalizados (
                role_id INTEGER PRIMARY KEY,
                nombre TEXT,
                descripcion TEXT,
                requisitos TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                fecha DATETIME,
                descripcion TEXT,
                canal TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS networking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,  
                descripcion TEXT,
                autor_id INTEGER,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS insignias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                descripcion TEXT,
                icono TEXT
            )
        ''')
        
        await self.conn.commit()
        await self.close()
    
    async def agregar_usuario(self, user_id: int, nombre: str):
        """Agregar un nuevo usuario a la base de datos"""
        await self.connect()
        await self.conn.execute(
            'INSERT OR IGNORE INTO usuarios (user_id, nombre) VALUES (?, ?)', 
            (user_id, nombre)
        )
        await self.conn.commit()
        await self.close()
    
    async def actualizar_experiencia(self, user_id: int, xp_ganada: int):
        """Actualizar experiencia de un usuario"""
        await self.connect()
        await self.conn.execute(
            'UPDATE usuarios SET experiencia = experiencia + ? WHERE user_id = ?',
            (xp_ganada, user_id)
        )
        await self.conn.commit()
        await self.close()
    
    async def obtener_usuario(self, user_id: int):
        """Obtener información de un usuario"""
        await self.connect()
        cursor = await self.conn.execute('SELECT * FROM usuarios WHERE user_id = ?', (user_id,))
        usuario = await cursor.fetchone()
        await self.close()
        return dict(usuario) if usuario else None
    
    async def registrar_evento(self, nombre: str, fecha: str, descripcion: str, canal: str = None):
        """Registrar un nuevo evento"""
        await self.connect()
        await self.conn.execute(
            'INSERT INTO eventos (nombre, fecha, descripcion, canal) VALUES (?, ?, ?, ?)', 
            (nombre, fecha, descripcion, canal)
        )
        await self.conn.commit()
        await self.close()
    
    async def obtener_eventos(self):
        """Obtener lista de eventos"""
        await self.connect()
        cursor = await self.conn.execute('SELECT * FROM eventos ORDER BY fecha')
        eventos = await cursor.fetchall()
        await self.close()
        return [dict(evento) for evento in eventos]

# Inicializar base de datos al importar
async def iniciar_base_datos():
    db_manager = DatabaseManager()
    await db_manager.init_tables()

# Ejecutar inicialización
if __name__ == '__main__':
    asyncio.run(iniciar_base_datos())
