from app import db
from datetime import datetime


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    threshold = db.Column(db.Float, nullable=False, default=0.1)
    email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    trigger_count = db.Column(db.Integer, nullable=False, default=0)
    last_triggered = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    creator = db.relationship("User", back_populates="alerts")

    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'type': self.type,
            'threshold': float(self.threshold) if self.threshold is not None else None,
            'email': self.email,
            'status': self.status,
            'trigger_count': int(self.trigger_count) if self.trigger_count is not None else 0,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Alert {self.address} {self.type} {self.status}>"


