from pymongo import MongoClient
from bson import ObjectId
import datetime
import hashlib
import secrets
import re
from nicegui import app, ui
import urllib.parse
import pandas as pd
import io
import base64

# MongoDB Setup
client = MongoClient('mongodb://localhost:27017/')
db = client['iqac_portal']

# Collections
institutions_col = db['institutions']
users_col = db['users']
academic_years_col = db['academic_years']
schools_col = db['schools']
programs_col = db['programs']
criterias_col = db['criterias']
audit_logs_col = db['audit_logs']
extended_profiles_col = db['extended_profiles']

# Global session management
current_user = None

# Beautiful Global Styles with Theme Support
def add_beautiful_global_styles():
    """Add comprehensive styling with theme color support"""
    ui.add_head_html("""
    <style>
        :root {
            --primary-color: #667eea;
            --primary-dark: #5a6fd8;
            --primary-light: #e3f2fd;
            --success-color: #4caf50;
            --warning-color: #ff9800;
            --error-color: #f44336;
            --info-color: #2196f3;
            --text-primary: #2c3e50;
            --text-secondary: #546e7a;
            --background: #fafafa;
            --surface: #ffffff;
            --border: #e0e0e0;
            --shadow: 0 2px 8px rgba(0,0,0,0.12);
            --shadow-hover: 0 4px 16px rgba(0,0,0,0.16);
            --border-radius: 8px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--background);
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        /* Beautiful Cards */
        .beautiful-card {
            background: var(--surface);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            transition: var(--transition);
            overflow: hidden;
        }
        
        .beautiful-card:hover {
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }
        
        /* Themed Buttons */
        .btn-primary {
            background: var(--primary-color);
            color: white;
            border: 2px solid var(--primary-color);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
            border-color: var(--primary-dark);
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: transparent;
            color: var(--primary-color);
            border: 2px solid var(--primary-color);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .btn-secondary:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
        }
        
        .btn-success {
            background: var(--success-color);
            color: white;
            border: 2px solid var(--success-color);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .btn-warning {
            background: var(--warning-color);
            color: white;
            border: 2px solid var(--warning-color);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .btn-danger {
            background: var(--error-color);
            color: white;
            border: 2px solid var(--error-color);
            border-radius: var(--border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: var(--transition);
            cursor: pointer;
        }
        
        /* Beautiful Inputs */
        .beautiful-input {
            border: 2px solid var(--border);
            border-radius: var(--border-radius);
            padding: 0.75rem;
            transition: var(--transition);
            background: var(--surface);
        }
        
        .beautiful-input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            outline: none;
        }
        
        /* Layout Components */
        .sidebar {
            background: var(--surface);
            border-right: 1px solid var(--border);
            min-height: 100vh;
            padding: 1.5rem;
        }
        
        .main-content {
            background: var(--background);
            min-height: 100vh;
            padding: 2rem;
        }
        
        /* Status Indicators */
        .status-success {
            background: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius);
            font-weight: 500;
        }
        
        .status-warning {
            background: #fff3e0;
            color: #f57c00;
            border: 1px solid #ffcc02;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius);
            font-weight: 500;
        }
        
        .status-error {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #ef9a9a;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius);
            font-weight: 500;
        }
        
        /* Animations */
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .slide-up {
            animation: slideUp 0.3s ease-out;
        }
        
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
    """)

# Color utility functions
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def lighten_color(color, percent):
    """Lighten a color by a percentage"""
    if color.startswith('rgb'):
        # Extract RGB values from rgb() string
        import re
        nums = re.findall(r'\d+', color)
        if len(nums) >= 3:
            r, g, b = int(nums[0]), int(nums[1]), int(nums[2])
        else:
            r, g, b = 102, 126, 234  # fallback
    else:
        # Assume hex color
        try:
            r, g, b = hex_to_rgb(color)
        except:
            r, g, b = 102, 126, 234  # fallback
    
    # Lighten each component
    r = min(255, int(r + (255 - r) * percent))
    g = min(255, int(g + (255 - g) * percent))
    b = min(255, int(b + (255 - b) * percent))
    
    return f'rgb({r}, {g}, {b})'

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
            r, g, b = hex_to_rgb(color)
        except:
            r, g, b = 102, 126, 234  # fallback
    
    # Darken each component
    r = max(0, int(r * (1 - percent)))
    g = max(0, int(g * (1 - percent)))
    b = max(0, int(b * (1 - percent)))
    
    return f'rgb({r}, {g}, {b})'

