# Importaciones y configuración
import os
import sys
import logging
import traceback
import threading
import datetime
import random
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from flask import Flask
import asyncio
import sqlite3
from datetime import datetime, timedelta
import re
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from transformers import pipeline

# Descargar recursos de NLTK
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("No se pudieron descargar recursos de NLTK")

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', mode='w'),
        logging.StreamHandler(sys.stdout)  # Salida a consola
    ]
)
logger = logging.getLogger('discord_bot')

# Configuración de intents con todos los permisos
intents = discord.Intents.all()

# Crear bot con prefijo de comandos
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Tarea en segundo plano para monitoreo
@tasks.loop(minutes=30)
async def status_task():
    try:
        logger.info("Actualizando estado del bot...")
        await bot.change_presence(
            status=discord.Status.online, 
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"Servidores: {len(bot.guilds)}"
            )
        )
    except Exception as e:
        logger.error(f"Error en tarea de estado: {e}")

# Configuración de base de datos de moderación
def init_mod_database():
    """Inicializar base de datos de moderación"""
    try:
        conn = sqlite3.connect('moderation.db')
        cursor = conn.cursor()
        
        # Tabla de advertencias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER,
                guild_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp DATETIME,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabla de sanciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sanctions (
                user_id INTEGER,
                guild_id INTEGER,
                type TEXT,
                duration INTEGER,
                reason TEXT,
                timestamp DATETIME,
                active INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos de moderación inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando base de datos de moderación: {e}")

# Configuración de IA conversacional
class AIAssistant:
    def __init__(self):
        try:
            # Inicializar modelo de generación de texto
            self.generator = pipeline('text-generation', model='gpt2-medium')
            
            # Cargar contexto y personalidad
            self.context = {
                "nombre": "TDPBot",
                "personalidad": "Un asistente inteligente, amable y servicial",
                "conocimientos": ["tecnología", "programación", "discord", "comunidad"]
            }
            
            # Cargar frases de inicio
            self.conversation_starters = [
                "Hola, ¿en qué puedo ayudarte hoy?",
                "Estoy aquí para asistirte. ¿Qué necesitas?",
                "¿Cómo puedo ser de ayuda?"
            ]
        except Exception as e:
            logger.error(f"Error inicializando AI Assistant: {e}")
            self.generator = None
    
    def generar_respuesta(self, mensaje, contexto=None):
        """Genera una respuesta coherente"""
        if not self.generator:
            return "Lo siento, mi sistema de IA está temporalmente desactivado."
        
        try:
            # Preprocesar mensaje
            mensaje = re.sub(r'[^\w\s]', '', mensaje.lower())
            tokens = word_tokenize(mensaje)
            tokens = [w for w in tokens if w not in stopwords.words('spanish')]
            
            # Construir prompt
            prompt = f"""Contexto: Eres {self.context['nombre']}, {self.context['personalidad']}.
Mensaje del usuario: {mensaje}
Respuesta inteligente y contextual:"""
            
            # Generar respuesta
            respuestas = self.generator(
                prompt, 
                max_length=150, 
                num_return_sequences=3,
                temperature=0.7
            )
            
            # Seleccionar la respuesta más coherente
            respuesta = max(respuestas, key=lambda x: len(x['generated_text']))['generated_text']
            
            # Limpiar y formatear
            respuesta = respuesta.split('Respuesta inteligente y contextual:')[-1].strip()
            respuesta = re.sub(r'\s+', ' ', respuesta)
            
            return respuesta
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return random.choice(self.conversation_starters)

# Inicializar asistente de IA
ai_assistant = AIAssistant()

# Importaciones adicionales
import json
import os

# Base de datos de comandos del servidor
class ServerCommandManager:
    def __init__(self):
        # Ruta para almacenar configuraciones de comandos por servidor
        self.config_dir = 'server_configs'
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _get_config_path(self, guild_id):
        """Obtener ruta de configuración para un servidor"""
        return os.path.join(self.config_dir, f'{guild_id}_commands.json')
    
    def registrar_comando_personalizado(self, guild_id, comando, descripcion, categoria='Personalizado'):
        """Registrar un nuevo comando personalizado para el servidor"""
        try:
            config_path = self._get_config_path(guild_id)
            
            # Cargar configuración existente
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"comandos_personalizados": []}
            
            # Añadir nuevo comando
            nuevo_comando = {
                "nombre": comando,
                "descripcion": descripcion,
                "categoria": categoria
            }
            
            # Evitar duplicados
            if not any(cmd['nombre'] == comando for cmd in config['comandos_personalizados']):
                config['comandos_personalizados'].append(nuevo_comando)
            
            # Guardar configuración
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Error registrando comando personalizado: {e}")
            return False
    
    def obtener_comandos_servidor(self, guild_id):
        """Obtener todos los comandos disponibles para un servidor"""
        try:
            config_path = self._get_config_path(guild_id)
            
            # Comandos base del bot
            comandos_base = {
                "Información": [
                    {"nombre": "!ping", "descripcion": "Muestra la latencia del bot"},
                    {"nombre": "!info", "descripcion": "Información básica del bot"},
                    {"nombre": "!diagnostico", "descripcion": "Diagnóstico de permisos (Solo Administradores)"},
                    {"nombre": "!servidor", "descripcion": "Información del servidor actual"},
                    {"nombre": "!miembro", "descripcion": "Información de un miembro específico"},
                    {"nombre": "!avatar", "descripcion": "Muestra el avatar de un usuario"}
                ],
                "Moderación": [
                    {"nombre": "!kick", "descripcion": "Expulsa a un miembro"},
                    {"nombre": "!ban", "descripcion": "Banea a un miembro"},
                    {"nombre": "!clear", "descripcion": "Elimina mensajes (máx. 100)"},
                    {"nombre": "!warn", "descripcion": "Advierte a un miembro"},
                    {"nombre": "!config_bienvenida", "descripcion": "Configura canal de bienvenida"}
                ],
                "Diversión": [
                    {"nombre": "!dado", "descripcion": "Lanza un dado"},
                    {"nombre": "!moneda", "descripcion": "Lanza una moneda"},
                    {"nombre": "!encuesta", "descripcion": "Crea una encuesta simple"}
                ],
                "IA": [
                    {"nombre": "!chat", "descripcion": "Chatear con el asistente de IA"},
                    {"nombre": "@TDPBot", "descripcion": "Mencióname para obtener una respuesta"}
                ]
            }
            
            # Cargar comandos personalizados del servidor
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    comandos_personalizados = config.get('comandos_personalizados', [])
                    
                    # Añadir comandos personalizados
                    for cmd in comandos_personalizados:
                        categoria = cmd.get('categoria', 'Personalizado')
                        if categoria not in comandos_base:
                            comandos_base[categoria] = []
                        comandos_base[categoria].append({
                            "nombre": cmd['nombre'],
                            "descripcion": cmd['descripcion']
                        })
            
            return comandos_base
        except Exception as e:
            logger.error(f"Error obteniendo comandos del servidor: {e}")
            return {}

