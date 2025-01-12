import os
import sys
import logging
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configuración de logging más detallada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='w'
)
logger = logging.getLogger('discord_bot')

# Habilitar logging detallado para discord.py
logging.getLogger('discord').setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.DEBUG)

# Configuración de intents
intents = discord.Intents.all()

# Crear bot con prefijo de comandos
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        logger.info(f'Bot conectado como {bot.user}')
        logger.info(f'ID: {bot.user.id}')
        logger.info(f'Conectado en {len(bot.guilds)} servidores')
        
        for guild in bot.guilds:
            logger.info(f'Servidor: {guild.name} (ID: {guild.id})')
            logger.info(f'Miembros: {guild.member_count}')
            logger.info(f'Canales: {len(guild.text_channels)}')
    except Exception as e:
        logger.error(f"Error en on_ready: {e}")
        logger.error(traceback.format_exc())

@bot.event
async def on_connect():
    logger.info("Conexión establecida exitosamente")

@bot.event
async def on_disconnect():
    logger.warning("Desconectado del servicio de Discord")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Error en evento {event}")
    logger.error(traceback.format_exc())

# Comando para enviar mensaje
@bot.command(name='enviar')
async def enviar_mensaje(ctx, *, mensaje):
    """Envía un mensaje en el canal actual"""
    await ctx.send(mensaje)

# Comando para subir imagen
@bot.command(name='imagen')
async def subir_imagen(ctx, url_imagen):
    """Sube una imagen al canal"""
    embed = discord.Embed()
    embed.set_image(url=url_imagen)
    await ctx.send(embed=embed)

# Comando para crear embed personalizado
@bot.command(name='embed')
async def crear_embed(ctx, titulo, descripcion, color=None):
    """Crea un embed personalizado"""
    if color is None:
        color = discord.Color.blue()
    else:
        color = discord.Color(int(color, 16))  # Convierte color hex
    
    embed = discord.Embed(title=titulo, description=descripcion, color=color)
    await ctx.send(embed=embed)

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando no encontrado. Usa !help para ver los comandos disponibles.")
    else:
        await ctx.send(f"Ocurrió un error: {str(error)}")

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        logger.critical("No se encontró el token de Discord. Verifica tus variables de entorno.")
        sys.exit(1)
    
    logger.info(f"Intentando conectar con token: {TOKEN[:10]}...")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure as e:
        logger.critical(f"Error de autenticación: {e}")
        logger.critical("Verifica que tu token sea correcto y tenga los permisos necesarios.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error crítico al iniciar el bot: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

# Agregar un endpoint de salud para monitoreo
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health_check():
    return "Bot de Discord funcionando", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Iniciar servidor Flask en un hilo
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

if __name__ == '__main__':
    run_bot()
