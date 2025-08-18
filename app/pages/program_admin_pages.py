from nicegui import ui
from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient

# Import collections from main.py
from main import programs_col, institutions_col, criterias_col, extended_profiles_col, criteria_submissions_col

def create_program_admin_criterias_page(program_id: str):
    """Program admin criteria management page"""
    from main import add_beautiful_global_styles, check_auth, app
    
    add_beautiful_global_styles()
    
    # Check authentication
    if not check_auth():
        ui.notify('Please log in first', color='negative')
        ui.navigate.to('/')
        return
    
    # Get program details
    program = programs_col.find_one({'_id': ObjectId(program_id)})
    if not program:
        ui.notify('Program not found', color='negative')
        ui.navigate.to('/')
        return
    
    # Get institution details
    institution = institutions_col.find_one({'_id': ObjectId(program['institution_id'])})
    main_color = institution.get('theme_color', 'rgb(154, 44, 84)') if institution else 'rgb(154, 44, 84)'
    
    def content(inst, main_color):
        ui.label('📊 Criteria Management').classes('fade-in').style(
            f'font-size: 2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        ui.label(f'Program: {program.get("name", "Unknown")}').style(
            'font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem;'
        )
        
        # Get criteria for this program
        program_criterias = list(criterias_col.find({
            'institution_id': program['institution_id'],
            'scope_type': 'program_based'
        }))
        
        if program_criterias:
            ui.label(f'Available Criterias ({len(program_criterias)} found)').style(
                f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1.5rem;'
            )
            
            for criteria in program_criterias:
                with ui.card().classes('beautiful-card').style('width: 100%; margin-bottom: 1.5rem; padding: 1.5rem;'):
                    with ui.row().style('width: 100%; align-items: center; justify-content: space-between;'):
                        with ui.column().style('flex: 1;'):
                            ui.label(f"📋 {criteria.get('name', 'Unnamed')}").style(
                                'font-size: 1.3rem; font-weight: bold; color: var(--text-primary); margin-bottom: 0.5rem;'
                            )
                            
                            if criteria.get('description'):
                                ui.label(f"Description: {criteria['description']}").style(
                                    'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;'
                                )
                            
                            # Fix deadline display
                            deadline = criteria.get('deadline')
                            if deadline:
                                try:
                                    if isinstance(deadline, str):
                                        deadline_str = deadline
                                    else:
                                        deadline_str = deadline.strftime('%Y-%m-%d')
                                    ui.label(f"⏰ Deadline: {deadline_str}").style(
                                        'font-size: 0.9rem; color: var(--warning-color); font-weight: bold; margin-bottom: 0.5rem;'
                                    )
                                except:
                                    ui.label("⏰ Deadline: Invalid date format").style(
                                        'font-size: 0.9rem; color: var(--error-color); margin-bottom: 0.5rem;'
                                    )
                            else:
                                ui.label("⏰ Deadline: No deadline set").style(
                                    'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;'
                                )
                            
                            # Check if user has draft for this criteria
                            current_user_email = app.storage.user.get('current_user', {}).get('email', 'Unknown User') if hasattr(app.storage, 'user') else 'Unknown User'
                            existing_draft = criteria_submissions_col.find_one({
                                'criteria_id': criteria['_id'],
                                'program_id': ObjectId(program_id),
                                'submitted_by': current_user_email,
                                'status': 'draft'
                            })
                            
                            if existing_draft:
                                ui.label('📝 You have a draft for this criteria').style(
                                    'font-size: 0.9rem; color: var(--info-color); font-weight: bold; margin-bottom: 0.5rem;'
                                )
                        
                        with ui.row().style('gap: 0.5rem;'):
                            if existing_draft:
                                ui.button('✏️ Edit Draft', on_click=lambda c_id=str(criteria['_id']): ui.navigate.to(f'/program_admin/{program_id}/fill_criteria/{c_id}')).style(
                                    f'background: var(--warning-color); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                                )
                            else:
                                ui.button('📝 Fill Criteria', on_click=lambda c_id=str(criteria['_id']): ui.navigate.to(f'/program_admin/{program_id}/fill_criteria/{c_id}')).style(
                                    f'background: {main_color}; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                                )
        else:
            with ui.card().classes('beautiful-card').style('width: 100%; padding: 3rem; text-align: center;'):
                ui.label('📊 No Criteria Available').style(
                    f'font-size: 1.5rem; color: {main_color}; margin-bottom: 1rem;'
                )
                ui.label('No criteria have been created for this program yet.').style(
                    'color: var(--text-secondary); margin-bottom: 1rem;'
                )
                ui.label('Please contact your institution administrator to create criteria.').style(
                    'color: var(--text-secondary); font-style: italic;'
                )
    
    # Create sidebar
    with ui.row().style('height: 100vh; width: 100vw; background: var(--background);'):
        # Sidebar
        with ui.column().style('width: 280px; background: var(--surface); border-right: 2px solid var(--border); padding: 0; height: 100vh; overflow-y: auto;'):
            # Institution header card
            with ui.card().style('background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)); color: white; padding: 1.5rem; margin: 1rem; border: none; border-radius: 12px; box-shadow: var(--shadow);'):
                ui.element('div').style('width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;').inner_html = '🎓'
                ui.label(institution.get('name', 'Institution')).style('font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem;')
                ui.separator().style('margin: 1rem 0; background: rgba(255,255,255,0.3);')
                current_user_email = app.storage.user.get('current_user', {}).get('email', 'Unknown User') if hasattr(app.storage, 'user') else 'Unknown User'
                ui.label(current_user_email).style('font-size: 0.9rem; text-align: center; opacity: 0.9; margin-bottom: 0.5rem;')
                ui.label('Program Admin').style('font-size: 0.9rem; text-align: center; opacity: 0.8;')
            
            # Navigation menu
            with ui.column().style('padding: 1rem; gap: 0.5rem;'):
                with ui.card().style('background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'):
                    ui.label('📊 OVERVIEW').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                    
                    overview_items = [
                        ('🏠', 'Dashboard', f'/program_admin/{program_id}'),
                        ('📊', 'Criteria Management', f'/program_admin/{program_id}/criterias'),
                        ('👤', 'Extended Profiles', f'/program_admin/{program_id}/profiles'),
                        ('📥', 'My Submissions', f'/program_admin/{program_id}/submissions'),
                    ]
                    
                    for icon, label, url in overview_items:
                        ui.button(f'{icon} {label}', on_click=lambda u=url: ui.navigate.to(u)).style(
                            f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                            f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                            f'padding: 0.75rem 1rem; border-radius: 8px; '
                            f'transition: all 0.3s ease; font-weight: 500;'
                        ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
                    
                    ui.separator().style('margin: 1rem 0; background: #e9ecef;')
                    ui.button('🚪 Logout', on_click=lambda: ui.navigate.to('/')).style(
                        f'width: 100%; justify-content: center; background: #dc3545; color: white; border: 1px solid #dc3545; '
                        f'padding: 0.75rem 1rem; border-radius: 8px; transition: all 0.3s ease; font-weight: 600;'
                    ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "#c82333"; event.target.style.borderColor = "#c82333";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "#dc3545"; event.target.style.borderColor = "#dc3545";'))
        
        # Main content
        with ui.column().style('flex: 1; padding: 2rem; overflow-y: auto;'):
            content(institution, main_color)

def create_program_admin_profiles_page(program_id: str):
    """Program admin extended profiles management page"""
    from main import add_beautiful_global_styles, check_auth, app
    
    add_beautiful_global_styles()
    
    # Check authentication
    if not check_auth():
        ui.notify('Please log in first', color='negative')
        ui.navigate.to('/')
        return
    
    # Get program details
    program = programs_col.find_one({'_id': ObjectId(program_id)})
    if not program:
        ui.notify('Program not found', color='negative')
        ui.navigate.to('/')
        return
    
    # Get institution details
    institution = institutions_col.find_one({'_id': ObjectId(program['institution_id'])})
    main_color = institution.get('theme_color', 'rgb(154, 44, 84)') if institution else 'rgb(154, 44, 84)'
    
    def content(inst, main_color):
        ui.label('👤 Extended Profiles').classes('fade-in').style(
            f'font-size: 2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        ui.label(f'Program: {program.get("name", "Unknown")}').style(
            'font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem;'
        )
        
        # Get extended profiles for this program
        program_profiles = list(extended_profiles_col.find({
            'institution_id': program['institution_id'],
            'scope_type': 'program_based'
        }))
        
        if program_profiles:
            ui.label(f'Available Extended Profiles ({len(program_profiles)} found)').style(
                f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1.5rem;'
            )
            
            for profile in program_profiles:
                with ui.card().classes('beautiful-card').style('width: 100%; margin-bottom: 1.5rem; padding: 1.5rem;'):
                    with ui.row().style('width: 100%; align-items: center; justify-content: space-between;'):
                        with ui.column().style('flex: 1;'):
                            ui.label(f"📄 {profile.get('name', 'Unnamed')}").style(
                                'font-size: 1.3rem; font-weight: bold; color: var(--text-primary); margin-bottom: 0.5rem;'
                            )
                            
                            if profile.get('description'):
                                ui.label(f"Description: {profile['description']}").style(
                                    'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;'
                                )
                            
                            # Check if user has draft for this profile
                            current_user_email = app.storage.user.get('current_user', {}).get('email', 'Unknown User') if hasattr(app.storage, 'user') else 'Unknown User'
                            existing_draft = criteria_submissions_col.find_one({
                                'profile_id': profile['_id'],
                                'program_id': ObjectId(program_id),
                                'submitted_by': current_user_email,
                                'status': 'draft'
                            })
                            
                            if existing_draft:
                                ui.label('📝 You have a draft for this profile').style(
                                    'font-size: 0.9rem; color: var(--info-color); font-weight: bold; margin-bottom: 0.5rem;'
                                )
                        
                        with ui.row().style('gap: 0.5rem;'):
                            if existing_draft:
                                ui.button('✏️ Edit Draft', on_click=lambda p_id=str(profile['_id']): ui.navigate.to(f'/program_admin/{program_id}/fill_profile/{p_id}')).style(
                                    f'background: var(--warning-color); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                                )
                            else:
                                ui.button('📝 Fill Profile', on_click=lambda p_id=str(profile['_id']): ui.navigate.to(f'/program_admin/{program_id}/fill_profile/{p_id}')).style(
                                    f'background: {main_color}; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                                )
        else:
            with ui.card().classes('beautiful-card').style('width: 100%; padding: 3rem; text-align: center;'):
                ui.label('👤 No Extended Profiles Available').style(
                    f'font-size: 1.5rem; color: {main_color}; margin-bottom: 1rem;'
                )
                ui.label('No extended profiles have been created for this program yet.').style(
                    'color: var(--text-secondary); margin-bottom: 1rem;'
                )
                ui.label('Please contact your institution administrator to create extended profiles.').style(
                    'color: var(--text-secondary); font-style: italic;'
                )
    
    # Create sidebar
    with ui.row().style('height: 100vh; width: 100vw; background: var(--background);'):
        # Sidebar
        with ui.column().style('width: 280px; background: var(--surface); border-right: 2px solid var(--border); padding: 0; height: 100vh; overflow-y: auto;'):
            # Institution header card
            with ui.card().style('background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)); color: white; padding: 1.5rem; margin: 1rem; border: none; border-radius: 12px; box-shadow: var(--shadow);'):
                ui.element('div').style('width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 50%; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;').inner_html = '🎓'
                ui.label(institution.get('name', 'Institution')).style('font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem;')
                ui.separator().style('margin: 1rem 0; background: rgba(255,255,255,0.3);')
                current_user_email = app.storage.user.get('current_user', {}).get('email', 'Unknown User') if hasattr(app.storage, 'user') else 'Unknown User'
                ui.label(current_user_email).style('font-size: 0.9rem; text-align: center; opacity: 0.9; margin-bottom: 0.5rem;')
                ui.label('Program Admin').style('font-size: 0.9rem; text-align: center; opacity: 0.8;')
            
            # Navigation menu
            with ui.column().style('padding: 1rem; gap: 0.5rem;'):
                with ui.card().style('background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'):
                    ui.label('📊 OVERVIEW').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                    
                    overview_items = [
                        ('🏠', 'Dashboard', f'/program_admin/{program_id}'),
                        ('📊', 'Criteria Management', f'/program_admin/{program_id}/criterias'),
                        ('👤', 'Extended Profiles', f'/program_admin/{program_id}/profiles'),
                        ('📥', 'My Submissions', f'/program_admin/{program_id}/submissions'),
                    ]
                    
                    for icon, label, url in overview_items:
                        ui.button(f'{icon} {label}', on_click=lambda u=url: ui.navigate.to(u)).style(
                            f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                            f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                            f'padding: 0.75rem 1rem; border-radius: 8px; '
                            f'transition: all 0.3s ease; font-weight: 500;'
                        ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
                    
                    ui.separator().style('margin: 1rem 0; background: #e9ecef;')
                    ui.button('🚪 Logout', on_click=lambda: ui.navigate.to('/')).style(
                        f'width: 100%; justify-content: center; background: #dc3545; color: white; border: 1px solid #dc3545; '
                        f'padding: 0.75rem 1rem; border-radius: 8px; transition: all 0.3s ease; font-weight: 600;'
                    ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "#c82333"; event.target.style.borderColor = "#c82333";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "#dc3545"; event.target.style.borderColor = "#dc3545";'))
        
        # Main content
        with ui.column().style('flex: 1; padding: 2rem; overflow-y: auto;'):
            content(institution, main_color)
