from flask import request, jsonify, session
from app.routes import api
from app import db
from app.models.user import User, UserPreferences, UserNotifications, UserSession, UserActivityLog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@api.route('/users/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        # For now, return a default user profile
        # In a real implementation, this would get the user from the session
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict_with_preferences())
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@api.route('/users/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # For now, update the admin user
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update basic profile fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        
        # Log the activity
        user.log_activity('profile_updated', data)
        
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@api.route('/users/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.preferences:
            # Create default preferences if they don't exist
            user.preferences = UserPreferences(user_id=user.id)
            db.session.commit()
        
        return jsonify(user.preferences.to_dict())
    except Exception as e:
        logger.error(f"Error fetching user preferences: {str(e)}")
        return jsonify({'error': 'Failed to fetch preferences'}), 500

@api.route('/users/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.preferences:
            user.preferences = UserPreferences(user_id=user.id)
        
        # Update preference fields
        if 'default_risk_threshold' in data:
            user.preferences.default_risk_threshold = data['default_risk_threshold']
        if 'auto_save_cases' in data:
            user.preferences.auto_save_cases = data['auto_save_cases']
        if 'theme' in data:
            user.preferences.theme = data['theme']
        if 'language' in data:
            user.preferences.language = data['language']
        if 'timezone' in data:
            user.preferences.timezone = data['timezone']
        
        db.session.commit()
        
        # Log the activity
        user.log_activity('preferences_updated', data)
        
        return jsonify(user.preferences.to_dict())
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

@api.route('/users/notifications', methods=['GET'])
def get_notifications():
    """Get user notification settings"""
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.notifications:
            # Create default notification settings if they don't exist
            user.notifications = UserNotifications(user_id=user.id)
            db.session.commit()
        
        return jsonify(user.notifications.to_dict())
    except Exception as e:
        logger.error(f"Error fetching user notifications: {str(e)}")
        return jsonify({'error': 'Failed to fetch notifications'}), 500

@api.route('/users/notifications', methods=['PUT'])
def update_notifications():
    """Update user notification settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.notifications:
            user.notifications = UserNotifications(user_id=user.id)
        
        # Update notification fields
        if 'email_notifications' in data:
            user.notifications.email_notifications = data['email_notifications']
        if 'browser_notifications' in data:
            user.notifications.browser_notifications = data['browser_notifications']
        if 'high_risk_only' in data:
            user.notifications.high_risk_only = data['high_risk_only']
        if 'daily_summary' in data:
            user.notifications.daily_summary = data['daily_summary']
        if 'weekly_report' in data:
            user.notifications.weekly_report = data['weekly_report']
        
        db.session.commit()
        
        # Log the activity
        user.log_activity('notifications_updated', data)
        
        return jsonify(user.notifications.to_dict())
    except Exception as e:
        logger.error(f"Error updating user notifications: {str(e)}")
        return jsonify({'error': 'Failed to update notifications'}), 500

@api.route('/users/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current and new password required'}), 400
        
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        # Update password
        user.password_hash = user._hash_password(data['new_password'])
        db.session.commit()
        
        # Log the activity
        user.log_activity('password_changed')
        
        return jsonify({'message': 'Password changed successfully'})
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500

@api.route('/users/activity', methods=['GET'])
def get_activity():
    """Get user activity log"""
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        activities = UserActivityLog.query.filter(
            UserActivityLog.user_id == user.id,
            UserActivityLog.created_at >= thirty_days_ago
        ).order_by(UserActivityLog.created_at.desc()).limit(100).all()
        
        return jsonify({
            'activities': [activity.to_dict() for activity in activities]
        })
    except Exception as e:
        logger.error(f"Error fetching user activity: {str(e)}")
        return jsonify({'error': 'Failed to fetch activity'}), 500

@api.route('/users/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Count user's classifications
        classification_count = len(user.classifications)
        
        # Count user's alerts
        alert_count = len(user.alerts)
        
        # Count active alerts
        active_alerts = len([alert for alert in user.alerts if alert.status == 'active'])
        
        # Get recent activity count (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = UserActivityLog.query.filter(
            UserActivityLog.user_id == user.id,
            UserActivityLog.created_at >= week_ago
        ).count()
        
        return jsonify({
            'classifications_count': classification_count,
            'alerts_count': alert_count,
            'active_alerts_count': active_alerts,
            'recent_activity_count': recent_activity,
            'account_age_days': (datetime.utcnow() - user.created_at).days
        })
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch stats'}), 500

@api.route('/users/export-data', methods=['POST'])
def export_user_data():
    """Export user data"""
    try:
        user = User.query.filter_by(username='admin').first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Log the export request
        user.log_activity('data_export_requested')
        
        # In a real implementation, this would generate and return a file
        # For now, just return a success message
        return jsonify({
            'message': 'Data export requested successfully',
            'export_id': f'export_{user.id}_{int(datetime.utcnow().timestamp())}'
        })
    except Exception as e:
        logger.error(f"Error requesting data export: {str(e)}")
        return jsonify({'error': 'Failed to request data export'}), 500
