from flask import request, jsonify
from app.routes import api
from app import db
from app.models import Alert
from app.utils.auth import get_current_user
from datetime import datetime


@api.route('/alerts', methods=['GET'])
def list_alerts():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        alerts = Alert.query.filter(Alert.created_by == current_user.id).order_by(Alert.created_at.desc()).all()
        return jsonify({'alerts': [a.to_dict() for a in alerts]})
    except Exception as exc:
        return jsonify({'error': 'Failed to fetch alerts', 'details': str(exc)}), 500


@api.route('/alerts/triggered', methods=['GET'])
def list_triggered_alerts():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        triggered_alerts = Alert.query.filter(
            Alert.created_by == current_user.id,
            Alert.trigger_count > 0
        ).order_by(Alert.last_triggered.desc()).all()
        return jsonify({'alerts': [a.to_dict() for a in triggered_alerts]})
    except Exception as exc:
        return jsonify({'error': 'Failed to fetch triggered alerts', 'details': str(exc)}), 500


@api.route('/alerts', methods=['POST'])
def create_alert():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json() or {}
        address = (data.get('address') or '').strip()
        alert_type = data.get('type') or 'new_transaction'
        threshold = float(data.get('threshold') or 0.1)
        email = (data.get('email') or '').strip()

        if not address:
            return jsonify({'error': 'Address is required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        alert = Alert(
            address=address,
            type=alert_type,
            threshold=threshold,
            email=email,
            status='active',
            trigger_count=0,
            last_triggered=None,
            created_by=current_user.id
        )
        db.session.add(alert)
        db.session.commit()
        return jsonify({'alert': alert.to_dict()}), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to create alert', 'details': str(exc)}), 500


@api.route('/alerts/<int:alert_id>/toggle', methods=['POST'])
def toggle_alert(alert_id: int):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.filter_by(id=alert_id, created_by=current_user.id).first()
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        alert.status = 'paused' if alert.status == 'active' else 'active'
        db.session.commit()
        return jsonify({'alert': alert.to_dict()})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to toggle alert', 'details': str(exc)}), 500


@api.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id: int):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.filter_by(id=alert_id, created_by=current_user.id).first()
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        db.session.delete(alert)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete alert', 'details': str(exc)}), 500