def set_theme_colors(primary_color):
    """Set CSS custom properties for theme colors"""
    light_color = lighten_color(primary_color, 0.8)
    dark_color = darken_color(primary_color, 0.1)
    
    ui.add_head_html(f"""
    <style>
        :root {{
            --primary-color: {primary_color};
            --primary-dark: {dark_color};
            --primary-light: {light_color};
        }}
    </style>
    """)

# Helper Functions
def log_audit_action(action, details, user_email=None, institution_id=None, entity_type=None, entity_id=None):
    """Log an audit action"""
    global current_user
    if not user_email and current_user:
        user_email = current_user.get('email', 'Unknown')
    
    audit_log = {
        'timestamp': datetime.datetime.utcnow(),
        'user_email': user_email or 'System',
        'action': action,
        'details': details,
        'ip_address': '127.0.0.1',
        'institution_id': institution_id,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'created_at': datetime.datetime.utcnow()
    }
    audit_logs_col.insert_one(audit_log)

def hash_password(password, salt):
    """Hash a password with salt"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Sidebar for Institution Admin
def institution_admin_sidebar(inst_id, content_func):
    """Create institution admin sidebar with themed styling"""
    global current_user
    if not current_user or not current_user.get('email'):
        ui.notify('Please log in first', color='negative')
        ui.navigate.to('/')
        return
    
    # Initialize app.storage.user if needed
    if not hasattr(app.storage, 'user'):
        app.storage.user = {}
    
    from bson import ObjectId
    inst = institutions_col.find_one({'_id': ObjectId(inst_id)})
    if not inst:
        ui.label('Institution not found').style('font-size: 1.2rem; color: #c00; margin-top: 2rem;')
        return
    
    # Set theme colors
    main_color = inst.get('theme_color', '#667eea')
    set_theme_colors(main_color)
    light_color = lighten_color(main_color, 0.8)
    dark_color = darken_color(main_color, 0.1)
    
    logo_url = inst.get('logo') or 'https://ui-avatars.com/api/?name=' + (inst.get('name') or 'Institution')
    
    with ui.row().style('height: 100vh; width: 100vw; background: var(--background);'):
        # Sidebar
        with ui.column().classes('sidebar').style(f'min-width: 280px; background: var(--surface); border-right: 1px solid var(--border);'):
            # Institution header
            with ui.row().style('align-items: center; margin-bottom: 2rem;'):
                ui.image(logo_url).style('width: 50px; height: 50px; border-radius: 8px; margin-right: 1rem;')
                with ui.column():
                    ui.label(inst.get('name', 'Institution')).style('font-size: 1.1rem; font-weight: bold; color: var(--text-primary);')
                    ui.label('Admin Portal').style('font-size: 0.9rem; color: var(--text-secondary);')
            
            # Navigation menu
            nav_items = [
                ('🏠', 'Dashboard', f'/institution_admin/{inst_id}'),
                ('🏛️', 'Institution Details', f'/institution_admin/{inst_id}/details'),
                ('🏫', 'Schools & Programs', f'/institution_admin/{inst_id}/hierarchy'),
                ('📊', 'Criterias', f'/institution_admin/{inst_id}/criterias'),
                ('📝', 'Extended Profiles', f'/institution_admin/{inst_id}/extended_profiles'),
                ('📈', 'Spreadsheets', f'/institution_admin/{inst_id}/spreadsheets'),
                ('👥', 'Users', f'/institution_admin/{inst_id}/users'),
                ('📅', 'Academic Years', f'/institution_admin/{inst_id}/academic_years'),
                ('📋', 'Audit Logs', f'/institution_admin/{inst_id}/audit_logs'),
            ]
            
            for icon, label, url in nav_items:
                ui.button(f'{icon} {label}', on_click=lambda u=url: ui.navigate.to(u)).style(
                    f'width: 100%; justify-content: flex-start; margin-bottom: 0.5rem; '
                    f'background: transparent; color: var(--text-primary); border: none; '
                    f'padding: 0.75rem 1rem; border-radius: var(--border-radius); '
                    f'transition: var(--transition);'
                ).props('flat')
            
            # Logout button
            def logout():
                global current_user
                current_user = None
                if hasattr(app.storage, 'user'):
                    app.storage.user.clear()
                ui.notify('Logged out successfully', color='positive')
                ui.navigate.to('/')
            
            ui.button('🚪 Logout', on_click=logout).style(
                'width: 100%; margin-top: auto; background: var(--error-color); color: white;'
            )
        
        # Main content area
        with ui.column().style('flex: 1; padding: 2rem; overflow-y: auto;'):
            content_func(inst, main_color)

@ui.page('/institution_admin/{inst_id}')
def institution_admin_dashboard(inst_id: str):
    """Institution admin dashboard"""
    add_beautiful_global_styles()
    
    def content(inst, main_color):
        ui.label('Institution Admin Dashboard').classes('fade-in').style(
            f'font-size: 2rem; font-weight: bold; color: {main_color}; margin-bottom: 2rem;'
        )
        
        # Quick stats cards
        with ui.row().style('width: 100%; gap: 1rem; margin-bottom: 2rem;'):
            # Academic Years count
            years_count = academic_years_col.count_documents({'institution_id': inst_id})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('📅').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(years_count)).style('font-size: 2rem; font-weight: bold; color: var(--primary-color);')
                ui.label('Academic Years').style('color: var(--text-secondary);')
            
            # Schools count
            schools_count = schools_col.count_documents({'institution_id': inst_id})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('🏫').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(schools_count)).style('font-size: 2rem; font-weight: bold; color: var(--success-color);')
                ui.label('Schools').style('color: var(--text-secondary);')
            
            # Programs count
            programs_count = programs_col.count_documents({'institution_id': inst_id})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('🎓').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(programs_count)).style('font-size: 2rem; font-weight: bold; color: var(--info-color);')
                ui.label('Programs').style('color: var(--text-secondary);')
            
            # Criterias count
            criterias_count = criterias_col.count_documents({'institution_id': inst_id})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('📊').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(criterias_count)).style('font-size: 2rem; font-weight: bold; color: var(--warning-color);')
                ui.label('Criterias').style('color: var(--text-secondary);')
        
        # Recent activity
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem;'):
            ui.label('Recent Activity').style('font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;')
            
            recent_logs = list(audit_logs_col.find(
                {'institution_id': inst_id}
            ).sort('timestamp', -1).limit(5))
            
            if recent_logs:
                for log in recent_logs:
                    with ui.row().style('align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--border);'):
                        ui.label('•').style('color: var(--primary-color); margin-right: 0.5rem;')
                        ui.label(log.get('action', 'Unknown Action')).style('font-weight: 500;')
                        ui.label(log.get('details', '')).style('color: var(--text-secondary); margin-left: 1rem;')
                        if log.get('timestamp'):
                            ui.label(log['timestamp'].strftime('%Y-%m-%d %H:%M')).style(
                                'margin-left: auto; color: var(--text-secondary); font-size: 0.9rem;'
                            )
            else:
                ui.label('No recent activity').style('color: var(--text-secondary); font-style: italic;')
    
    institution_admin_sidebar(inst_id, content)

@ui.page('/institution_admin/{inst_id}/criterias')
def institution_admin_criterias(inst_id: str):
    """Enhanced criterias management page"""
    add_beautiful_global_styles()
    
    def content(inst, main_color):
        ui.label('Criterias Management').classes('fade-in').style(
            f'font-size: 2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        
        # Academic year selector
        from nicegui import app
        unlocked_years = list(academic_years_col.find({'institution_id': inst_id, 'is_locked': False}))
        year_options = [y['name'] for y in unlocked_years]
        name_to_id = {y['name']: str(y['_id']) for y in unlocked_years}
        selected_year_id = app.storage.user.get('selected_academic_year_id') if hasattr(app.storage, 'user') else None
        
        def on_year_change(e):
            if hasattr(app.storage, 'user'):
                app.storage.user['selected_academic_year_id'] = name_to_id.get(e.value)
            ui.update()
        
        with ui.row().style('width: 100%; align-items: center; justify-content: flex-end; margin-bottom: 1rem;'):
            if year_options:
                selected_year_name = None
                for name, id_val in name_to_id.items():
                    if id_val == selected_year_id:
                        selected_year_name = name
                        break
                
                ui.select(
                    options=year_options,
                    value=selected_year_name,
                    on_change=on_year_change,
                    label='Academic Year'
                ).style('min-width: 200px;').classes('beautiful-input')
        
        # Create criteria button
        def open_create_dialog():
            if not selected_year_id:
                ui.notify('Select an academic year first', color='negative')
                return
            
            with ui.dialog() as dialog:
                with ui.card().style(
                    'padding: 2rem; min-width: 800px; max-width: 1000px; max-height: 90vh; overflow-y: auto;'
                ).classes('beautiful-card'):
                    ui.label('Create New Criteria').style(
                        f'font-size: 1.8rem; font-weight: bold; color: {main_color}; margin-bottom: 2rem; text-align: center;'
                    )
                    
                    with ui.column().style('width: 100%; gap: 1.5rem;'):
                        # Criteria Type Selection
                        ui.label('Criteria Type').style(
                            f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 0.5rem;'
                        )
                        
                        scope_type = ui.radio(
                            options=['Program-based Criteria', 'Department-based Criteria'],
                            value='Program-based Criteria'
                        ).style('margin-bottom: 1rem;')
                        
                        ui.label('Choose whether this criteria applies to programs or departments.').style(
                            'color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1.5rem;'
                        )
                        
                        # Basic Information
                        ui.label('Basic Information').style(
                            f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 0.5rem;'
                        )
                        
                        criteria_name = ui.input('Criteria Name').classes('beautiful-input').style('width: 100%;')
                        criteria_description = ui.textarea('Description').classes('beautiful-input').style('width: 100%; min-height: 100px;')
                        
                        # Deadline
                        deadline_input = ui.input('Deadline').props('type=date').classes('beautiful-input').style('width: 100%;')
                        
                        # Headers/Fields
                        ui.label('Spreadsheet Headers').style(
                            f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 0.5rem; margin-top: 1rem;'
                        )
                        
                        headers_input = ui.textarea(
                            'Headers (one per line)',
                            placeholder='id\nname\nnumber\nscore\nremarks'
                        ).classes('beautiful-input').style('width: 100%; min-height: 120px;')
                        
                        # Options
                        with ui.row().style('width: 100%; gap: 2rem; margin-top: 1rem;'):
                            needs_docs = ui.checkbox('Needs Supporting Documents', value=True)
                            is_editable = ui.checkbox('Is Editable', value=True)
                        
                        # Create function
                        def create_criteria():
                            global current_user
                            if not criteria_name.value:
                                ui.notify('Criteria name is required', color='negative')
                                return
                            
                            if not headers_input.value:
                                ui.notify('At least one header is required', color='negative')
                                return
                            
                            # Parse headers
                            headers = [h.strip() for h in headers_input.value.split('\n') if h.strip()]
                            
                            # Determine scope type and department_id
                            scope_val = 'program_based' if scope_type.value == 'Program-based Criteria' else 'department_based'
                            dept_id = None  # For now, we'll implement department selection later
                            
                            # Parse deadline
                            deadline_val = None
                            if deadline_input.value:
                                try:
                                    deadline_val = datetime.datetime.strptime(deadline_input.value, '%Y-%m-%d')
                                except:
                                    pass
                            
                            criteria_doc = {
                                'name': criteria_name.value,
                                'description': criteria_description.value,
                                'deadline': deadline_val,
                                'institution_id': inst_id,
                                'academic_cycle_id': selected_year_id,
                                'scope_type': scope_val,
                                'department_id': dept_id,
                                'headers': headers,
                                'needs_supporting_docs': needs_docs.value,
                                'is_editable': is_editable.value,
                                'created_at': datetime.datetime.utcnow(),
                                'updated_at': datetime.datetime.utcnow(),
                                'created_by': current_user.get('email', 'admin') if current_user else 'admin'
                            }
                            
                            try:
                                result = criterias_col.insert_one(criteria_doc)
                                
                                log_audit_action(
                                    action='Created Criteria',
                                    details=f'Criteria "{criteria_name.value}" created with scope: {scope_val}',
                                    institution_id=inst_id,
                                    entity_type='criteria',
                                    entity_id=str(result.inserted_id)
                                )
                                
                                ui.notify(f'Criteria "{criteria_name.value}" created successfully!', color='positive')
                                dialog.close()
                                ui.navigate.to(f'/institution_admin/{inst_id}/criterias')
                            
                            except Exception as e:
                                ui.notify(f'Error creating criteria: {str(e)}', color='negative')
                        
                        # Action buttons
                        with ui.row().style('width: 100%; justify-content: space-between; margin-top: 2rem;'):
                            ui.button('Cancel', on_click=dialog.close).classes('btn-secondary')
                            ui.button('Create Criteria', on_click=create_criteria).classes('btn-primary')
                
                dialog.open()
        
        ui.button('+ Create New Criteria', on_click=open_create_dialog).classes('btn-primary').style('margin-bottom: 2rem;')
        
        # Display existing criterias
        if selected_year_id:
            existing_criterias = list(criterias_col.find({
                'institution_id': inst_id,
                'academic_cycle_id': selected_year_id
            }))
            
            if existing_criterias:
                ui.label(f'Existing Criterias ({len(existing_criterias)} found)').style(
                    f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
                )
                
                for criteria in existing_criterias:
                    with ui.card().classes('beautiful-card').style('width: 100%; margin-bottom: 1rem; padding: 1.5rem;'):
                        with ui.row().style('width: 100%; align-items: center; justify-content: space-between;'):
                            with ui.column().style('flex: 1;'):
                                criteria_name = criteria.get('name', 'Unnamed Criteria')
                                scope_type = criteria.get('scope_type', 'program_based')
                                scope_label = 'Program-based' if scope_type == 'program_based' else 'Department-based'
                                
                                ui.label(f"📊 {criteria_name}").style(
                                    'font-size: 1.2rem; font-weight: bold; color: var(--text-primary); margin-bottom: 0.5rem;'
                                )
                                ui.label(f"Type: {scope_label}").style(
                                    'font-size: 0.9rem; color: var(--primary-color); margin-bottom: 0.3rem;'
                                )
                                
                                headers = criteria.get('headers', [])
                                if headers:
                                    ui.label(f"Headers: {', '.join(headers[:3])}{'...' if len(headers) > 3 else ''}").style(
                                        'font-size: 0.8rem; color: var(--text-secondary);'
                                    )
                                
                                if criteria.get('deadline'):
                                    deadline_str = criteria['deadline'].strftime('%Y-%m-%d')
                                    ui.label(f"Deadline: {deadline_str}").style(
                                        'font-size: 0.8rem; color: var(--warning-color);'
                                    )
                                
                                created_at = criteria.get('created_at')
                                if created_at:
                                    ui.label(f"Created: {created_at.strftime('%Y-%m-%d %H:%M')}").style(
                                        'font-size: 0.8rem; color: var(--text-secondary);'
                                    )
                            
                            with ui.row().style('gap: 0.5rem;'):
                                ui.button(
                                    '📈 View Data',
                                    on_click=lambda c_id=str(criteria['_id']): ui.navigate.to(
                                        f'/institution_admin/{inst_id}/spreadsheets?criteria_id={c_id}'
                                    )
                                ).classes('btn-success')
                                
                                if criteria.get('is_editable', True):
                                    ui.button('✏️ Edit').classes('btn-warning')
                                
                                def delete_criteria(criteria_id=str(criteria['_id']), criteria_name=criteria.get('name', '')):
                                    log_audit_action(
                                        action='Deleted Criteria',
                                        details=f'Criteria "{criteria_name}" deleted',
                                        institution_id=inst_id,
                                        entity_type='criteria',
                                        entity_id=criteria_id
                                    )
                                    criterias_col.delete_one({'_id': ObjectId(criteria_id)})
                                    ui.notify(f'Criteria "{criteria_name}" deleted', color='positive')
                                    ui.navigate.to(f'/institution_admin/{inst_id}/criterias')
                                
                                ui.button('🗑️', on_click=delete_criteria).classes('btn-danger')
            else:
                ui.label('No criterias found for the selected academic year.').style(
                    'color: var(--text-secondary); font-style: italic; margin-top: 2rem;'
                )
        else:
            ui.label('Please select an academic year to view criterias.').style(
                'color: var(--text-secondary); font-style: italic; margin-top: 2rem;'
            )
    
    institution_admin_sidebar(inst_id, content)

@ui.page('/')
def login_page():
    """Enhanced login page with beautiful styling"""
    add_beautiful_global_styles()
    
    global current_user
    
    # Check if already logged in
    if current_user and current_user.get('email'):
        ui.navigate.to('/dashboard')
        return
    
    with ui.column().style(
        'height: 100vh; width: 100vw; align-items: center; justify-content: center; '
        'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
    ):
        with ui.card().classes('beautiful-card fade-in').style(
            'padding: 3rem; min-width: 400px; background: var(--surface); border-radius: 16px; '
            'box-shadow: 0 10px 40px rgba(0,0,0,0.2);'
        ):
            # Logo and title
            ui.label('🎓 IQAC Portal').style(
                'font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 0.5rem; '
                'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                '-webkit-background-clip: text; -webkit-text-fill-color: transparent;'
            )
            ui.label('Institutional Quality Assurance Cell').style(
                'text-align: center; color: var(--text-secondary); margin-bottom: 2rem; font-size: 1rem;'
            )
            
            # Login form
            email_input = ui.input('Email Address').props('type=email').classes('beautiful-input').style('width: 100%; margin-bottom: 1rem;')
            password_input = ui.input('Password').props('type=password').classes('beautiful-input').style('width: 100%; margin-bottom: 1.5rem;')
            
            def do_login():
                global current_user
                
                if not email_input.value or not password_input.value:
                    ui.notify('Please enter both email and password', color='negative')
                    return
                
                email = email_input.value.lower().strip()
                password = password_input.value
                
                try:
                    # Find user by email
                    user = users_col.find_one({'email': email})
                    
                    if user:
                        # Check password
                        salt = user.get('salt', '')
                        stored_hash = user.get('password_hash', '')
                        
                        if salt:
                            # New salted password system
                            computed_hash = hash_password(password, salt)
                            password_valid = computed_hash == stored_hash
                        else:
                            # Legacy password system (fallback)
                            legacy_hash = hashlib.sha256(password.encode()).hexdigest()
                            password_valid = legacy_hash == user.get('password', '')
                        
                        if password_valid:
                            # Set current user
                            current_user = {
                                'user_id': str(user['_id']),
                                'email': user['email'],
                                'role': user.get('role', 'User'),
                                'first_name': user.get('first_name', ''),
                                'last_name': user.get('last_name', ''),
                                'institution_id': user.get('institution_id'),
                                'must_change_password': user.get('must_change_password', False)
                            }
                            
                            # Initialize session storage
                            if not hasattr(app.storage, 'user'):
                                app.storage.user = {}
                            app.storage.user['current_user'] = current_user
                            
                            # Log successful login
                            log_audit_action(
                                action='Successful Login',
                                details=f'User logged in with role: {current_user["role"]}',
                                user_email=email,
                                institution_id=current_user.get('institution_id')
                            )
                            
                            ui.notify(f'Welcome, {user.get("first_name", email)}!', color='positive')
                            
                            # Redirect based on role and password change requirement
                            if current_user.get('must_change_password'):
                                ui.navigate.to('/change_password')
                            elif current_user.get('role') == 'Platform Owner':
                                ui.navigate.to('/dashboard')
                            elif current_user.get('institution_id'):
                                ui.navigate.to(f'/institution_admin/{current_user["institution_id"]}')
                            else:
                                ui.navigate.to('/dashboard')
                        else:
                            ui.notify('Invalid email or password', color='negative')
                            log_audit_action(
                                action='Failed Login',
                                details=f'Invalid password for email: {email}',
                                user_email=email
                            )
                    else:
                        ui.notify('Invalid email or password', color='negative')
                        log_audit_action(
                            action='Failed Login',
                            details=f'User not found: {email}'
                        )
                
                except Exception as e:
                    ui.notify(f'Login error: {str(e)}', color='negative')
                    log_audit_action(
                        action='Login Error',
                        details=f'Login error for {email}: {str(e)}'
                    )
            
            # Login button
            ui.button('Login', on_click=do_login).classes('btn-primary').style('width: 100%; margin-bottom: 1rem;')
            
            # Forgot password link
            ui.label('Forgot your password? Contact your administrator.').style(
                'text-align: center; color: var(--text-secondary); font-size: 0.9rem;'
            )

@ui.page('/dashboard')
def dashboard():
    """Platform owner dashboard"""
    add_beautiful_global_styles()
    
    global current_user
    if not current_user or current_user.get('role') != 'Platform Owner':
        ui.notify('Access denied', color='negative')
        ui.navigate.to('/')
        return
    
    with ui.column().style('min-height: 100vh; background: var(--background); padding: 2rem;'):
        # Header
        with ui.row().style('width: 100%; align-items: center; justify-content: space-between; margin-bottom: 2rem;'):
            ui.label('Platform Dashboard').style(
                'font-size: 2.5rem; font-weight: bold; color: var(--primary-color);'
            )
            
            def logout():
                global current_user
                current_user = None
                if hasattr(app.storage, 'user'):
                    app.storage.user.clear()
                ui.notify('Logged out successfully', color='positive')
                ui.navigate.to('/')
            
            ui.button('Logout', on_click=logout).classes('btn-secondary')
        
        # Stats cards
        with ui.row().style('width: 100%; gap: 1rem; margin-bottom: 2rem;'):
            # Total institutions
            inst_count = institutions_col.count_documents({})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('🏛️').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(inst_count)).style('font-size: 2rem; font-weight: bold; color: var(--primary-color);')
                ui.label('Institutions').style('color: var(--text-secondary);')
            
            # Total users
            users_count = users_col.count_documents({})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('👥').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(users_count)).style('font-size: 2rem; font-weight: bold; color: var(--success-color);')
                ui.label('Users').style('color: var(--text-secondary);')
            
            # Total criterias
            criterias_count = criterias_col.count_documents({})
            with ui.card().classes('beautiful-card slide-up').style('flex: 1; padding: 1.5rem;'):
                ui.label('📊').style('font-size: 2rem; margin-bottom: 0.5rem;')
                ui.label(str(criterias_count)).style('font-size: 2rem; font-weight: bold; color: var(--info-color);')
                ui.label('Criterias').style('color: var(--text-secondary);')
        
        # Actions
        with ui.row().style('width: 100%; gap: 1rem; margin-bottom: 2rem;'):
            def create_institution():
                ui.navigate.to('/create_institution')
            
            ui.button('+ Create New Institution', on_click=create_institution).classes('btn-primary')
        
        # Institutions list
        institutions = list(institutions_col.find())
        
        if institutions:
            ui.label('Institutions').style(
                'font-size: 1.5rem; font-weight: bold; color: var(--text-primary); margin-bottom: 1rem;'
            )
            
            with ui.column().style('width: 100%; gap: 1rem;'):
                for inst in institutions:
                    with ui.card().classes('beautiful-card').style('padding: 1.5rem;'):
                        with ui.row().style('width: 100%; align-items: center; justify-content: space-between;'):
                            with ui.row().style('align-items: center;'):
                                if inst.get('logo'):
                                    ui.image(inst['logo']).style('width: 60px; height: 60px; border-radius: 8px; margin-right: 1rem;')
                                
                                with ui.column():
                                    ui.label(inst.get('name', 'Unnamed Institution')).style(
                                        'font-size: 1.2rem; font-weight: bold; color: var(--text-primary);'
                                    )
                                    if inst.get('website_url'):
                                        ui.label(inst['website_url']).style('color: var(--text-secondary); font-size: 0.9rem;')
                                    if inst.get('city'):
                                        ui.label(f"📍 {inst['city']}, {inst.get('state', '')}").style(
                                            'color: var(--text-secondary); font-size: 0.9rem;'
                                        )
                            
                            ui.button(
                                'Manage',
                                on_click=lambda inst_id=str(inst['_id']): ui.navigate.to(f'/institution_admin/{inst_id}')
                            ).classes('btn-primary')
        else:
            ui.label('No institutions found. Create your first institution to get started.').style(
                'color: var(--text-secondary); font-style: italic; text-align: center; margin-top: 2rem;'
            )

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8081, storage_secret="super-secret-key-2025-change-this")
