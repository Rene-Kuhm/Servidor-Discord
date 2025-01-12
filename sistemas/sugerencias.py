import discord
from discord.ext import commands
import asyncio
import logging

class SistemaSugerencias:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        
        # Configuración del sistema de sugerencias
        self.config = {
            "canal_sugerencias": "💡-sugerencias",
            "canal_aprobadas": "✅-sugerencias-aprobadas",
            "canal_rechazadas": "❌-sugerencias-rechazadas"
        }
    
    async def crear_canales_sugerencias(self, guild):
        """Crear canales para el sistema de sugerencias"""
        # Categoría de sugerencias
        categoria_sugerencias = discord.utils.get(guild.categories, name="💡 Mejoras de Comunidad")
        if not categoria_sugerencias:
            categoria_sugerencias = await guild.create_category("💡 Mejoras de Comunidad")
        
        # Canales de sugerencias
        canales = [
            self.config["canal_sugerencias"],
            self.config["canal_aprobadas"],
            self.config["canal_rechazadas"]
        ]
        
        for nombre_canal in canales:
            canal = discord.utils.get(guild.text_channels, name=nombre_canal)
            if not canal:
                canal = await guild.create_text_channel(
                    name=nombre_canal, 
                    category=categoria_sugerencias,
                    topic="Sistema de sugerencias para mejora continua del servidor"
                )
                
                # Mensaje de bienvenida para cada canal
                embed = discord.Embed(
                    title=f"🌟 Bienvenido al Canal {nombre_canal}",
                    description="Aquí puedes compartir tus ideas para mejorar nuestra comunidad.",
                    color=discord.Color.green()
                )
                
                if nombre_canal == self.config["canal_sugerencias"]:
                    embed.add_field(name="Cómo hacer una sugerencia", value=[
                        "• Sé claro y específico",
                        "• Explica el beneficio de tu idea",
                        "• Usa el comando `!sugerir` para enviar"
                    ], inline=False)
                
                await canal.send(embed=embed)
        
        self.logger.info("Canales de sugerencias configurados exitosamente")
    
    async def enviar_sugerencia(self, ctx, sugerencia):
        """Enviar una sugerencia al canal correspondiente"""
        canal_sugerencias = discord.utils.get(ctx.guild.text_channels, name=self.config["canal_sugerencias"])
        
        if not canal_sugerencias:
            await ctx.send("Canal de sugerencias no configurado.")
            return
        
        # Crear embed de sugerencia
        embed = discord.Embed(
            title="💡 Nueva Sugerencia",
            description=sugerencia,
            color=discord.Color.blue()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        
        # Enviar sugerencia
        mensaje = await canal_sugerencias.send(embed=embed)
        
        # Añadir reacciones para votar
        await mensaje.add_reaction("👍")  # Apoyar
        await mensaje.add_reaction("👎")  # No apoyar
        
        await ctx.send("Tu sugerencia ha sido enviada. ¡Gracias por ayudar a mejorar nuestra comunidad!")
    
    def setup(self, bot):
        """Configurar comandos de sugerencias"""
        @bot.command(name="sugerir")
        async def sugerir(ctx, *, sugerencia):
            """Enviar una sugerencia para el servidor"""
            await self.enviar_sugerencia(ctx, sugerencia)
