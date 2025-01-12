import discord
from typing import Dict, List
from .database import DatabaseManager
from datetime import datetime, timedelta

class SistemaEventos:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
        
        self.eventos_programados = [
            {
                "nombre": "Coding Night",
                "frecuencia": "Semanal",
                "dia": "Viernes",
                "hora": "20:00",
                "descripcion": "Noche de programación en vivo y resolución de problemas",
                "canal": "💻-coding-night",
                "actividades": [
                    "Programación en vivo",
                    "Resolución de desafíos de código",
                    "Pair programming"
                ]
            },
            {
                "nombre": "Tech Talk",
                "frecuencia": "Mensual",
                "dia": "Último Jueves",
                "hora": "19:00",
                "descripcion": "Charla sobre tecnologías emergentes",
                "canal": "🎤-tech-talks",
                "temas_pendientes": []
            }
        ]
    
    async def programar_evento(self, guild):
        """Programar eventos en el servidor"""
        for evento in self.eventos_programados:
            # Crear canal si no existe
            canal = discord.utils.get(guild.text_channels, name=evento['canal'])
            if not canal:
                categoria = discord.utils.get(guild.categories, name="🌐 Tecnología")
                canal = await guild.create_text_channel(
                    name=evento['canal'], 
                    category=categoria
                )
            
            # Crear evento programado
            embed = discord.Embed(
                title=f"📅 {evento['nombre']}",
                description=evento['descripcion'],
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Detalles", 
                value=f"**Frecuencia:** {evento['frecuencia']}\n"
                      f"**Día:** {evento['dia']}\n"
                      f"**Hora:** {evento['hora']}"
            )
            
            await canal.send(embed=embed)
            
            # Registrar evento en base de datos
            await self.db_manager.registrar_evento(
                evento['nombre'], 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                evento['descripcion']
            )
    
    async def notificar_proximo_evento(self, guild):
        """Notificar sobre el próximo evento"""
        eventos = await self.db_manager.obtener_eventos()
        
        if not eventos:
            return
        
        # Obtener el próximo evento
        proximo_evento = eventos[0]
        
        # Canal de anuncios
        canal_anuncios = discord.utils.get(guild.text_channels, name="📢-anuncios")
        
        if canal_anuncios:
            embed = discord.Embed(
                title="🎉 Próximo Evento",
                description=f"**{proximo_evento['nombre']}**\n{proximo_evento['descripcion']}",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Fecha", 
                value=proximo_evento['fecha'], 
                inline=True
            )
            
            await canal_anuncios.send(embed=embed)
    
    async def proponer_tema_tech_talk(self, ctx, tema):
        """Proponer un tema para Tech Talk"""
        # Encontrar el evento de Tech Talk
        tech_talk = next((evento for evento in self.eventos_programados 
                          if evento['nombre'] == 'Tech Talk'), None)
        
        if tech_talk:
            # Añadir tema propuesto
            if 'temas_pendientes' not in tech_talk:
                tech_talk['temas_pendientes'] = []
            
            tech_talk['temas_pendientes'].append({
                "tema": tema,
                "proponente": ctx.author.name,
                "votos": 0
            })
            
            # Notificar en canal de anuncios
            canal_anuncios = discord.utils.get(ctx.guild.text_channels, name="📢-anuncios")
            if canal_anuncios:
                embed = discord.Embed(
                    title="💡 Nuevo Tema Propuesto para Tech Talk",
                    description=f"**Tema:** {tema}\n**Propuesto por:** {ctx.author.name}",
                    color=discord.Color.blue()
                )
                await canal_anuncios.send(embed=embed)
            
            await ctx.send("¡Tema propuesto con éxito! Los moderadores lo revisarán.")
        else:
            await ctx.send("No se encontró el evento Tech Talk.")
    
    async def votar_tema_tech_talk(self, ctx, tema):
        """Votar por un tema de Tech Talk"""
        tech_talk = next((evento for evento in self.eventos_programados 
                          if evento['nombre'] == 'Tech Talk'), None)
        
        if tech_talk and 'temas_pendientes' in tech_talk:
            # Buscar tema
            tema_encontrado = next((t for t in tech_talk['temas_pendientes'] 
                                    if t['tema'] == tema), None)
            
            if tema_encontrado:
                tema_encontrado['votos'] += 1
                await ctx.send(f"Has votado por el tema: {tema}")
            else:
                await ctx.send("Tema no encontrado.")
        else:
            await ctx.send("No hay temas disponibles para votar.")
