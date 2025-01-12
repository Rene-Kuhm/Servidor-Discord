# Importaciones y configuración
import os
import sys
import logging
import traceback
import threading
import datetime
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from flask import Flask

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

# Comando de ayuda personalizado
@bot.command(name='help')
async def help_command(ctx):
    """Muestra una lista de comandos disponibles"""
    embed = discord.Embed(
        title=" Comandos Disponibles", 
        description="Lista de comandos para interactuar con el bot", 
        color=discord.Color.blue()
    )
    
    commands_list = [
        ("!ping", "Muestra la latencia del bot"),
        ("!info", "Información básica del bot"),
        ("!diagnostico", "Diagnóstico de permisos (Solo Administradores)"),
        ("!servidor", "Información del servidor actual"),
        ("!miembro @usuario", "Información de un miembro específico")
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
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

# Iniciar bot al ejecutar el script
if __name__ == '__main__':
    run_bot()
