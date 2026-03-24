from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app import db
import secrets
import hashlib

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(20), default='investigator')
    status = Column(String(20), default='active')
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    notifications = relationship("UserNotifications", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    classifications = relationship("Classification", back_populates="creator")
    alerts = relationship("Alert", back_populates="creator")
    activity_log = relationship("UserActivityLog", back_populates="user")
    created_cases = relationship("Case", foreign_keys="Case.created_by", back_populates="creator")
    assigned_cases = relationship("Case", foreign_keys="Case.assigned_to", back_populates="assignee")
    
    def __init__(self, username, email, password, first_name=None, last_name=None, role='investigator'):
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return self.password_hash == self._hash_password(password)
    
    def create_session(self, ip_address=None, user_agent=None):
        """Create a new session for the user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        session = UserSession(
            user_id=self.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(session)
        db.session.commit()
        
        return session_token
    
    def log_activity(self, action, details=None, ip_address=None, user_agent=None):
        """Log user activity"""
        log_entry = UserActivityLog(
            user_id=self.id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_with_preferences(self):
        """Convert user to dictionary including preferences"""
        user_dict = self.to_dict()
        if self.preferences:
            user_dict['preferences'] = self.preferences.to_dict()
        if self.notifications:
            user_dict['notifications'] = self.notifications.to_dict()
        return user_dict

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    default_risk_threshold = Column(Numeric(3, 2), default=0.5)
    auto_save_cases = Column(Boolean, default=True)
    theme = Column(String(20), default='light')
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'default_risk_threshold': float(self.default_risk_threshold),
            'auto_save_cases': self.auto_save_cases,
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserNotifications(db.Model):
    __tablename__ = 'user_notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_notifications = Column(Boolean, default=True)
    browser_notifications = Column(Boolean, default=True)
    high_risk_only = Column(Boolean, default=False)
    daily_summary = Column(Boolean, default=True)
    weekly_report = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        """Convert notifications to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_notifications': self.email_notifications,
            'browser_notifications': self.browser_notifications,
            'high_risk_only': self.high_risk_only,
            'daily_summary': self.daily_summary,
            'weekly_report': self.weekly_report,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(Text)  # Using Text for compatibility
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(db.JSON)  # Using db.JSON for SQLite compatibility
    ip_address = Column(Text)  # Using Text for compatibility
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activity_log")
    
    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }
