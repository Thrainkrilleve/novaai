"""
Shared Discord state between discord_bot.py and main.py
This allows the web API to access Discord bot information
"""

# Global reference to the Discord bot instance
discord_bot = None

def set_bot(bot):
    """Set the Discord bot instance"""
    global discord_bot
    discord_bot = bot

def get_bot():
    """Get the Discord bot instance"""
    return discord_bot

def is_bot_ready():
    """Check if Discord bot is connected"""
    return discord_bot is not None and discord_bot.is_ready()

def get_friends():
    """Get list of friends"""
    if not is_bot_ready():
        return []
    
    try:
        friends = []
        for friend in discord_bot.user.friends:
            friends.append({
                "id": str(friend.id),
                "name": friend.name,
                "discriminator": friend.discriminator,
                "avatar": str(friend.avatar.url) if friend.avatar else None,
                "display_name": friend.display_name if hasattr(friend, 'display_name') else friend.name
            })
        return friends
    except:
        return []

def get_pending_requests():
    """Get pending friend requests"""
    if not is_bot_ready():
        return {"incoming": [], "outgoing": []}
    
    try:
        incoming = []
        outgoing = []
        
        for relationship in discord_bot.user.relationships:
            user_data = {
                "id": str(relationship.user.id),
                "name": relationship.user.name,
                "discriminator": relationship.user.discriminator,
                "avatar": str(relationship.user.avatar.url) if relationship.user.avatar else None
            }
            
            if relationship.type.name == 'incoming_request' or relationship.type.name == 'incoming':
                incoming.append(user_data)
            elif relationship.type.name == 'outgoing_request' or relationship.type.name == 'outgoing':
                outgoing.append(user_data)
        
        return {"incoming": incoming, "outgoing": outgoing}
    except:
        return {"incoming": [], "outgoing": []}

def get_user_info():
    """Get current user information"""
    if not is_bot_ready():
        return None
    
    try:
        user = discord_bot.user
        return {
            "id": str(user.id),
            "name": user.name,
            "discriminator": user.discriminator,
            "avatar": str(user.avatar.url) if user.avatar else None,
            "display_name": user.display_name if hasattr(user, 'display_name') else user.name
        }
    except:
        return None
