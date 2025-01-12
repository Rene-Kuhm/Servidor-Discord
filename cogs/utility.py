import discord
from discord.ext import commands
import logging

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot.utility')

    @commands.command(name='serverinfo')
    async def server_info(self, ctx):
        """Mostrar información detallada del servidor"""
        server = ctx.guild
        embed = discord.Embed(
            title=server.name, 
            description='Información Detallada del Servidor', 
            color=discord.Color.blue()
        )
        embed.add_field(name='Dueño', value=server.owner.mention, inline=False)
        embed.add_field(name='Miembros', value=server.member_count, inline=True)
        embed.add_field(name='Fecha de Creación', value=server.created_at.strftime('%Y-%m-%d'), inline=True)
        embed.add_field(name='Región', value=str(server.region), inline=True)
        embed.add_field(name='Nivel de Verificación', value=str(server.verification_level), inline=True)
        
        # Añadir ícono del servidor
        if server.icon:
            embed.set_thumbnail(url=server.icon.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Limpiar mensajes en el canal"""
        try:
            deleted = await ctx.channel.purge(limit=amount)
            embed = discord.Embed(
                title="🧹 Mensajes Eliminados", 
                description=f"Se eliminaron {len(deleted)} mensajes", 
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=5)
        except Exception as e:
            self.logger.error(f"Error al limpiar mensajes: {e}")
            await ctx.send("No se pudieron eliminar los mensajes.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
