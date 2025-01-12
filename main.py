import os
import sys
import logging
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='w'
)
logger = logging.getLogger('discord_bot')

# Configuración de intents
intents = discord.Intents.all()

# Crear bot con prefijo de comandos
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot conectado como {bot.user}')
    logger.info(f'ID: {bot.user.id}')
    logger.info(f'Conectado en {len(bot.guilds)} servidores')
    
    for guild in bot.guilds:
        logger.info(f'Servidor: {guild.name} (ID: {guild.id})')
        logger.info(f'Miembros: {guild.member_count}')
        logger.info(f'Canales: {len(guild.text_channels)}')

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
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Error crítico al iniciar el bot: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    run_bot()
