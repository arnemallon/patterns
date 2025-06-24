from app import db
from datetime import datetime
import json

class Classification(db.Model):
    __tablename__ = 'classifications'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False, index=True)
    classification = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float(precision=8), nullable=False)
    features = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'classification': int(self.classification),
            'confidence': round(float(self.confidence), 8),
            'features': self.features,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Classification {self.address}: {self.classification}>' 