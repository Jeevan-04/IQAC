from nicegui import ui
import pandas as pd
import io
import re
from datetime import datetime
from bson import ObjectId

def normalize_header(header):
    """Normalize header for better matching - handles case, spacing, and common variations"""
    if not header:
        return ""
    
    # Convert to string and normalize
    header_str = str(header).strip()
    
    # Remove extra spaces and convert to lowercase
    normalized = re.sub(r'\s+', ' ', header_str.lower())
    
    # Common header variations mapping
    header_variations = {
        'id': ['id', 'i.d', 'i d', 'identity', 'identifier', 'serial no', 'serial number', 's.no', 's no'],
        'name': ['name', 'full name', 'fullname', 'student name', 'faculty name', 'staff name'],
        'description': ['description', 'desc', 'details', 'detail', 'remarks', 'comment', 'comments'],
        'score': ['score', 'marks', 'grade', 'rating', 'points', 'total', 'total score'],
        'email': ['email', 'e-mail', 'email address', 'e mail'],
        'phone': ['phone', 'phone number', 'mobile', 'mobile number', 'contact', 'contact number'],
        'address': ['address', 'location', 'residence', 'permanent address'],
        'date': ['date', 'dob', 'date of birth', 'birth date', 'joining date', 'start date'],
        'status': ['status', 'state', 'condition', 'current status'],
        'category': ['category', 'type', 'classification', 'group', 'division'],
        'quantity': ['quantity', 'qty', 'amount', 'number', 'count', 'total'],
        'percentage': ['percentage', 'percent', '%', 'pct', 'ratio'],
        'year': ['year', 'academic year', 'academic year', 'session', 'period'],
        'semester': ['semester', 'sem', 'term', 'trimester', 'quarter'],
        'department': ['department', 'dept', 'division', 'unit', 'section'],
        'program': ['program', 'course', 'degree', 'curriculum', 'study program'],
        'faculty': ['faculty', 'teacher', 'instructor', 'professor', 'lecturer'],
        'student': ['student', 'learner', 'pupil', 'candidate', 'enrollee']
    }
    
    # Check if normalized header matches any known variations
    for standard, variations in header_variations.items():
        if normalized in variations or any(v in normalized for v in variations):
            return standard
    
    # If no match found, return the normalized version
    return normalized

def smart_header_mapping(file_headers, expected_headers):
    """Intelligently map file headers to expected headers"""
    mapping = {}
    used_expected = set()
    
    # First pass: exact matches
    for file_header in file_headers:
        normalized_file = normalize_header(file_header)
        for expected_header in expected_headers:
            if expected_header not in used_expected:
                normalized_expected = normalize_header(expected_header)
                if normalized_file == normalized_expected:
                    mapping[file_header] = expected_header
                    used_expected.add(expected_header)
                    break
    
    # Second pass: partial matches
    for file_header in file_headers:
        if file_header not in mapping:
            normalized_file = normalize_header(file_header)
            best_match = None
            best_score = 0
            
            for expected_header in expected_headers:
                if expected_header not in used_expected:
                    normalized_expected = normalize_header(expected_header)
                    
                    # Calculate similarity score
                    score = 0
                    if normalized_file in normalized_expected or normalized_expected in normalized_file:
                        score += 0.5
                    if any(word in normalized_file for word in normalized_expected.split()):
                        score += 0.3
                    if any(word in normalized_expected for word in normalized_file.split()):
                        score += 0.3
                    
                    if score > best_score:
                        best_score = score
                        best_match = expected_header
            
            if best_match and best_score > 0.3:
                mapping[file_header] = best_match
                used_expected.add(best_match)
    
    # Third pass: assign remaining expected headers to unused file headers
    unused_file_headers = [h for h in file_headers if h not in mapping]
    unused_expected = [h for h in expected_headers if h not in used_expected]
    
    for i, expected_header in enumerate(unused_expected):
        if i < len(unused_file_headers):
            mapping[unused_file_headers[i]] = expected_header
    
    return mapping

