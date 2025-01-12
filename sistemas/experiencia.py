import discord
from typing import Dict, List
from .database import DatabaseManager
import datetime

class SistemaExperiencia:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
        
        self.niveles = {
            1: {"xp_requerida": 0, "rol": "🌱 Aprendiz", "beneficios": []},
            2: {"xp_requerida": 100, "rol": "🌿 Principiante", "beneficios": ["acceso_canal_principiantes"]},
            3: {"xp_requerida": 250, "rol": "🌳 Desarrollador Junior", "beneficios": ["mentoria_junior"]},
            4: {"xp_requerida": 500, "rol": "🚀 Desarrollador Mid", "beneficios": ["proyectos_internos"]},
            5: {"xp_requerida": 1000, "rol": "💎 Desarrollador Senior", "beneficios": ["canal_senior", "voto_decisiones"]}
        }
        
        self.fuentes_xp = {
            "mensaje_enviado": 1,
            "reaccion_util": 5,
            "resolver_duda": 10,
            "contribuir_proyecto": 20,
            "participar_evento": 15
        }
    
    async def calcular_nivel(self, xp_total):
        """Calcular el nivel actual basado en la experiencia total"""
        nivel_actual = 1
        for nivel, detalles in sorted(self.niveles.items(), key=lambda x: x[1]['xp_requerida'], reverse=True):
            if xp_total >= detalles["xp_requerida"]:
                return nivel
        return 1
    
    async def obtener_beneficios_nivel(self, nivel):
        """Obtener los beneficios de un nivel específico"""
        return self.niveles.get(nivel, {}).get('beneficios', [])
    
    async def agregar_experiencia(self, member, fuente, cantidad=None):
        """Agregar experiencia a un miembro"""
        # Cantidad de XP por defecto o personalizada
        xp_ganada = cantidad or self.fuentes_xp.get(fuente, 1)
        
        # Agregar experiencia en base de datos
        await self.db_manager.actualizar_experiencia(member.id, xp_ganada)
        
        # Obtener experiencia total
        usuario = await self.db_manager.obtener_usuario(member.id)
        xp_total = usuario['experiencia'] if usuario else 0
        
        # Verificar si sube de nivel
        nuevo_nivel = await self.calcular_nivel(xp_total)
        
        # Manejar subida de nivel
        await self.manejar_subida_nivel(member, nuevo_nivel)
    
    async def manejar_subida_nivel(self, member, nuevo_nivel):
        """Manejar la subida de nivel de un miembro"""
        # Obtener rol correspondiente al nivel
        rol_nivel = self.niveles.get(nuevo_nivel, {}).get('rol')
        
        if rol_nivel:
            # Buscar o crear rol de nivel
            rol = discord.utils.get(member.guild.roles, name=rol_nivel)
            if not rol:
                rol = await member.guild.create_role(name=rol_nivel)
            
            # Asignar rol
            await member.add_roles(rol)
        
        # Notificar subida de nivel
        canal_niveles = discord.utils.get(member.guild.text_channels, name="🆙-niveles")
        if canal_niveles:
            embed = discord.Embed(
                title="¡Subida de Nivel! 🎉",
                description=f"{member.mention} ha alcanzado el nivel {nuevo_nivel}",
                color=discord.Color.gold()
            )
            await canal_niveles.send(embed=embed)
    
    async def mostrar_perfil(self, ctx):
        """Mostrar perfil de experiencia de un usuario"""
        usuario = await self.db_manager.obtener_usuario(ctx.author.id)
        
        if not usuario:
            await ctx.send("No se encontró tu perfil. ¡Comienza a interactuar para ganar experiencia!")
            return
        
        nivel = await self.calcular_nivel(usuario['experiencia'])
        rol_nivel = self.niveles.get(nivel, {}).get('rol', 'Sin Rol')
        beneficios = await self.obtener_beneficios_nivel(nivel)
        
        embed = discord.Embed(
            title=f"📊 Perfil de {ctx.author.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Experiencia", value=usuario['experiencia'], inline=True)
        embed.add_field(name="Nivel", value=nivel, inline=True)
        embed.add_field(name="Rol de Nivel", value=rol_nivel, inline=True)
        
        if beneficios:
            embed.add_field(
                name="Beneficios Actuales", 
                value="\n".join(f"• {beneficio}" for beneficio in beneficios), 
                inline=False
            )
        
        await ctx.send(embed=embed)
