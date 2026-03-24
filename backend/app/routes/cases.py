from flask import request, jsonify
from app.routes import api
from app import db
from app.models.case import Case, CaseAddress
from app.models.user import User
from app.models.classification import Classification
from app.utils.auth import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@api.route('/cases', methods=['GET'])

def get_cases():
    """Get all cases for the current user with optional filtering"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        status = request.args.get('status', 'all')
        priority = request.args.get('priority', 'all')
        
        # Start with base query - only show cases created by current user
        query = Case.query.filter(Case.created_by == current_user.id)
        
        # Apply filters
        if status != 'all':
            query = query.filter(Case.status == status)
        if priority != 'all':
            query = query.filter(Case.priority == priority)
        
        # Order by creation date (newest first)
        cases = query.order_by(Case.created_at.desc()).all()
        
        return jsonify({
            'cases': [case.to_dict() for case in cases]
        })
        
    except Exception as e:
        logger.error(f"Error fetching cases: {str(e)}")
        return jsonify({'error': 'Failed to fetch cases'}), 500

@api.route('/cases/<int:case_id>', methods=['GET'])

def get_case(case_id):
    """Get a specific case with all its addresses (only if owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        return jsonify(case.to_dict_with_addresses(user_id=current_user.id))
        
    except Exception as e:
        logger.error(f"Error fetching case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch case'}), 500

@api.route('/cases', methods=['POST'])

def create_case():
    """Create a new case"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Case name is required'}), 400
        
        new_case = Case(
            name=data['name'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            tags=data.get('tags', []),
            created_by=current_user.id,
            assigned_to=data.get('assigned_to')
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('case_created', {
            'case_id': new_case.id,
            'case_name': new_case.name
        })
        
        return jsonify(new_case.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating case: {str(e)}")
        return jsonify({'error': 'Failed to create case'}), 500

@api.route('/cases/<int:case_id>', methods=['PUT'])

def update_case(case_id):
    """Update an existing case (only if owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'name' in data:
            case.name = data['name']
        if 'description' in data:
            case.description = data['description']
        if 'status' in data:
            case.status = data['status']
            if data['status'] == 'closed':
                case.closed_at = datetime.utcnow()
        if 'priority' in data:
            case.priority = data['priority']
        if 'tags' in data:
            case.tags = data['tags']
        if 'assigned_to' in data:
            case.assigned_to = data['assigned_to']
        
        case.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('case_updated', {
            'case_id': case.id,
            'case_name': case.name
        })
        
        return jsonify(case.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to update case'}), 500

@api.route('/cases/<int:case_id>', methods=['DELETE'])

def delete_case(case_id):
    """Delete a case and all its addresses (only if owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        # Log the activity before deletion
        current_user.log_activity('case_deleted', {
            'case_id': case.id,
            'case_name': case.name
        })
        
        db.session.delete(case)
        db.session.commit()
        
        return jsonify({'message': 'Case deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete case'}), 500

@api.route('/cases/<int:case_id>/addresses', methods=['POST'])

def add_address_to_case(case_id):
    """Add an address to a case (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        data = request.get_json()
        if not data or 'address' not in data:
            return jsonify({'error': 'Address is required'}), 400
        
        # Check if address already exists in this case
        existing_address = CaseAddress.query.filter_by(
            case_id=case_id, 
            address=data['address']
        ).first()
        
        if existing_address:
            return jsonify({'error': 'Address already exists in this case'}), 400
        
        # Get classification data if available (only for current user)
        classification = Classification.query.filter_by(
            address=data['address'],
            created_by=current_user.id
        ).first()
        
        # If no classification exists, try to classify the address
        if not classification:
            try:
                from app.services import FeatureService, MLService
                import os
                
                # Initialize services
                feature_service = FeatureService()
                ml_service = MLService()
                
                # Extract features and classify
                features = feature_service.extract_features(data['address'])
                prediction_result = ml_service.predict(features, address=data['address'])
                
                # Create classification record with current user
                classification = Classification(
                    address=data['address'],
                    classification=int(prediction_result['prediction']),
                    confidence=round(float(prediction_result['confidence']), 8),
                    features=features,
                    created_by=current_user.id
                )
                db.session.add(classification)
                db.session.commit()
                
                logger.info(f"Auto-classified address {data['address']} for case {case_id}")
                
            except Exception as e:
                logger.warning(f"Failed to auto-classify address {data['address']}: {str(e)}")
                # Continue without classification
        
        # Determine classification and risk score
        if classification:
            # Map classification number to text
            classification_map = {
                0: 'normal', 1: 'suspicious', 2: 'suspicious', 3: 'suspicious',
                4: 'suspicious', 5: 'suspicious', 6: 'suspicious', 7: 'suspicious',
                8: 'suspicious', 9: 'suspicious', 10: 'suspicious', 11: 'suspicious', 12: 'normal'
            }
            classification_text = classification_map.get(classification.classification, 'unknown')
            risk_score = classification.confidence
        else:
            classification_text = 'unknown'
            risk_score = 0.0
        
        new_address = CaseAddress(
            case_id=case_id,
            address=data['address'],
            classification=classification_text,
            risk_score=risk_score,
            note=data.get('note', ''),
            added_by=current_user.id
        )
        
        db.session.add(new_address)
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('address_added_to_case', {
            'case_id': case_id,
            'case_name': case.name,
            'address': data['address']
        })
        
        return jsonify(new_address.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error adding address to case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to add address to case'}), 500

@api.route('/cases/<int:case_id>/addresses/bulk', methods=['POST'])

def add_addresses_bulk_to_case(case_id):
    """Add multiple addresses to a case in bulk (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        data = request.get_json()
        if not data or 'addresses' not in data:
            return jsonify({'error': 'Addresses list is required'}), 400
        
        addresses = data['addresses']
        if not isinstance(addresses, list) or len(addresses) == 0:
            return jsonify({'error': 'Addresses must be a non-empty list'}), 400
        
        added_addresses = []
        skipped_addresses = []
        
        for address_data in addresses:
            address = address_data if isinstance(address_data, str) else address_data.get('address', '')
            note = address_data.get('note', '') if isinstance(address_data, dict) else ''
            
            if not address:
                continue
                
            # Check if address already exists in this case
            existing_address = CaseAddress.query.filter_by(
                case_id=case_id, 
                address=address
            ).first()
            
            if existing_address:
                skipped_addresses.append(address)
                continue
            
            # Get or create classification (only for current user)
            classification = Classification.query.filter_by(
                address=address,
                created_by=current_user.id
            ).first()
            
            if not classification:
                try:
                    from app.services import FeatureService, MLService
                    
                    feature_service = FeatureService()
                    ml_service = MLService()
                    
                    features = feature_service.extract_features(address)
                    prediction_result = ml_service.predict(features, address=address)
                    
                    classification = Classification(
                        address=address,
                        classification=int(prediction_result['prediction']),
                        confidence=round(float(prediction_result['confidence']), 8),
                        features=features,
                        created_by=current_user.id
                    )
                    db.session.add(classification)
                    db.session.commit()
                    
                except Exception as e:
                    logger.warning(f"Failed to classify address {address}: {str(e)}")
            
            # Determine classification and risk score
            if classification:
                classification_map = {
                    0: 'normal', 1: 'suspicious', 2: 'suspicious', 3: 'suspicious',
                    4: 'suspicious', 5: 'suspicious', 6: 'suspicious', 7: 'suspicious',
                    8: 'suspicious', 9: 'suspicious', 10: 'suspicious', 11: 'suspicious', 12: 'normal'
                }
                classification_text = classification_map.get(classification.classification, 'unknown')
                risk_score = classification.confidence
            else:
                classification_text = 'unknown'
                risk_score = 0.0
            
            new_address = CaseAddress(
                case_id=case_id,
                address=address,
                classification=classification_text,
                risk_score=risk_score,
                note=note,
                added_by=current_user.id
            )
            
            db.session.add(new_address)
            added_addresses.append(new_address.to_dict())
        
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('addresses_added_bulk_to_case', {
            'case_id': case_id,
            'case_name': case.name,
            'addresses_added': len(added_addresses),
            'addresses_skipped': len(skipped_addresses)
        })
        
        return jsonify({
            'message': f'Successfully added {len(added_addresses)} addresses to case',
            'added_addresses': added_addresses,
            'skipped_addresses': skipped_addresses,
            'total_added': len(added_addresses),
            'total_skipped': len(skipped_addresses)
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding addresses in bulk to case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to add addresses in bulk'}), 500

@api.route('/cases/<int:case_id>/addresses/<int:address_id>', methods=['DELETE'])

def remove_address_from_case(case_id, address_id):
    """Remove an address from a case (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        address = CaseAddress.query.filter_by(
            case_id=case_id, 
            id=address_id
        ).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        # Log the activity before deletion
        current_user.log_activity('address_removed_from_case', {
            'case_id': case_id,
            'case_name': case.name,
            'address': address.address
        })
        
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({'message': 'Address removed from case successfully'})
        
    except Exception as e:
        logger.error(f"Error removing address from case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to remove address from case'}), 500

@api.route('/cases/<int:case_id>/addresses/<int:address_id>/refresh', methods=['POST'])

def refresh_address_classification(case_id, address_id):
    """Refresh classification for an address in a case (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        address = CaseAddress.query.filter_by(
            case_id=case_id, 
            id=address_id
        ).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        # Get or create classification (only for current user)
        classification = Classification.query.filter_by(
            address=address.address,
            created_by=current_user.id
        ).first()
        
        if not classification:
            try:
                from app.services import FeatureService, MLService
                
                feature_service = FeatureService()
                ml_service = MLService()
                
                features = feature_service.extract_features(address.address)
                prediction_result = ml_service.predict(features, address=address.address)
                
                classification = Classification(
                    address=address.address,
                    classification=int(prediction_result['prediction']),
                    confidence=round(float(prediction_result['confidence']), 8),
                    features=features,
                    created_by=current_user.id
                )
                db.session.add(classification)
                db.session.commit()
                
            except Exception as e:
                logger.warning(f"Failed to classify address {address.address}: {str(e)}")
                return jsonify({'error': f'Failed to classify address: {str(e)}'}), 500
        
        # Update address with new classification
        classification_map = {
            0: 'normal', 1: 'suspicious', 2: 'suspicious', 3: 'suspicious',
            4: 'suspicious', 5: 'suspicious', 6: 'suspicious', 7: 'suspicious',
            8: 'suspicious', 9: 'suspicious', 10: 'suspicious', 11: 'suspicious', 12: 'normal'
        }
        classification_text = classification_map.get(classification.classification, 'unknown')
        
        address.classification = classification_text
        address.risk_score = classification.confidence
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('address_classification_refreshed', {
            'case_id': case_id,
            'case_name': case.name,
            'address': address.address,
            'new_classification': classification_text,
            'new_risk_score': classification.confidence
        })
        
        return jsonify(address.to_dict())
        
    except Exception as e:
        logger.error(f"Error refreshing classification for address {address_id} in case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to refresh classification'}), 500

@api.route('/cases/<int:case_id>/addresses/<int:address_id>', methods=['PUT'])

def update_case_address(case_id, address_id):
    """Update an address in a case (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        address = CaseAddress.query.filter_by(
            case_id=case_id, 
            id=address_id
        ).first()
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'note' in data:
            address.note = data['note']
        if 'classification' in data:
            address.classification = data['classification']
        if 'risk_score' in data:
            address.risk_score = data['risk_score']
        
        db.session.commit()
        
        # Log the activity
        current_user.log_activity('case_address_updated', {
            'case_id': case_id,
            'case_name': case.name,
            'address': address.address
        })
        
        return jsonify(address.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating address in case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to update address'}), 500

@api.route('/cases/<int:case_id>/export', methods=['POST'])

def export_case(case_id):
    """Export case data (only if case is owned by current user)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        case = Case.query.filter_by(id=case_id, created_by=current_user.id).first()
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        # Log the export request
        current_user.log_activity('case_exported', {
            'case_id': case_id,
            'case_name': case.name
        })
        
        # In a real implementation, this would generate and return a file
        # For now, just return the case data (filtered by user)
        return jsonify({
            'message': 'Case export requested successfully',
            'export_id': f'case_export_{case_id}_{int(datetime.utcnow().timestamp())}',
            'case_data': case.to_dict_with_addresses(user_id=current_user.id)
        })
        
    except Exception as e:
        logger.error(f"Error exporting case {case_id}: {str(e)}")
        return jsonify({'error': 'Failed to export case'}), 500

@api.route('/cases/stats', methods=['GET'])

def get_case_stats():
    """Get case statistics for the current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Filter all queries by current user
        user_cases_query = Case.query.filter(Case.created_by == current_user.id)
        
        total_cases = user_cases_query.count()
        active_cases = user_cases_query.filter_by(status='active').count()
        closed_cases = user_cases_query.filter_by(status='closed').count()
        
        # Get cases by priority for current user
        priority_stats = db.session.query(
            Case.priority,
            db.func.count(Case.id).label('count')
        ).filter(Case.created_by == current_user.id).group_by(Case.priority).all()
        
        priority_distribution = {priority: count for priority, count in priority_stats}
        
        # Get recent activity (last 7 days) for current user
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_cases = user_cases_query.filter(Case.created_at >= week_ago).count()
        
        return jsonify({
            'total_cases': total_cases,
            'active_cases': active_cases,
            'closed_cases': closed_cases,
            'priority_distribution': priority_distribution,
            'recent_cases': recent_cases
        })
        
    except Exception as e:
        logger.error(f"Error fetching case stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch case statistics'}), 500
