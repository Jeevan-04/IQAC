from nicegui import ui
from bson import ObjectId
from datetime import datetime

def create_admin_dashboard(admin_type, entity_id, entity_name, institution_id, main_color):
    """Create admin dashboard with proper sidebar and scope-based content"""
    
    # Get collections
    from main import criterias_col, extended_profiles_col, criteria_submissions_col, current_user
    
    # Get user details
    user = current_user
    if not user:
        ui.notify('User not authenticated', color='negative')
        return
    
    # Get scope-based criterias and profiles
    if admin_type == 'Program Admin':
        scope_filter = {'scope_type': 'program_based'}
        entity_filter = {'program_id': entity_id}
    else:  # Department Admin
        scope_filter = {'scope_type': 'department_based'}
        entity_filter = {'department_id': entity_id}
    
    # Get counts
    total_criterias = criterias_col.count_documents({
        'institution_id': ObjectId(institution_id),
        **scope_filter
    })
    
    total_profiles = extended_profiles_col.count_documents({
        'institution_id': ObjectId(institution_id),
        **scope_filter
    })
    
    # Get pending submissions count
    pending_submissions = criteria_submissions_col.count_documents({
        **entity_filter,
        'status': 'draft'
    })
    
    # Get completed submissions count
    completed_submissions = criteria_submissions_col.count_documents({
        **entity_filter,
        'status': 'submitted'
    })
    
    # Main dashboard content
    with ui.column().classes('main-content').style('flex: 1; padding: 2rem; overflow-y: auto;'):
        # Welcome header
        ui.label(f'Welcome, {admin_type}').style(
            f'font-size: 2.5rem; font-weight: bold; color: {main_color}; margin-bottom: 0.5rem;'
        )
        ui.label(f'Managing: {entity_name}').style(
            'font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem;'
        )
        
        # Stats cards
        with ui.row().style('width: 100%; gap: 1rem; margin-bottom: 2rem;'):
            # Criterias card
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('📊').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(total_criterias)).style('font-size: 2rem; font-weight: bold; color: var(--primary-color);')
                ui.label('Criterias to Fill').style('color: var(--text-secondary);')
                
                if total_criterias > 0:
                    ui.button('View Criterias', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/criterias')).style(
                        f'background: {main_color}; color: white; padding: 0.5rem 1rem; border-radius: 6px; border: none; margin-top: 1rem; font-size: 0.9rem;'
                    )
            
            # Extended Profiles card
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('👤').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(total_profiles)).style('font-size: 2rem; font-weight: bold; color: var(--success-color);')
                ui.label('Extended Profiles').style('color: var(--text-secondary);')
                
                if total_profiles > 0:
                    ui.button('View Profiles', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/profiles')).style(
                        f'background: var(--success-color); color: white; padding: 0.5rem 1rem; border-radius: 6px; border: none; margin-top: 1rem; font-size: 0.9rem;'
                    )
            
            # Pending Submissions card
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('⏳').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(pending_submissions)).style('font-size: 2rem; font-weight: bold; color: var(--warning-color);')
                ui.label('Draft Submissions').style('color: var(--text-secondary);')
                
                if pending_submissions > 0:
                    ui.button('View Drafts', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/submissions?status=draft')).style(
                        'background: var(--warning-color); color: white; padding: 0.5rem 1rem; border-radius: 6px; border: none; margin-top: 1rem; font-size: 0.9rem;'
                    )
            
            # Completed Submissions card
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('✅').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(completed_submissions)).style('font-size: 2rem; font-weight: bold; color: var(--info-color);')
                ui.label('Completed').style('color: var(--text-secondary);')
                
                if completed_submissions > 0:
                    ui.button('View Completed', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/submissions?status=submitted')).style(
                        'background: var(--info-color); color: white; padding: 0.5rem 1rem; border-radius: 6px; border: none; margin-top: 1rem; font-size: 0.9rem;'
                    )
        
        # Quick Actions
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 2rem; margin-bottom: 2rem;'):
            ui.label('🚀 Quick Actions').style(
                f'font-size: 1.5rem; font-weight: bold; color: {main_color}; margin-bottom: 1.5rem;'
            )
            
            with ui.row().style('gap: 1rem; flex-wrap: wrap;'):
                # Fill Criteria button
                if total_criterias > 0:
                    ui.button('📋 Fill Criteria', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/criterias')).style(
                        f'background: {main_color}; color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 600; font-size: 1.1rem;'
                    )
                
                # Fill Extended Profile button
                if total_profiles > 0:
                    ui.button('👤 Fill Extended Profile', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/profiles')).style(
                        'background: var(--success-color); color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 600; font-size: 1.1rem;'
                    )
                
                # View Submissions button
                ui.button('📊 View My Submissions', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/submissions')).style(
                    'background: var(--info-color); color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 600; font-size: 1.1rem;'
                )
        
        # Recent Activity
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 2rem;'):
            ui.label('📈 Recent Activity').style(
                f'font-size: 1.5rem; font-weight: bold; color: {main_color}; margin-bottom: 1.5rem;'
            )
            
            # Get recent submissions
            recent_submissions = list(criteria_submissions_col.find({
                **entity_filter
            }).sort('submitted_at', -1).limit(5))
            
            if recent_submissions:
                for submission in recent_submissions:
                    with ui.row().style('align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border);'):
                        # Status icon
                        status_icon = '⏳' if submission.get('status') == 'draft' else '✅'
                        status_color = 'var(--warning-color)' if submission.get('status') == 'draft' else 'var(--success-color)'
                        ui.label(status_icon).style(f'color: {status_color}; margin-right: 1rem; font-size: 1.2rem;')
                        
                        # Submission details
                        with ui.column().style('flex: 1;'):
                            ui.label(f"Status: {submission.get('status', 'Unknown').title()}").style('font-weight: 600; color: var(--text-primary);')
                            if submission.get('submitted_at'):
                                ui.label(f"Submitted: {submission['submitted_at'].strftime('%Y-%m-%d %H:%M')}").style('font-size: 0.9rem; color: var(--text-secondary);')
                        
                        # Action button
                        ui.button('View Details', on_click=lambda s=submission: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/submissions/{str(s["_id"])}')).style(
                            'background: var(--primary-color); color: white; padding: 0.5rem 1rem; border-radius: 6px; border: none; font-size: 0.9rem;'
                        )
            else:
                ui.label('No recent activity').style('color: var(--text-secondary); font-style: italic; text-align: center; padding: 2rem;')
