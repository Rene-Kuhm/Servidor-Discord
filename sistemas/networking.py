import discord
from typing import Dict, List
from .database import DatabaseManager
import logging

class SistemaNetworking:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
        
        self.canales_networking = [
            {
                "name": "💼-oportunidades-laborales", 
                "category": "🤝 Comunidad", 
                "topic": "Comparte y encuentra ofertas de trabajo en tecnología",
                "reglas": [
                    "Solo publicar ofertas relacionadas con tecnología",
                    "Incluir detalles como: empresa, puesto, tecnologías, salario",
                    "No spam de reclutadores",
                    "Usar formato: Empresa | Puesto | Tecnologías | Salario"
                ]
            },
            {
                "name": "🤝-busco-equipo", 
                "category": "🤝 Comunidad", 
                "topic": "Encuentra colaboradores para proyectos",
                "reglas": [
                    "Describir proyecto claramente",
                    "Mencionar tecnologías y roles necesarios",
                    "Ser específico en requisitos",
                    "Incluir objetivo del proyecto y etapa actual"
                ]
            },
            {
                "name": "🌐-freelance", 
                "category": "🤝 Comunidad", 
                "topic": "Proyectos freelance y colaboraciones",
                "reglas": [
                    "Describir alcance del proyecto",
                    "Especificar tecnologías requeridas",
                    "Indicar presupuesto o forma de pago",
                    "Incluir plazo estimado de proyecto"
                ]
            }
        ]
        
        self.canal_general = {
            "name": "💬-comunidad-tech", 
            "category": "💡 Comunidad Principal", 
            "topic": "🚀 Canal principal para discusiones generales, networking y colaboración tecnológica",
            "reglas": [
                "Sé respetuoso y amable con todos los miembros",
                "Mantén las conversaciones relacionadas con tecnología y desarrollo",
                "Evita spam y contenido inapropiado",
                "Usa hilos para conversaciones extensas"
            ]
        }
    
    async def crear_canales_networking(self, guild):
        """Crear canales de networking"""
        import logging
        import discord
        logger = logging.getLogger('discord_bot')
        
        try:
            # Asegurar que la categoría exista
            categoria_comunidad = discord.utils.get(guild.categories, name="🤝 Comunidad")
            if not categoria_comunidad:
                categoria_comunidad = await guild.create_category("🤝 Comunidad")
                logger.info("Categoría 🤝 Comunidad creada")
            
            # Lista de canales a crear
            canales_a_crear = [
                {
                    "name": "💼-oportunidades-laborales", 
                    "topic": "Comparte y encuentra ofertas de trabajo en tecnología",
                    "reglas": [
                        "Solo publicar ofertas relacionadas con tecnología",
                        "Incluir detalles como: empresa, puesto, tecnologías, salario",
                        "No spam de reclutadores",
                        "Usar formato: Empresa | Puesto | Tecnologías | Salario"
                    ]
                },
                {
                    "name": "🤝-busco-equipo", 
                    "topic": "Encuentra colaboradores para proyectos",
                    "reglas": [
                        "Describir proyecto claramente",
                        "Mencionar tecnologías y roles necesarios",
                        "Ser específico en requisitos",
                        "Incluir objetivo del proyecto y etapa actual"
                    ]
                },
                {
                    "name": "🌐-freelance", 
                    "topic": "Proyectos freelance y colaboraciones",
                    "reglas": [
                        "Describir alcance del proyecto",
                        "Especificar tecnologías requeridas",
                        "Indicar presupuesto o forma de pago",
                        "Incluir plazo estimado de proyecto"
                    ]
                }
            ]
            
            # Crear cada canal
            for canal_config in canales_a_crear:
                # Verificar si el canal ya existe
                canal_existente = discord.utils.get(guild.text_channels, name=canal_config['name'])
                
                if canal_existente:
                    logger.info(f"Canal {canal_config['name']} ya existe. Actualizando.")
                    await canal_existente.edit(
                        name=canal_config['name'],
                        category=categoria_comunidad,
                        topic=canal_config['topic']
                    )
                    canal = canal_existente
                else:
                    # Crear nuevo canal
                    canal = await guild.create_text_channel(
                        name=canal_config['name'], 
                        category=categoria_comunidad, 
                        topic=canal_config['topic']
                    )
                    logger.info(f"Canal creado: {canal_config['name']}")
                
                # Enviar reglas
                embed_reglas = discord.Embed(
                    title="📋 Reglas del Canal",
                    description="\n".join([f"• {regla}" for regla in canal_config.get('reglas', [])]),
                    color=discord.Color.blue()
                )
                
                # Limpiar mensajes anteriores y enviar reglas
                await canal.purge(limit=10)
                await canal.send(embed=embed_reglas)
            
            # Crear canal general
            categoria_principal = discord.utils.get(guild.categories, name="💡 Comunidad Principal")
            if not categoria_principal:
                categoria_principal = await guild.create_category("💡 Comunidad Principal")
                logger.info("Categoría 💡 Comunidad Principal creada")
            
            # Verificar canal general
            canal_general_existente = discord.utils.get(guild.text_channels, name="💬-comunidad-tech")
            
            if canal_general_existente:
                logger.info("Canal general ya existe. Actualizando.")
                await canal_general_existente.edit(
                    name="💬-comunidad-tech",
                    category=categoria_principal,
                    topic="🚀 Canal principal para discusiones generales, networking y colaboración tecnológica"
                )
                canal_general = canal_general_existente
            else:
                # Crear nuevo canal general
                canal_general = await guild.create_text_channel(
                    name="💬-comunidad-tech", 
                    category=categoria_principal, 
                    topic="🚀 Canal principal para discusiones generales, networking y colaboración tecnológica"
                )
                logger.info("Canal general creado")
            
            # Mensaje de bienvenida
            embed = discord.Embed(
                title="🌟 Bienvenido a la Comunidad Tech",
                description="¡Este es el espacio principal para interacciones, networking y colaboración tecnológica!",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="🚀 Sobre este Canal", 
                value="Un lugar vibrante para compartir conocimientos, ideas y conectar con profesionales de tecnología.",
                inline=False
            )
            embed.add_field(
                name="📜 Reglas del Canal", 
                value="\n".join([
                    "• Sé respetuoso y amable con todos los miembros",
                    "• Mantén las conversaciones relacionadas con tecnología y desarrollo",
                    "• Evita spam y contenido inapropiado",
                    "• Usa hilos para conversaciones extensas"
                ]), 
                inline=False
            )
            
            # Limpiar mensajes anteriores y enviar nuevo embed
            await canal_general.purge(limit=10)
            await canal_general.send(embed=embed)
            
            logger.info("Creación de canales de networking completada exitosamente")
        
        except Exception as e:
            logger.error(f"Error al crear canales de networking: {e}")
            import traceback
            traceback.print_exc()
    
    async def publicar_oferta(self, ctx, detalles_oferta):
        """Publicar una oferta de trabajo"""
        canal_ofertas = discord.utils.get(ctx.guild.text_channels, name="💼-oportunidades-laborales")
        
        if not canal_ofertas:
            await ctx.send("Canal de oportunidades laborales no encontrado.")
            return
        
        embed_oferta = discord.Embed(
            title="🆕 Nueva Oferta de Trabajo",
            description=detalles_oferta,
            color=discord.Color.green()
        )
        embed_oferta.set_footer(text=f"Publicado por {ctx.author.name}")
        
        await canal_ofertas.send(embed=embed_oferta)
        await ctx.send("Oferta publicada exitosamente.")
    
    async def buscar_equipo(self, ctx, descripcion_proyecto):
        """Publicar búsqueda de equipo"""
        canal_equipo = discord.utils.get(ctx.guild.text_channels, name="🤝-busco-equipo")
        
        if not canal_equipo:
            await ctx.send("Canal de búsqueda de equipo no encontrado.")
            return
        
        embed_proyecto = discord.Embed(
            title="🤝 Buscando Colaboradores",
            description=descripcion_proyecto,
            color=discord.Color.blue()
        )
        embed_proyecto.set_footer(text=f"Publicado por {ctx.author.name}")
        
        await canal_equipo.send(embed=embed_proyecto)
        await ctx.send("Búsqueda de equipo publicada exitosamente.")
    
    async def publicar_freelance(self, ctx, detalles_proyecto):
        """Publicar proyecto freelance"""
        canal_freelance = discord.utils.get(ctx.guild.text_channels, name="🌐-freelance")
        
        if not canal_freelance:
            await ctx.send("Canal de proyectos freelance no encontrado.")
            return
        
        embed_freelance = discord.Embed(
            title="💻 Proyecto Freelance",
            description=detalles_proyecto,
            color=discord.Color.purple()
        )
        embed_freelance.set_footer(text=f"Publicado por {ctx.author.name}")
        
        await canal_freelance.send(embed=embed_freelance)
        await ctx.send("Proyecto freelance publicado exitosamente.")
