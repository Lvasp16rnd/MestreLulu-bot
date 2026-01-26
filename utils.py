# Roles de admin em ordem de prioridade
ADMIN_ROLES = [
    "líderes", "lideres",
    "admins", "admin",
    "administradores", "administrador",
    "administração", "administracao",
    "moderadores", "moderador",
    "staff"
]

def eh_admin(ctx):
    """Verifica se o usuário é admin por role ou permissão do servidor."""
    # Primeiro verifica permissão nativa do Discord
    if ctx.author.guild_permissions.administrator:
        return True
    
    # Depois verifica se tem alguma das roles de admin
    if hasattr(ctx.author, 'roles'):
        user_roles = [role.name.lower() for role in ctx.author.roles]
        for admin_role in ADMIN_ROLES:
            if admin_role in user_roles:
                return True
    
    return False
