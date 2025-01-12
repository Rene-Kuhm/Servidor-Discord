import discord
import aiohttp
from typing import Dict
from .database import DatabaseManager

class IntegracionesDesarrollo:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
        
        self.integraciones = {
            "github": {
                "webhook": None,
                "canal": "#🔗-integraciones",
                "eventos": ["pull_request", "issues", "commits"]
            },
            "trello": {
                "webhook": None,
                "canal": "#📋-proyectos",
                "eventos": ["tarjeta_creada", "lista_cambiada"]
            }
        }
    
    async def configurar_webhooks(self, guild):
        """Configurar webhooks para integraciones"""
        for plataforma, config in self.integraciones.items():
            # Buscar canal de integración
            canal = discord.utils.get(guild.text_channels, name=config['canal'].replace('#', ''))
            
            if not canal:
                # Crear canal si no existe
                categoria = discord.utils.get(guild.categories, name="💻 Desarrollo")
                canal = await guild.create_text_channel(
                    name=config['canal'].replace('#', ''), 
                    category=categoria
                )
            
            # Crear webhook
            try:
                webhook = await canal.create_webhook(name=f"Webhook {plataforma}")
                
                # Almacenar URL del webhook
                config['webhook'] = webhook.url
                
                # Notificar configuración
                embed = discord.Embed(
                    title=f"🔗 Integración {plataforma.capitalize()} Configurada",
                    description=f"Webhook creado para el canal {canal.mention}",
                    color=discord.Color.green()
                )
                await canal.send(embed=embed)
            
            except discord.Forbidden:
                print(f"No se pudo crear webhook para {plataforma}")
    
    async def manejar_evento_github(self, payload):
        """Manejar eventos de GitHub"""
        canal_integraciones = discord.utils.get(self.bot.get_all_channels(), name="🔗-integraciones")
        
        if canal_integraciones:
            # Procesar diferentes tipos de eventos
            if payload.get('action') == 'opened':
                if 'pull_request' in payload:
                    pr = payload['pull_request']
                    embed = discord.Embed(
                        title="🔧 Nuevo Pull Request",
                        description=f"[{pr['title']}]({pr['html_url']})",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Repositorio", value=payload['repository']['full_name'], inline=True)
                    embed.add_field(name="Autor", value=pr['user']['login'], inline=True)
                    
                    await canal_integraciones.send(embed=embed)
                
                elif 'issue' in payload:
                    issue = payload['issue']
                    embed = discord.Embed(
                        title="📋 Nueva Issue",
                        description=f"[{issue['title']}]({issue['html_url']})",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Repositorio", value=payload['repository']['full_name'], inline=True)
                    embed.add_field(name="Autor", value=issue['user']['login'], inline=True)
                    
                    await canal_integraciones.send(embed=embed)
    
    async def manejar_evento_trello(self, payload):
        """Manejar eventos de Trello"""
        canal_proyectos = discord.utils.get(self.bot.get_all_channels(), name="📋-proyectos")
        
        if canal_proyectos:
            # Procesar diferentes tipos de eventos de Trello
            if payload.get('action') == 'createCard':
                embed = discord.Embed(
                    title="📇 Nueva Tarjeta Creada",
                    description=payload.get('card', {}).get('name', 'Sin nombre'),
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Lista", 
                    value=payload.get('list', {}).get('name', 'Sin lista'), 
                    inline=True
                )
                
                await canal_proyectos.send(embed=embed)
    
    async def sincronizar_repositorio(self, ctx, url_repositorio):
        """Sincronizar repositorio de GitHub con el servidor"""
        # Validar URL de repositorio
        if not url_repositorio.startswith('https://github.com/'):
            await ctx.send("Por favor, proporciona una URL válida de GitHub.")
            return
        
        # Obtener información del repositorio
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url_repositorio}.git") as response:
                if response.status == 200:
                    # Crear canal para el repositorio
                    nombre_canal = f"🔗-{url_repositorio.split('/')[-1]}"
                    categoria = discord.utils.get(ctx.guild.categories, name="💻 Desarrollo")
                    
                    canal = await ctx.guild.create_text_channel(
                        name=nombre_canal, 
                        category=categoria
                    )
                    
                    embed = discord.Embed(
                        title="🔗 Repositorio Sincronizado",
                        description=f"Repositorio: {url_repositorio}",
                        color=discord.Color.blue()
                    )
                    await canal.send(embed=embed)
                    
                    await ctx.send(f"Repositorio sincronizado en {canal.mention}")
                else:
                    await ctx.send("No se pudo sincronizar el repositorio. Verifica la URL.")
