from nicegui import ui
from bson import ObjectId

def create_admin_sidebar(admin_type, entity_id, institution_id, entity_name, main_color):
    """Create sidebar for program/department admins with institution branding"""
    
    # Get institution details for logo
    from main import institutions_col
    institution = institutions_col.find_one({'_id': ObjectId(institution_id)})
    logo_url = institution.get('logo') or 'https://ui-avatars.com/api/?name=' + (institution.get('name') or 'Institution')
    
    with ui.column().classes('sidebar').style(f'min-width: 280px; background: var(--surface); border-right: 2px solid var(--border); height: 100vh; overflow-y: auto; padding: 0;'):
        # Institution header with logo and entity info
        with ui.card().style(f'background: linear-gradient(135deg, {main_color} 0%, {darken_color(main_color, 0.1)} 100%); color: white; margin: 1rem; padding: 1.5rem; border-radius: 12px; border: none;'):
            # Institution logo above name
            with ui.row().style('align-items: center; margin-bottom: 1rem; justify-content: center;'):
                ui.image(logo_url).style('width: 80px; height: 80px; border-radius: 12px; border: 3px solid rgba(255,255,255,0.3);')
            
            with ui.column().style('text-align: center;'):
                ui.label(institution.get('name', 'Institution')).style('font-size: 1.1rem; font-weight: bold; color: white; margin-bottom: 0.3rem;')
                ui.label(f'{admin_type} Portal').style('font-size: 0.9rem; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;')
                ui.label(entity_name).style('font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.9);')
        
        # Navigation menu with simplified sections
        with ui.column().style('padding: 0 1rem; gap: 1.5rem;'):
            # Dashboard
            with ui.card().style('background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 1rem;'):
                ui.label('🏠 DASHBOARD').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                
                ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/dashboard')).style(
                    f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                    f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                    f'padding: 0.75rem 1rem; border-radius: 8px; '
                    f'transition: all 0.3s ease; font-weight: 500;'
                ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
            
            # Criteria Section
            with ui.card().style('background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 1rem;'):
                ui.label('📊 CRITERIAS').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                
                ui.button('📋 Fill Criteria', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/criterias')).style(
                    f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                    f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                    f'padding: 0.75rem 1rem; border-radius: 8px; '
                    f'transition: all 0.3s ease; font-weight: 500;'
                ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
            
            # Extended Profiles Section
            with ui.card().style('background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 1rem;'):
                ui.label('👤 EXTENDED PROFILES').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                
                ui.button('📝 Fill Extended Profiles', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/profiles')).style(
                    f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                    f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                    f'padding: 0.75rem 1rem; border-radius: 8px; '
                    f'transition: all 0.3s ease; font-weight: 500;'
                ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
            
            # Submissions Section
            with ui.card().style('background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; padding: 1rem;'):
                ui.label('📥 SUBMISSIONS').style('font-size: 0.85rem; font-weight: 700; color: rgb(154, 44, 84); margin-bottom: 1rem; text-align: left; letter-spacing: 1px; text-transform: uppercase;')
                
                ui.button('📊 My Submissions', on_click=lambda: ui.navigate.to(f'/{admin_type.lower().replace(" ", "_")}/{entity_id}/submissions')).style(
                    f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; text-align: left; '
                    f'background: white; color: var(--text-primary); border: 1px solid #e9ecef; '
                    f'padding: 0.75rem 1rem; border-radius: 8px; '
                    f'transition: all 0.3s ease; font-weight: 500;'
                ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "rgb(154, 44, 84)"; event.target.style.color = "white"; event.target.style.borderColor = "rgb(154, 44, 84)";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "white"; event.target.style.color = "var(--text-primary)"; event.target.style.borderColor = "#e9ecef";'))
            
            # Logout button
            ui.separator().style('margin: 1rem 0; background: #e9ecef;')
            ui.button('🚪 Logout', on_click=lambda: ui.navigate.to('/')).style(
                f'width: 100%; justify-content: center; background: #dc3545; color: white; border: 1px solid #dc3545; '
                f'padding: 0.75rem 1rem; border-radius: 8px; transition: all 0.3s ease; font-weight: 600;'
            ).on('mouseenter', lambda e: ui.run_javascript(f'event.target.style.background = "#c82333"; event.target.style.borderColor = "#c82333";')).on('mouseleave', lambda e: ui.run_javascript(f'event.target.style.background = "#dc3545"; event.target.style.borderColor = "#dc3545";'))

def darken_color(color, percent):
    """Darken a color by a percentage"""
    if color.startswith('rgb'):
        import re
        nums = re.findall(r'\d+', color)
        if len(nums) >= 3:
            r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
        else:
            r, g, b = 102, 126, 234  # fallback
    else:
        try:
            # Assume hex color
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        except:
            r, g, b = 102, 126, 234  # fallback
    
    # Darken each component
    r = max(0, int(r * (1 - percent)))
    g = max(0, int(g * (1 - percent)))
    b = max(0, int(b * (1 - percent)))
    
    return f'rgb({r}, {g}, {b})'