def parse_file_content(file_content, file_name, expected_headers):
    """Parse uploaded file content and return structured data"""
    try:
        if file_name.endswith('.csv'):
            # Parse CSV
            csv_content = file_content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
        elif file_name.endswith(('.xlsx', '.xls')):
            # Parse Excel
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file format: {file_name}")
        
        if df.empty:
            return [], []
        
        # Get file headers
        file_headers = list(df.columns)
        
        # Create smart mapping
        header_mapping = smart_header_mapping(file_headers, expected_headers)
        
        # Transform data using mapping
        transformed_data = []
        for _, row in df.iterrows():
            transformed_row = {}
            for expected_header in expected_headers:
                # Find the corresponding file header
                file_header = None
                for fh, eh in header_mapping.items():
                    if eh == expected_header:
                        file_header = fh
                        break
                
                if file_header and file_header in row:
                    value = row[file_header]
                    # Handle NaN values
                    if pd.isna(value):
                        value = ''
                    transformed_row[expected_header] = str(value)
                else:
                    transformed_row[expected_header] = ''
            
            transformed_data.append(transformed_row)
        
        return transformed_data, list(header_mapping.values())
        
    except Exception as e:
        raise Exception(f"Error parsing file: {str(e)}")

def create_enhanced_fill_criteria_page_v2(criteria_id, program_id=None, department_id=None, user_role=None):
    """Create enhanced fill criteria page with improved UI and header parsing"""
    
    # Get collections
    from main import criterias_col, programs_col, schools_col, institutions_col, criteria_submissions_col, current_user
    
    criteria = criterias_col.find_one({'_id': ObjectId(criteria_id)})
    if not criteria:
        ui.notify('Criteria not found', color='negative')
        return
    
    # Get entity details
    entity_name = "Unknown"
    entity_type = "Unknown"
    if program_id:
        program = programs_col.find_one({'_id': ObjectId(program_id)})
        if program:
            entity_name = program.get('name', 'Unknown Program')
            entity_type = "Program"
    elif department_id:
        dept = schools_col.find_one({'_id': ObjectId(department_id)})
        if dept:
            entity_name = dept.get('name', 'Unknown Department')
            entity_type = "Department"
    
    # Get institution details for theming
    institution = institutions_col.find_one({'_id': ObjectId(criteria['institution_id'])})
    main_color = institution.get('theme_color', 'rgb(154, 44, 84)') if institution else 'rgb(154, 44, 84)'
    
    # State variables
    parsed_data = []
    current_headers = []
    file_uploaded = False
    show_upload_section = True
    show_manual_section = False
    data_entry_mode = 'upload'  # 'upload' or 'manual'
    
    # Page header
    with ui.card().classes('beautiful-card').style('width: 100%; padding: 2rem; margin-bottom: 2rem; text-align: center;'):
        ui.label('📋 Fill Criteria').style(
            f'font-size: 2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        ui.label(f'Criteria: {criteria.get("name", "Unknown")}').style(
            'font-size: 1.5rem; color: var(--text-primary); margin-bottom: 0.5rem;'
        )
        ui.label(f'{entity_type}: {entity_name}').style(
            'font-size: 1.2rem; color: var(--text-secondary);'
        )
    
    # Spreadsheet Headers Reference
    with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem; margin-bottom: 2rem;'):
        ui.label('📋 Spreadsheet Headers (Reference)').style(
            f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        
        headers = criteria.get('headers', [])
        if headers:
            with ui.row().style('flex-wrap: wrap; gap: 0.5rem;'):
                for i, header in enumerate(headers):
                    with ui.card().style('background: #f8f9fa; border: 1px solid #e9ecef; padding: 0.5rem; border-radius: 6px;'):
                        ui.label(f'{i+1}. {header}').style('font-weight: 500; color: var(--text-primary);')
        else:
            ui.label('No headers defined for this criteria.').style('color: var(--text-secondary); font-style: italic;')
    
    # Data Entry Method Selection
    with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem; margin-bottom: 2rem;'):
        ui.label('📥 Choose Data Entry Method').style(
            f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
        )
        
        with ui.row().style('gap: 1rem; align-items: center;'):
            ui.radio('Data Entry Method', ['upload', 'manual'], value='upload').on('change', lambda e: on_entry_method_change(e.value))
            ui.label('Upload Spreadsheet').style('color: var(--text-secondary);')
            ui.label('Manual Data Entry').style('color: var(--text-secondary);')
    
    # Upload Section
    upload_section = ui.column().style('width: 100%;')
    
    with upload_section:
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem; margin-bottom: 1rem;'):
            ui.label('📤 Upload Spreadsheet').style(
                f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
            )
            ui.label('Upload your Excel/CSV file with data matching the headers above').style(
                'color: var(--text-secondary); margin-bottom: 1.5rem;'
            )
            
            # File upload
            ui.upload(
                label='Choose File',
                on_upload=handle_file_upload,
                multiple=False,
                accept='.xlsx,.xls,.csv'
            ).style('width: 100%;')
    
    # Manual Data Entry Section
    manual_section = ui.column().style('width: 100%; display: none;')
    
    with manual_section:
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem; margin-bottom: 1rem;'):
            ui.label('✏️ Manual Data Entry').style(
                f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
            )
            ui.label('Enter data manually in the table below').style(
                'color: var(--text-secondary); margin-bottom: 1.5rem;'
            )
            
            # Add row button
            ui.button('➕ Add New Row', on_click=add_manual_row).style(
                f'background: {main_color}; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
            )
            
            # Manual data table
            manual_data_table = ui.column().style('width: 100%; margin-top: 1rem;')
    
    # Data Table Section (initially hidden)
    data_table_section = ui.column().style('width: 100%; display: none;')
    
    with data_table_section:
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 1.5rem; margin-bottom: 1rem;'):
            ui.label('📊 Data Table').style(
                f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
            )
            
            # Data summary
            data_summary = ui.label('').style('color: var(--text-secondary); margin-bottom: 1rem;')
            
            # Editable data table
            data_table_container = ui.column().style('width: 100%;')
            
            # Action buttons
            with ui.row().style('gap: 1rem; margin-top: 1rem;'):
                ui.button('💾 Save as Draft', on_click=save_as_draft).style(
                    f'background: var(--warning-color); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                )
                ui.button('📤 Submit', on_click=submit_data).style(
                    f'background: var(--success-color); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                )
    
    def on_entry_method_change(method):
        nonlocal data_entry_mode, show_upload_section, show_manual_section
        data_entry_mode = method
        
        if method == 'upload':
            upload_section.style('display: block;')
            manual_section.style('display: none;')
        else:
            upload_section.style('display: none;')
            manual_section.style('display: block;')
            create_manual_data_table()
    
    def handle_file_upload(e):
        nonlocal parsed_data, current_headers, file_uploaded
        
        try:
            file_name = e.name
            file_content = e.content.read()
            
            # Parse the file
            expected_headers = criteria.get('headers', [])
            parsed_data, current_headers = parse_file_content(file_content, file_name, expected_headers)
            
            if parsed_data:
                file_uploaded = True
                ui.notify(f'File "{file_name}" parsed successfully! {len(parsed_data)} rows loaded.', color='positive')
                
                # Show the data table
                show_data_table()
            else:
                ui.notify('No data found in the file.', color='warning')
                
        except Exception as e:
            ui.notify(f'Error processing file: {str(e)}', color='negative')
    
    def create_manual_data_table():
        """Create manual data entry table"""
        manual_data_table.clear()
        
        headers = criteria.get('headers', [])
        if not headers:
            with manual_data_table:
                ui.label('No headers defined for manual entry.').style('color: var(--text-secondary); font-style: italic;')
            return
        
        with manual_data_table:
            # Table header
            with ui.row().style('background: var(--primary-color); color: white; padding: 0.75rem; border-radius: 8px 8px 0 0; font-weight: bold;'):
                ui.label('#').style('min-width: 50px; text-align: center;')
                for header in headers:
                    ui.label(header).style('flex: 1; text-align: center;')
                ui.label('Actions').style('min-width: 100px; text-align: center;')
            
            # Initial empty row
            add_manual_row()
    
    def add_manual_row():
        """Add a new row to manual data entry table"""
        headers = criteria.get('headers', [])
        if not headers:
            return
        
        row_data = {'inputs': {}, 'row_id': len(manual_data_table.children) + 1}
        
        with manual_data_table:
            with ui.row().style('background: white; padding: 0.75rem; border: 1px solid #e9ecef; align-items: center;'):
                # Row number
                ui.label(str(row_data['row_id'])).style('min-width: 50px; text-align: center; font-weight: bold;')
                
                # Input fields for each header
                for header in headers:
                    input_field = ui.input('').style('flex: 1; margin: 0 0.25rem;')
                    row_data['inputs'][header] = input_field
                
                # Delete row button
                ui.button('🗑️', on_click=lambda: delete_manual_row(row_data)).style(
                    'background: var(--error-color); color: white; padding: 0.5rem; border-radius: 4px; border: none; min-width: 40px;'
                )
        
        # Store row data for later processing
        if not hasattr(manual_data_table, 'row_data_list'):
            manual_data_table.row_data_list = []
        manual_data_table.row_data_list.append(row_data)
    
    def delete_manual_row(row_data):
        """Delete a row from manual data entry table"""
        if hasattr(manual_data_table, 'row_data_list'):
            manual_data_table.row_data_list.remove(row_data)
        
        # Remove the row from UI
        row_data['inputs'].clear()
        # Note: In a real implementation, you'd need to properly remove the UI elements
    
    def show_data_table():
        """Display the parsed data in an editable table"""
        if not parsed_data:
            return
        
        # Show data table section
        data_table_section.style('display: block;')
        
        # Update data summary
        data_summary.text = f'Parsed {len(parsed_data)} rows from uploaded file'
        
        # Clear previous table
        data_table_container.clear()
        
        with data_table_container:
            # Create spreadsheet-like table
            with ui.element('div').style('overflow-x: auto; border: 1px solid var(--border); border-radius: 8px;'):
                with ui.element('table').style('width: 100%; border-collapse: collapse; background: white;'):
                    # Header row
                    with ui.element('thead'):
                        with ui.element('tr'):
                            # Row number column
                            with ui.element('th').style('background: #f8f9fa; padding: 12px; text-align: center; border: 1px solid var(--border); font-weight: bold; width: 50px;'):
                                ui.label('#')
                            
                            # Data headers
                            for header in current_headers:
                                with ui.element('th').style(f'background: {main_color}; color: white; padding: 12px; text-align: left; border: 1px solid var(--border); font-weight: bold; min-width: 150px;'):
                                    ui.label(header)
                    
                    # Data rows
                    with ui.element('tbody'):
                        for row_index, row_data in enumerate(parsed_data):
                            with ui.element('tr'):
                                # Row number
                                with ui.element('td').style('background: #f8f9fa; padding: 10px; text-align: center; border: 1px solid var(--border); font-weight: bold;'):
                                    ui.label(str(row_index + 1))
                                
                                # Data cells (editable)
                                for header in current_headers:
                                    cell_value = row_data.get(header, '')
                                    with ui.element('td').style('padding: 5px; border: 1px solid var(--border); background: white;'):
                                        # Use input for editable cells
                                        cell_input = ui.input('').style('width: 100%; border: none; background: transparent; padding: 5px;').props('dense outlined')
                                        cell_input.value = cell_value
                                        cell_input.props('placeholder=Click to edit')
                                        
                                        # Store reference to input field
                                        row_data[f'input_{header}'] = cell_input
    
    def save_as_draft():
        """Save current data as draft"""
        if data_entry_mode == 'upload' and not parsed_data:
            ui.notify('No data to save. Please upload a file first.', color='warning')
            return
        elif data_entry_mode == 'manual' and not hasattr(manual_data_table, 'row_data_list'):
            ui.notify('No data to save. Please add some rows first.', color='warning')
            return
        
        try:
            # Collect data based on mode
            if data_entry_mode == 'upload':
                collected_data = []
                for row_data in parsed_data:
                    row_values = {}
                    for header in current_headers:
                        input_field = row_data.get(f'input_{header}')
                        if input_field and hasattr(input_field, 'value'):
                            row_values[header] = input_field.value
                        else:
                            row_values[header] = row_data.get(header, '')
                    collected_data.append(row_values)
            else:
                # Manual mode
                collected_data = []
                for row_data in manual_data_table.row_data_list:
                    row_values = {}
                    for header, input_field in row_data['inputs'].items():
                        row_values[header] = input_field.value
                    collected_data.append(row_values)
            
            # Save to database
            draft_doc = {
                'criteria_id': ObjectId(criteria_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'institution_id': ObjectId(criteria['institution_id']),
                'academic_year_id': criteria.get('academic_cycle_id'),
                'data': collected_data,
                'status': 'draft',
                'submitted_by': current_user.get('email', 'admin') if current_user else 'admin',
                'submitted_at': datetime.datetime.now(datetime.timezone.utc),
                'entry_mode': data_entry_mode
            }
            
            # Check if draft already exists
            existing_draft = criteria_submissions_col.find_one({
                'criteria_id': ObjectId(criteria_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'submitted_by': current_user.get('email', 'admin') if current_user else 'admin',
                'status': 'draft'
            })
            
            if existing_draft:
                # Update existing draft
                criteria_submissions_col.update_one(
                    {'_id': existing_draft['_id']},
                    {'$set': {
                        'data': collected_data,
                        'updated_at': datetime.datetime.now(datetime.timezone.utc),
                        'entry_mode': data_entry_mode
                    }}
                )
                ui.notify('Draft updated successfully!', color='positive')
            else:
                # Create new draft
                criteria_submissions_col.insert_one(draft_doc)
                ui.notify('Draft saved successfully!', color='positive')
            
        except Exception as e:
            ui.notify(f'Error saving draft: {str(e)}', color='negative')
    
    def submit_data():
        """Submit the data"""
        if data_entry_mode == 'upload' and not parsed_data:
            ui.notify('No data to submit. Please upload a file first.', color='warning')
            return
        elif data_entry_mode == 'manual' and not hasattr(manual_data_table, 'row_data_list'):
            ui.notify('No data to submit. Please add some rows first.', color='warning')
            return
        
        try:
            # Collect data based on mode
            if data_entry_mode == 'upload':
                collected_data = []
                for row_data in parsed_data:
                    row_values = {}
                    for header in current_headers:
                        input_field = row_data.get(f'input_{header}')
                        if input_field and hasattr(input_field, 'value'):
                            row_values[header] = input_field.value
                        else:
                            row_values[header] = row_data.get(header, '')
                    collected_data.append(row_values)
            else:
                # Manual mode
                collected_data = []
                for row_data in manual_data_table.row_data_list:
                    row_values = {}
                    for header, input_field in row_data['inputs'].items():
                        row_values[header] = input_field.value
                    collected_data.append(row_values)
            
            # Check if draft exists and update it, or create new submission
            existing_draft = criteria_submissions_col.find_one({
                'criteria_id': ObjectId(criteria_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'submitted_by': current_user.get('email', 'admin') if current_user else 'admin',
                'status': 'draft'
            })
            
            if existing_draft:
                # Update existing draft to submitted
                criteria_submissions_col.update_one(
                    {'_id': existing_draft['_id']},
                    {'$set': {
                        'data': collected_data,
                        'status': 'submitted',
                        'submitted_at': datetime.datetime.now(datetime.timezone.utc),
                        'entry_mode': data_entry_mode
                    }}
                )
                ui.notify('Data submitted successfully!', color='positive')
            else:
                # Create new submission
                submission_doc = {
                    'criteria_id': ObjectId(criteria_id),
                    'program_id': ObjectId(program_id) if program_id else None,
                    'department_id': ObjectId(department_id) if department_id else None,
                    'institution_id': ObjectId(criteria['institution_id']),
                    'academic_year_id': criteria.get('academic_cycle_id'),
                    'data': collected_data,
                    'status': 'submitted',
                    'submitted_by': current_user.get('email', 'admin') if current_user else 'admin',
                    'submitted_at': datetime.datetime.now(datetime.timezone.utc),
                    'entry_mode': data_entry_mode
                }
                
                criteria_submissions_col.insert_one(submission_doc)
                ui.notify('Data submitted successfully!', color='positive')
            
            # Navigate back to dashboard
            if program_id:
                ui.navigate.to(f'/program_admin/{program_id}')
            elif department_id:
                ui.navigate.to(f'/department_admin/{department_id}')
            
        except Exception as e:
            ui.notify(f'Error submitting data: {str(e)}', color='negative')
    
    # Initialize manual data table if manual mode is selected
    if data_entry_mode == 'manual':
        create_manual_data_table()
