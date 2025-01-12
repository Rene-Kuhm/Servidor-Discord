import discord
from discord.ext import commands
import logging

logger = logging.getLogger('discord_bot')

class RolePersonalizationSystem:
    def __init__(self, bot):
        self.bot = bot

    async def solicitar_rol(self, ctx, nombre_rol):
        """Solicitar un rol especial"""
        try:
            guild = ctx.guild
            rol = discord.utils.get(guild.roles, name=nombre_rol)
            
            if not rol:
                await ctx.send(f"El rol {nombre_rol} no existe.")
                return
            
            await ctx.author.add_roles(rol)
            await ctx.send(f"¡Se te ha asignado el rol {nombre_rol}!")
            logger.info(f"Rol {nombre_rol} asignado a {ctx.author}")
        
        except Exception as e:
            logger.error(f"Error al asignar rol: {e}")
            await ctx.send("Hubo un error al asignar el rol.")

    async def listar_roles_disponibles(self, ctx):
        """Listar roles especiales disponibles"""
        try:
            roles_especiales = [
                "Desarrollador", 
                "Diseñador", 
                "DevOps", 
                "Estudiante", 
                "Freelancer"
            ]
            
            mensaje = "**Roles disponibles:**\n"
            for rol in roles_especiales:
                mensaje += f"- {rol}\n"
            
            await ctx.send(mensaje)
        
        except Exception as e:
            logger.error(f"Error al listar roles: {e}")
            await ctx.send("Hubo un error al listar los roles.")
