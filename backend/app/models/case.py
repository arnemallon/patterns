from app import db
from datetime import datetime
import json

class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, closed, archived
    priority = db.Column(db.String(50), default='medium')  # low, medium, high, critical
    tags = db.Column(db.JSON)  # Array of tags for categorization
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship("User", foreign_keys=[created_by], back_populates="created_cases")
    assignee = db.relationship("User", foreign_keys=[assigned_to], back_populates="assigned_cases")
    addresses = db.relationship("CaseAddress", back_populates="case", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert case to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'tags': self.tags or [],
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'addresses_count': len(self.addresses)
        }
    
    def to_dict_with_addresses(self, user_id=None):
        """Convert case to dictionary including addresses (optionally filtered by user)"""
        case_dict = self.to_dict()
        if user_id:
            # Filter addresses by the user who added them
            user_addresses = [addr for addr in self.addresses if addr.added_by == user_id]
            case_dict['addresses'] = [addr.to_dict() for addr in user_addresses]
            case_dict['addresses_count'] = len(user_addresses)
        else:
            case_dict['addresses'] = [addr.to_dict() for addr in self.addresses]
        return case_dict
    
    def __repr__(self):
        return f'<Case {self.name}>'

class CaseAddress(db.Model):
    __tablename__ = 'case_addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    classification = db.Column(db.String(50))  # suspicious, normal, unknown
    risk_score = db.Column(db.Float, default=0.0)
    note = db.Column(db.Text)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    case = db.relationship("Case", back_populates="addresses")
    adder = db.relationship("User", foreign_keys=[added_by])
    
    def to_dict(self):
        """Convert case address to dictionary"""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'address': self.address,
            'classification': self.classification,
            'risk_score': self.risk_score,
            'note': self.note,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
    
    def __repr__(self):
        return f'<CaseAddress {self.address} in case {self.case_id}>'
