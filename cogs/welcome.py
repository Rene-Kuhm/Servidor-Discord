import discord
from discord.ext import commands
import logging
import random

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot.welcome')
        self.welcome_messages = [
            "¡Bienvenido al servidor! Esperamos que te sientas como en casa.",
            "¡Qué bueno tenerte aquí! No dudes en presentarte.",
            "¡Un nuevo miembro se une! Prepárense para la diversión.",
            "¡Bienvenido! Esperamos que disfrutes tu estancia con nosotros."
        ]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Mensaje de bienvenida personalizado"""
        try:
            # Buscar canal de bienvenida
            welcome_channel = discord.utils.get(member.guild.text_channels, name="bienvenidas")
            
            if welcome_channel:
                # Crear embed de bienvenida
                embed = discord.Embed(
                    title="🎉 Nuevo Miembro 🎉",
                    description=f"{member.mention} se ha unido al servidor",
                    color=discord.Color.green()
                )
                
                # Mensaje de bienvenida aleatorio
                embed.add_field(
                    name="Mensaje de Bienvenida", 
                    value=random.choice(self.welcome_messages), 
                    inline=False
                )
                
                # Información adicional
                embed.add_field(
                    name="Información", 
                    value="Por favor, lee las reglas del servidor y diviértete", 
                    inline=False
                )
                
                # Añadir avatar del nuevo miembro
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await welcome_channel.send(embed=embed)
                
                # Intentar asignar rol de novato
                try:
                    newbie_role = discord.utils.get(member.guild.roles, name="Novato")
                    if newbie_role:
                        await member.add_roles(newbie_role)
                except Exception as role_error:
                    self.logger.error(f"No se pudo asignar rol de novato: {role_error}")
        
        except Exception as e:
            self.logger.error(f"Error en mensaje de bienvenida: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Mensaje de despedida"""
        try:
            goodbye_channel = discord.utils.get(member.guild.text_channels, name="registro-moderacion")
            
            if goodbye_channel:
                embed = discord.Embed(
                    title="👋 Miembro que Abandona",
                    description=f"{member.name} ha dejado el servidor",
                    color=discord.Color.red()
                )
                embed.add_field(name="Fecha", value=discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                
                await goodbye_channel.send(embed=embed)
        
        except Exception as e:
            self.logger.error(f"Error en mensaje de despedida: {e}")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
