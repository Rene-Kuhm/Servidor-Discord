import os
import sys
import logging
import traceback
import threading
import discord
from discord.ext import commands
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

# Configuración de intents con permisos explícitos
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Crear bot con prefijo de comandos
bot = commands.Bot(command_prefix='!', intents=intents)

# Eventos y comandos
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
    logger.info("Conexión con Discord establecida exitosamente")

@bot.event
async def on_disconnect():
    logger.warning("Desconectado del servicio de Discord")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Error en evento {event}")
    logger.error(traceback.format_exc())

# Comando de prueba
@bot.command(name='ping')
async def ping(ctx):
    """Comando de prueba para verificar la conectividad del bot"""
    await ctx.send('Pong! Bot está funcionando.')

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
