import discord
from discord.ext import commands
import logging

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot.moderation')

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No se especificó razón"):
        """Expulsar a un miembro del servidor"""
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Miembro Expulsado", 
                description=f"{member.mention} ha sido expulsado del servidor",
                color=discord.Color.orange()
            )
            embed.add_field(name="Razón", value=reason)
            embed.add_field(name="Moderador", value=ctx.author.mention)
            await ctx.send(embed=embed)
            
            # Registrar en el canal de moderación
            log_channel = discord.utils.get(ctx.guild.text_channels, name="registro-moderacion")
            if log_channel:
                await log_channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error al expulsar miembro: {e}")
            await ctx.send("No se pudo expulsar al miembro.")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No se especificó razón"):
        """Banear a un miembro del servidor"""
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Miembro Baneado", 
                description=f"{member.mention} ha sido baneado del servidor",
                color=discord.Color.red()
            )
            embed.add_field(name="Razón", value=reason)
            embed.add_field(name="Moderador", value=ctx.author.mention)
            await ctx.send(embed=embed)
            
            # Registrar en el canal de moderación
            log_channel = discord.utils.get(ctx.guild.text_channels, name="registro-moderacion")
            if log_channel:
                await log_channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error al banear miembro: {e}")
            await ctx.send("No se pudo banear al miembro.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
