from app.models.user import User
import logging

logger = logging.getLogger(__name__)

def get_current_user():
    """
    Return the default admin user. Authentication has been removed;
    the app is publicly accessible.
    """
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User.query.first()
        return user
    except Exception as e:
        logger.error(f"Error getting default user: {str(e)}")
        return None
