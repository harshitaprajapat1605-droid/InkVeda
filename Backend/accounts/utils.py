def is_admin(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'admin'

def is_user(user):
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'user'
