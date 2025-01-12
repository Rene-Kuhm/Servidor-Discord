import discord
from typing import Dict, List
from .database import DatabaseManager
import json

class SistemaInsignias:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
        
        self.insignias = {
            "primera_contribucion": {
                "nombre": "🌟 Primera Contribución",
                "descripcion": "Realizaste tu primera contribución a un proyecto",
                "icono": "🏆",
                "criterios": self.verificar_primera_contribucion
            },
            "mentor": {
                "nombre": "🧠 Mentor",
                "descripcion": "Has ayudado a 5 miembros en la comunidad",
                "icono": "🎓",
                "criterios": self.verificar_mentoria
            },
            "hackathon": {
                "nombre": "🚀 Participante de Hackathon",
                "descripcion": "Participaste en un evento de hackathon",
                "icono": "💻",
                "criterios": self.verificar_hackathon
            }
        }
    
    async def verificar_primera_contribucion(self, member):
        """Verificar primera contribución"""
        # TODO: Implementar lógica de verificación de contribución
        return False
    
    async def verificar_mentoria(self, member):
        """Verificar si un miembro ha sido mentor"""
        # TODO: Implementar lógica de conteo de ayudas
        return False
    
    async def verificar_hackathon(self, member):
        """Verificar participación en hackathon"""
        # TODO: Implementar lógica de verificación de evento
        return False
    
    async def otorgar_insignia(self, member, nombre_insignia):
        """Otorgar una insignia a un miembro"""
        insignia = self.insignias.get(nombre_insignia)
        if not insignia:
            return False
        
        # Verificar criterios
        if await insignia['criterios'](member):
            # Obtener usuario de la base de datos
            usuario = await self.db_manager.obtener_usuario(member.id)
            
            if not usuario:
                return False
            
            # Obtener insignias actuales
            insignias_actuales = json.loads(usuario.get('insignias', '[]'))
            
            # Añadir nueva insignia
            if nombre_insignia not in insignias_actuales:
                insignias_actuales.append(nombre_insignia)
                
                # Actualizar en base de datos
                await self.db_manager.connect()
                await self.db_manager.conn.execute(
                    'UPDATE usuarios SET insignias = ? WHERE user_id = ?',
                    (json.dumps(insignias_actuales), member.id)
                )
                await self.db_manager.conn.commit()
                await self.db_manager.close()
            
            # Notificar
            canal_logros = discord.utils.get(member.guild.text_channels, name="🏆-logros")
            if canal_logros:
                embed = discord.Embed(
                    title="🏅 Nueva Insignia Desbloqueada",
                    description=f"{member.mention} ha obtenido la insignia: {insignia['nombre']}",
                    color=discord.Color.gold()
                )
                await canal_logros.send(embed=embed)
            
            return True
        
        return False
    
    async def obtener_insignias(self, member):
        """Obtener insignias de un miembro"""
        usuario = await self.db_manager.obtener_usuario(member.id)
        
        if not usuario or not usuario.get('insignias'):
            return []
        
        return json.loads(usuario['insignias'])
    
    async def mostrar_insignias(self, ctx):
        """Mostrar insignias del usuario"""
        insignias = await self.obtener_insignias(ctx.author)
        
        if insignias:
            embed = discord.Embed(
                title="🏅 Tus Insignias",
                description="\n".join([
                    f"{self.insignias[insignia]['icono']} {self.insignias[insignia]['nombre']}" 
                    for insignia in insignias
                ]),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Aún no has desbloqueado ninguna insignia. ¡Sigue participando!")
    
    async def listar_insignias_disponibles(self, ctx):
        """Listar todas las insignias disponibles"""
        embed = discord.Embed(
            title="🏆 Insignias Disponibles",
            description="Descubre cómo obtener estas increíbles insignias",
            color=discord.Color.blue()
        )
        
        for nombre, detalles in self.insignias.items():
            embed.add_field(
                name=f"{detalles['icono']} {detalles['nombre']}", 
                value=detalles['descripcion'], 
                inline=False
            )
        
        await ctx.send(embed=embed)
