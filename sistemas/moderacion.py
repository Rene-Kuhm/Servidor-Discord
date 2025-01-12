import discord
from discord.ext import commands
import asyncio
import logging

class SistemaModeración:
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        
        # Configuración de sistemas de moderación
        self.config = {
            "warn_limits": {
                "soft_warn": 3,
                "hard_warn": 5,
                "kick": 7,
                "ban": 10
            },
            "auto_mod_rules": {
                "invite_links": True,
                "spam_detection": True,
                "explicit_content": True
            }
        }
        
        # Diccionario para rastrear advertencias de usuarios
        self.user_warnings = {}
    
    async def registrar_advertencia(self, member, razon, severidad='leve'):
        """Registrar una advertencia para un usuario"""
        if member.id not in self.user_warnings:
            self.user_warnings[member.id] = []
        
        self.user_warnings[member.id].append({
            "razon": razon,
            "severidad": severidad,
            "timestamp": discord.utils.utcnow()
        })
        
        # Verificar límites de advertencias
        total_warns = len(self.user_warnings[member.id])
        
        # Crear embed de advertencia
        embed = discord.Embed(
            title="⚠️ Sistema de Moderación - Advertencia",
            description=f"Usuario {member.mention} ha recibido una advertencia.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Razón", value=razon, inline=False)
        embed.add_field(name="Número de Advertencias", value=f"{total_warns}/{self.config['warn_limits']['ban']}", inline=False)
        
        # Buscar canal de moderación
        mod_channel = discord.utils.get(member.guild.text_channels, name="registro-moderacion")
        if mod_channel:
            await mod_channel.send(embed=embed)
        
        # Acciones según número de advertencias
        if total_warns >= self.config['warn_limits']['ban']:
            await self.ban_usuario(member, "Límite máximo de advertencias alcanzado")
        elif total_warns >= self.config['warn_limits']['kick']:
            await self.kick_usuario(member, "Múltiples advertencias")
    
    async def kick_usuario(self, member, razon="Comportamiento inapropiado"):
        """Expulsar a un usuario del servidor"""
        try:
            await member.kick(reason=razon)
            
            # Notificar en canal de moderación
            embed = discord.Embed(
                title="🚫 Usuario Expulsado",
                description=f"{member.mention} ha sido expulsado del servidor.",
                color=discord.Color.red()
            )
            embed.add_field(name="Razón", value=razon, inline=False)
            
            mod_channel = discord.utils.get(member.guild.text_channels, name="registro-moderacion")
            if mod_channel:
                await mod_channel.send(embed=embed)
            
            self.logger.info(f"Usuario {member} expulsado: {razon}")
        except Exception as e:
            self.logger.error(f"Error al expulsar usuario: {e}")
    
    async def ban_usuario(self, member, razon="Comportamiento grave"):
        """Banear a un usuario del servidor"""
        try:
            await member.ban(reason=razon)
            
            # Notificar en canal de moderación
            embed = discord.Embed(
                title="🔨 Usuario Baneado",
                description=f"{member.mention} ha sido baneado del servidor.",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Razón", value=razon, inline=False)
            
            mod_channel = discord.utils.get(member.guild.text_channels, name="registro-moderacion")
            if mod_channel:
                await mod_channel.send(embed=embed)
            
            self.logger.info(f"Usuario {member} baneado: {razon}")
        except Exception as e:
            self.logger.error(f"Error al banear usuario: {e}")
    
    async def configurar_canal_moderacion(self, guild):
        """Crear canal de registro de moderación"""
        # Buscar categoría de moderación
        categoria_mod = discord.utils.get(guild.categories, name="🛡️ Moderación")
        if not categoria_mod:
            categoria_mod = await guild.create_category("🛡️ Moderación")
        
        # Crear canal de registro de moderación
        canal_mod = discord.utils.get(guild.text_channels, name="registro-moderacion")
        if not canal_mod:
            canal_mod = await guild.create_text_channel(
                name="registro-moderacion", 
                category=categoria_mod,
                topic="Registro de acciones de moderación y alertas del servidor"
            )
        
        # Enviar mensaje de bienvenida
        embed = discord.Embed(
            title="🛡️ Canal de Moderación",
            description="Este canal registra todas las acciones de moderación del servidor.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Funciones", value=[
            "• Registro de advertencias",
            "• Notificaciones de expulsiones",
            "• Registro de baneos",
            "• Alertas de seguridad"
        ], inline=False)
        
        await canal_mod.send(embed=embed)
        
        self.logger.info("Canal de moderación configurado exitosamente")
    
    def setup(self, bot):
        """Configurar eventos de moderación"""
        @bot.event
        async def on_message(message):
            # Ignorar mensajes de bots
            if message.author.bot:
                return
            
            # Detección de spam de invitaciones
            if self.config['auto_mod_rules']['invite_links']:
                if 'discord.gg/' in message.content.lower():
                    await message.delete()
                    await self.registrar_advertencia(
                        message.author, 
                        "Publicación de enlace de invitación no autorizado"
                    )
            
            # Continuar procesamiento de comandos
            await bot.process_commands(message)