# Inicializar gestor de comandos
command_manager = ServerCommandManager()

# Comando para registrar comandos personalizados
@bot.command(name='registrar_comando')
@commands.has_permissions(administrator=True)
async def registrar_comando(ctx, comando: str, *, descripcion: str):
    """Registrar un nuevo comando personalizado para el servidor"""
    try:
        # Registrar comando
        resultado = command_manager.registrar_comando_personalizado(
            ctx.guild.id, 
            comando, 
            descripcion
        )
        
        if resultado:
            embed = discord.Embed(
                title="✅ Comando Registrado", 
                description=f"Comando `{comando}` añadido exitosamente", 
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error", 
                description="No se pudo registrar el comando", 
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en registro de comando: {e}")
        await ctx.send("Ocurrió un error al registrar el comando.")

# Comando para ver comandos disponibles
@bot.command(name='comandos')
async def listar_comandos(ctx):
    """Mostrar todos los comandos disponibles en el servidor"""
    try:
        # Obtener comandos del servidor
        comandos = command_manager.obtener_comandos_servidor(ctx.guild.id)
        
        # Crear embed
        embed = discord.Embed(
            title="📋 Comandos Disponibles", 
            description="Lista completa de comandos para este servidor", 
            color=discord.Color.blue()
        )
        
        # Añadir cada categoría
        for categoria, lista_comandos in comandos.items():
            valor_comandos = "\n".join([f"`{cmd['nombre']}`: {cmd['descripcion']}" for cmd in lista_comandos])
            embed.add_field(name=categoria, value=valor_comandos, inline=False)
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error listando comandos: {e}")
        await ctx.send("Ocurrió un error al listar los comandos.")

# Actualizar comando de ayuda para incluir nuevos comandos
@bot.command(name='help')
async def help_command(ctx):
    """Muestra una lista de comandos disponibles"""
    embed = discord.Embed(
        title="🤖 Comandos Disponibles", 
        description="Lista de comandos para interactuar con el bot", 
        color=discord.Color.blue()
    )
    
    comandos = {
        "Información": [
            ("!ping", "Muestra la latencia del bot"),
            ("!info", "Información básica del bot"),
            ("!diagnostico", "Diagnóstico de permisos (Solo Administradores)"),
            ("!servidor", "Información del servidor actual"),
            ("!miembro @usuario", "Información de un miembro específico"),
            ("!avatar @usuario", "Muestra el avatar de un usuario")
        ],
        "Moderación": [
            ("!kick @usuario", "Expulsa a un miembro"),
            ("!ban @usuario", "Banea a un miembro"),
            ("!clear [cantidad]", "Elimina mensajes (máx. 100)"),
            ("!config_bienvenida", "Configura canal de bienvenida"),
            ("!warn @usuario", "Advierte a un miembro")
        ],
        "Diversión": [
            ("!dado", "Lanza un dado"),
            ("!moneda", "Lanza una moneda"),
            ("!encuesta [pregunta]", "Crea una encuesta simple")
        ],
        "IA": [
            ("!chat [mensaje]", "Chatear con el asistente de IA"),
            ("@TDPBot", "Mencióname para obtener una respuesta")
        ],
        "Gestión de Comandos": [
            ("!comandos", "Ver todos los comandos disponibles"),
            ("!registrar_comando", "Registrar un comando personalizado (Solo Administradores)")
        ]
    }
    
    for categoria, lista_comandos in comandos.items():
        valor_comandos = "\n".join([f"`{cmd}`: {desc}" for cmd, desc in lista_comandos])
        embed.add_field(name=categoria, value=valor_comandos, inline=False)
    
    await ctx.send(embed=embed)

# Eventos y comandos
@bot.event
async def on_ready():
    try:
        logger.info(f'Bot conectado como {bot.user}')
        logger.info(f'ID: {bot.user.id}')
        logger.info(f'Conectado en {len(bot.guilds)} servidores')
        
        # Iniciar tarea de estado
        status_task.start()
        
        # Información detallada de cada servidor
        for guild in bot.guilds:
            try:
                logger.info(f'Servidor: {guild.name} (ID: {guild.id})')
                logger.info(f'Miembros: {guild.member_count}')
                logger.info(f'Canales: {len(guild.text_channels)}')
                
                # Intentar obtener información del sistema
                system_channel = guild.system_channel
                if system_channel:
                    logger.info(f'Canal de sistema: {system_channel.name}')
            except Exception as guild_error:
                logger.error(f"Error obteniendo información de servidor {guild.name}: {guild_error}")
    except Exception as e:
        logger.error(f"Error en on_ready: {e}")
        logger.error(traceback.format_exc())

@bot.event
async def on_connect():
    logger.info("Conexión con Discord establecida exitosamente")
    logger.info(f"Latencia: {bot.latency * 1000:.2f} ms")

@bot.event
async def on_disconnect():
    logger.warning("Desconectado del servicio de Discord")
    # Detener tarea de estado si está corriendo
    if status_task.is_running():
        status_task.stop()

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Error en evento {event}")
    logger.error(traceback.format_exc())

@bot.event
async def on_member_join(member):
    """Evento cuando un nuevo miembro se une al servidor"""
    try:
        # Buscar canal de bienvenida
        canal_bienvenida = member.guild.system_channel or member.guild.text_channels[0]
        
        # Crear embed de bienvenida
        embed = discord.Embed(
            title="¡Nuevo Miembro!", 
            description=f"¡Bienvenido {member.mention} al servidor {member.guild.name}! 🎉", 
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
        embed.set_footer(text=f"Miembro #{member.guild.member_count}")
        
        await canal_bienvenida.send(embed=embed)
        
        # Logging
        logger.info(f"Nuevo miembro unido: {member.name} en {member.guild.name}")
    except Exception as e:
        logger.error(f"Error en bienvenida de {member.name}: {e}")

# Comandos de Moderación
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, miembro: discord.Member, *, razon=None):
    """Expulsa a un miembro del servidor"""
    try:
        if razon:
            await miembro.kick(reason=razon)
            await ctx.send(f"🚫 {miembro.mention} ha sido expulsado. Razón: {razon}")
        else:
            await miembro.kick()
            await ctx.send(f"🚫 {miembro.mention} ha sido expulsado.")
        
        # Logging de la acción
        logger.info(f"Miembro expulsado: {miembro.name} por {ctx.author.name}")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para expulsar miembros.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al expulsar: {e}")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, miembro: discord.Member, *, razon=None):
    """Banea a un miembro del servidor"""
    try:
        if razon:
            await miembro.ban(reason=razon)
            await ctx.send(f"🔨 {miembro.mention} ha sido baneado. Razón: {razon}")
        else:
            await miembro.ban()
            await ctx.send(f"🔨 {miembro.mention} ha sido baneado.")
        
        # Logging de la acción
        logger.info(f"Miembro baneado: {miembro.name} por {ctx.author.name}")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para banear miembros.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al banear: {e}")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, cantidad: int = 10):
    """Elimina mensajes en un canal"""
    try:
        # Limitar cantidad de mensajes para evitar sobrecarga
        cantidad = min(cantidad, 100)
        deleted = await ctx.channel.purge(limit=cantidad + 1)
        await ctx.send(f"🗑️ Se han eliminado {len(deleted) - 1} mensajes.", delete_after=3)
        
        # Logging de la acción
        logger.info(f"Mensajes eliminados: {len(deleted) - 1} por {ctx.author.name}")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para eliminar mensajes.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al eliminar mensajes: {e}")

# Comando de advertencia profesional
@bot.command(name='warn')
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No se especificó razón"):
    """Sistema profesional de advertencias"""
    try:
        # Conexión a base de datos
        conn = sqlite3.connect('moderation.db')
        cursor = conn.cursor()
        
        # Registrar advertencia
        cursor.execute('''
            INSERT INTO warnings 
            (user_id, guild_id, moderator_id, reason, timestamp) 
            VALUES (?, ?, ?, ?, ?)
        ''', (
            member.id, 
            ctx.guild.id, 
            ctx.author.id, 
            reason, 
            datetime.now()
        ))
        
        # Obtener número de advertencias
        cursor.execute('''
            SELECT COUNT(*) FROM warnings 
            WHERE user_id = ? AND guild_id = ? AND active = 1
        ''', (member.id, ctx.guild.id))
        warning_count = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        # Embed de advertencia
        embed = discord.Embed(
            title="⚠️ Sistema de Advertencias", 
            color=discord.Color.orange()
        )
        embed.add_field(name="Miembro Advertido", value=member.mention, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
        embed.add_field(name="Razón", value=reason, inline=False)
        embed.add_field(name="Número de Advertencias", value=str(warning_count), inline=False)
        
        await ctx.send(embed=embed)
        
        # Notificación privada al usuario
        try:
            await member.send(
                f"Has recibido una advertencia en {ctx.guild.name}. "
                f"Razón: {reason}\n"
                f"Advertencias totales: {warning_count}"
            )
        except:
            await ctx.send(f"No se pudo enviar mensaje privado a {member.mention}")
        
        # Acciones según número de advertencias
        if warning_count == 3:
            await member.timeout(timedelta(hours=1), reason="3 advertencias")
            await ctx.send(f"{member.mention} ha sido silenciado por 1 hora debido a múltiples advertencias.")
        elif warning_count >= 5:
            await member.ban(reason="Máximo de advertencias alcanzado")
            await ctx.send(f"{member.mention} ha sido baneado por acumular demasiadas advertencias.")
        
    except Exception as e:
        logger.error(f"Error en comando de advertencia: {e}")
        await ctx.send("Ocurrió un error procesando la advertencia.")

# Comandos de Utilidad
@bot.command(name='dado')
async def dado(ctx):
    """Lanza un dado"""
    resultado = random.randint(1, 6)
    await ctx.send(f"🎲 Has lanzado un dado: **{resultado}**")

@bot.command(name='moneda')
async def moneda(ctx):
    """Lanza una moneda"""
    resultado = random.choice(["Cara", "Cruz"])
    await ctx.send(f"🪙 Has lanzado una moneda: **{resultado}**")

@bot.command(name='encuesta')
@commands.has_permissions(manage_messages=True)
async def encuesta(ctx, *, pregunta):
    """Crea una encuesta simple"""
    embed = discord.Embed(title="📊 Nueva Encuesta", description=pregunta, color=discord.Color.blue())
    message = await ctx.send(embed=embed)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

@bot.command(name='avatar')
async def avatar(ctx, miembro: discord.Member = None):
    """Muestra el avatar de un miembro"""
    miembro = miembro or ctx.author
    embed = discord.Embed(title=f"Avatar de {miembro.name}", color=discord.Color.blue())
    embed.set_image(url=miembro.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name='config_bienvenida')
@commands.has_permissions(administrator=True)
async def config_bienvenida(ctx, canal: discord.TextChannel = None):
    """Configura el canal de bienvenida"""
    canal = canal or ctx.channel
    
    embed = discord.Embed(
        title="Canal de Bienvenida Configurado", 
        description=f"Los nuevos miembros serán bienvenidos en {canal.mention}", 
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    
    # Aquí podrías añadir lógica para guardar la configuración en una base de datos

# Comando de respuesta inteligente
@bot.command(name='chat')
async def chat_ai(ctx, *, mensaje):
    """Chatear con el asistente de IA"""
    try:
        # Generar respuesta
        respuesta = ai_assistant.generar_respuesta(mensaje)
        
        # Crear embed para la respuesta
        embed = discord.Embed(
            title="🤖 Asistente IA", 
            description=respuesta, 
            color=discord.Color.blue()
        )
        embed.set_footer(text="Respuesta generada por IA")
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error en comando de chat: {e}")
        await ctx.send("Disculpa, hubo un problema generando la respuesta.")

# Evento de mención
@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return
    
    # Procesar comandos existentes
    await bot.process_commands(message)
    
    # Responder si es mencionado
    if bot.user.mentioned_in(message):
        # Extraer texto sin menciones
        texto = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        try:
            # Generar respuesta
            respuesta = ai_assistant.generar_respuesta(texto)
            
            # Crear embed
            embed = discord.Embed(
                title="🤖 Asistente IA", 
                description=respuesta, 
                color=discord.Color.blue()
            )
            embed.set_footer(text="Respuesta generada por IA")
            
            await message.channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error en respuesta por mención: {e}")

# Comando de ayuda personalizado
@bot.command(name='help')
async def help_command(ctx):
    """Muestra una lista de comandos disponibles"""
    embed = discord.Embed(
        title="🤖 Comandos Disponibles", 
        description="Lista de comandos para interactuar con el bot", 
        color=discord.Color.blue()
    )
    
    comandos = {
        "Información": [
            ("!ping", "Muestra la latencia del bot"),
            ("!info", "Información básica del bot"),
            ("!diagnostico", "Diagnóstico de permisos (Solo Administradores)"),
            ("!servidor", "Información del servidor actual"),
            ("!miembro @usuario", "Información de un miembro específico"),
            ("!avatar @usuario", "Muestra el avatar de un usuario")
        ],
        "Moderación": [
            ("!kick @usuario", "Expulsa a un miembro"),
            ("!ban @usuario", "Banea a un miembro"),
            ("!clear [cantidad]", "Elimina mensajes (máx. 100)"),
            ("!config_bienvenida", "Configura canal de bienvenida"),
            ("!warn @usuario", "Advierte a un miembro")
        ],
        "Diversión": [
            ("!dado", "Lanza un dado"),
            ("!moneda", "Lanza una moneda"),
            ("!encuesta [pregunta]", "Crea una encuesta simple")
        ],
        "IA": [
            ("!chat [mensaje]", "Chatear con el asistente de IA"),
            ("@TDPBot", "Mencióname para obtener una respuesta")
        ],
        "Gestión de Comandos": [
            ("!comandos", "Ver todos los comandos disponibles"),
            ("!registrar_comando", "Registrar un comando personalizado (Solo Administradores)")
        ]
    }
    
    for categoria, lista_comandos in comandos.items():
        valor_comandos = "\n".join([f"`{cmd}`: {desc}" for cmd, desc in lista_comandos])
        embed.add_field(name=categoria, value=valor_comandos, inline=False)
    
    await ctx.send(embed=embed)

# Comando de prueba
@bot.command(name='ping')
async def ping(ctx):
    """Comando de prueba para verificar la conectividad del bot"""
    start_time = datetime.datetime.now()
    message = await ctx.send('Pong!')
    end_time = datetime.datetime.now()
    
    latency = (end_time - start_time).total_seconds() * 1000
    await message.edit(content=f'Pong! \nLatencia: {round(bot.latency * 1000)}ms\nTiempo de respuesta: {round(latency)}ms')

# Comando de información del bot
@bot.command(name='info')
async def bot_info(ctx):
    """Muestra información básica del bot"""
    embed = discord.Embed(title="Información del Bot", color=discord.Color.blue())
    embed.add_field(name="Nombre", value=bot.user.name, inline=False)
    embed.add_field(name="ID", value=bot.user.id, inline=False)
    embed.add_field(name="Servidores", value=len(bot.guilds), inline=False)
    embed.add_field(name="Latencia", value=f"{round(bot.latency * 1000)}ms", inline=False)
    embed.add_field(name="Estado", value="", inline=False)
    embed.add_field(name="Desarrollador", value="TDPBlog", inline=False)
    await ctx.send(embed=embed)

# Comando de diagnóstico de permisos
@bot.command(name='diagnostico')
@commands.has_permissions(administrator=True)
async def diagnostico(ctx):
    """Muestra diagnóstico detallado de permisos y configuración"""
    embed = discord.Embed(title="Diagnóstico del Bot", color=discord.Color.green())
    
    # Información del servidor
    embed.add_field(name="Servidor", value=ctx.guild.name, inline=False)
    embed.add_field(name="ID del Servidor", value=ctx.guild.id, inline=False)
    
    # Permisos del bot
    bot_member = ctx.guild.get_member(bot.user.id)
    bot_permissions = bot_member.guild_permissions
    
    # Verificar permisos clave
    key_permissions = [
        "send_messages", 
        "read_messages", 
        "embed_links", 
        "attach_files", 
        "read_message_history"
    ]
    
    permission_status = "\n".join([
        f"{' ' if getattr(bot_permissions, perm) else ' '} {perm.replace('_', ' ').title()}" 
        for perm in key_permissions
    ])
    
    embed.add_field(name="Permisos del Bot", value=permission_status, inline=False)
    
    await ctx.send(embed=embed)

# Comando de información del servidor
@bot.command(name='servidor')
async def servidor(ctx):
    """Muestra información del servidor"""
    embed = discord.Embed(title="Información del Servidor", color=discord.Color.blue())
    embed.add_field(name="Nombre", value=ctx.guild.name, inline=False)
    embed.add_field(name="ID", value=ctx.guild.id, inline=False)
    embed.add_field(name="Miembros", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Canales", value=len(ctx.guild.text_channels), inline=False)
    embed.add_field(name="Creado", value=ctx.guild.created_at.strftime("%d/%m/%Y"), inline=False)
    await ctx.send(embed=embed)

# Comando de información de un miembro
@bot.command(name='miembro')
async def miembro(ctx, miembro: discord.Member = None):
    """Muestra información de un miembro"""
    # Si no se especifica miembro, usar el autor del mensaje
    miembro = miembro or ctx.author
    
    embed = discord.Embed(title="Información del Miembro", color=discord.Color.blue())
    embed.set_thumbnail(url=miembro.display_avatar.url)
    embed.add_field(name="Nombre", value=miembro.name, inline=False)
    embed.add_field(name="Nombre para mostrar", value=miembro.display_name, inline=False)
    embed.add_field(name="ID", value=miembro.id, inline=False)
    embed.add_field(name="Rol más alto", value=miembro.top_role.name, inline=False)
    embed.add_field(name="Cuenta creada", value=miembro.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Se unió al servidor", value=miembro.joined_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="Estado", value=str(miembro.status), inline=False)
    await ctx.send(embed=embed)

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando no encontrado. Usa !help para ver los comandos disponibles.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("No tienes permisos para usar este comando.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Argumento inválido. Verifica el formato del comando.")
    else:
        await ctx.send(f"Ocurrió un error: {str(error)}")

# Crear aplicación Flask para monitoreo
app = Flask(__name__)

@app.route('/health')
def health_check():
    logger.info("Health check endpoint accessed")
    return "Bot de Discord funcionando", 200

def create_app():
    return app

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        logger.critical("No se encontró el token de Discord. Verifica tus variables de entorno.")
        sys.exit(1)
    
    logger.info(f"Intentando conectar con token: {TOKEN[:10]}...")
    
    try:
        def start_bot():
            try:
                logger.info("Iniciando bot de Discord...")
                bot.run(TOKEN)
            except discord.LoginFailure as e:
                logger.critical(f"Error de autenticación: {e}")
                logger.critical("Verifica que tu token sea correcto y tenga los permisos necesarios.")
            except Exception as e:
                logger.critical(f"Error al ejecutar el bot: {e}")
                logger.critical(traceback.format_exc())
        
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.start()
    except Exception as e:
        logger.critical(f"Error crítico al iniciar el bot: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

# Inicializar base de datos al inicio
init_mod_database()

# Iniciar bot al ejecutar el script
if __name__ == '__main__':
    run_bot()
