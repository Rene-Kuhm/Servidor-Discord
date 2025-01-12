import discord
from typing import Dict
from .database import DatabaseManager

class SistemaBienvenida:
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
    
    async def generar_embed_bienvenida(self, member):
        """Crear un embed de bienvenida personalizado"""
        embed = discord.Embed(
            title=f"¡Bienvenido {member.name}! 🎉",
            description=(
                "Estás a punto de entrar en una comunidad increíble de tecnología y desarrollo. \n\n"
                "🔍 Explora nuestros canales\n"
                "🤝 Conéctate con otros miembros\n"
                "📚 Aprende y crece con nosotros"
            ),
            color=discord.Color.blue()
        )
        
        # Personalizar según información del miembro
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🌐 Servidor", value=member.guild.name, inline=True)
        embed.add_field(name="📅 Fecha de Unión", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        
        # Información adicional
        embed.add_field(
            name="🚀 Próximos Pasos", 
            value=(
                "1. Lee las reglas en #📋-reglas\n"
                "2. Preséntate en #🏠-bienvenida\n"
                "3. Elige tus roles en #🎭-roles"
            ),
            inline=False
        )
        
        return embed
    
    async def bienvenida_personalizada(self, member):
        """Proceso de bienvenida personalizado"""
        # Registrar usuario en base de datos
        await self.db_manager.agregar_usuario(member.id, member.name)
        
        # Canal de bienvenida
        canal_bienvenida = discord.utils.get(member.guild.text_channels, name="🏠-bienvenida")
        
        if canal_bienvenida:
            # Embed de bienvenida
            embed = await self.generar_embed_bienvenida(member)
            await canal_bienvenida.send(embed=embed)
            
            # Mensaje directo al nuevo miembro
            try:
                await member.send(
                    "¡Bienvenido a nuestra comunidad! "
                    "Te recomendamos completar tu perfil y explorar nuestros canales."
                )
            except:
                # Si no se puede enviar MD, notificar en canal de bienvenida
                await canal_bienvenida.send(f"{member.mention} ¡Bienvenido!")
            
            # Asignar rol de nuevo miembro
            rol_nuevo = discord.utils.get(member.guild.roles, name="🆕 Nuevo Miembro")
            if not rol_nuevo:
                rol_nuevo = await member.guild.create_role(name="🆕 Nuevo Miembro")
            
            await member.add_roles(rol_nuevo)
    
    async def sistema_presentacion(self, ctx, presentacion):
        """Sistema para que los nuevos miembros se presenten"""
        # Canal de presentaciones
        canal_presentaciones = discord.utils.get(ctx.guild.text_channels, name="🏠-bienvenida")
        
        if canal_presentaciones:
            embed = discord.Embed(
                title=f"🤝 Presentación de {ctx.author.name}",
                description=presentacion,
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            # Enviar presentación
            await canal_presentaciones.send(embed=embed)
            
            # Asignar rol de miembro activo
            rol_activo = discord.utils.get(ctx.guild.roles, name="🌟 Miembro Activo")
            if not rol_activo:
                rol_activo = await ctx.guild.create_role(name="🌟 Miembro Activo")
            
            await ctx.author.add_roles(rol_activo)
            
            await ctx.send("¡Presentación publicada exitosamente! Bienvenido a la comunidad.")
