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
    
    # Common header variations mapping for extended profiles
    header_variations = {
        'id': ['id', 'i.d', 'i d', 'identity', 'identifier', 'serial no', 'serial number', 's.no', 's no'],
        'name': ['name', 'full name', 'fullname', 'student name', 'faculty name', 'staff name', 'employee name'],
        'description': ['description', 'desc', 'details', 'detail', 'remarks', 'comment', 'comments', 'summary'],
        'email': ['email', 'e-mail', 'email address', 'e mail', 'contact email'],
        'phone': ['phone', 'phone number', 'mobile', 'mobile number', 'contact', 'contact number', 'telephone'],
        'address': ['address', 'location', 'residence', 'permanent address', 'current address', 'home address'],
        'date': ['date', 'dob', 'date of birth', 'birth date', 'joining date', 'start date', 'appointment date'],
        'status': ['status', 'state', 'condition', 'current status', 'employment status', 'academic status'],
        'category': ['category', 'type', 'classification', 'group', 'division', 'level', 'rank'],
        'qualification': ['qualification', 'degree', 'education', 'academic qualification', 'certification'],
        'experience': ['experience', 'work experience', 'years of experience', 'professional experience'],
        'department': ['department', 'dept', 'division', 'unit', 'section', 'school', 'faculty'],
        'program': ['program', 'course', 'degree', 'curriculum', 'study program', 'academic program'],
        'faculty': ['faculty', 'teacher', 'instructor', 'professor', 'lecturer', 'academic staff'],
        'student': ['student', 'learner', 'pupil', 'candidate', 'enrollee', 'academic student'],
        'salary': ['salary', 'pay', 'compensation', 'remuneration', 'wage', 'income'],
        'designation': ['designation', 'title', 'position', 'job title', 'role', 'post'],
        'specialization': ['specialization', 'specialty', 'area of expertise', 'field', 'domain'],
        'publications': ['publications', 'research papers', 'articles', 'books', 'papers published'],
        'projects': ['projects', 'research projects', 'completed projects', 'ongoing projects'],
        'awards': ['awards', 'honors', 'recognition', 'achievements', 'certificates', 'medals']
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

def create_enhanced_fill_profile_page(profile_id, program_id=None, department_id=None, user_role=None):
    """Create enhanced fill profile page with improved UI and header parsing"""
    
    # Get profile details
    from main import extended_profiles_col, programs_col, schools_col, institutions_col, criteria_submissions_col, current_user
    
    profile = extended_profiles_col.find_one({'_id': ObjectId(profile_id)})
    if not profile:
        ui.notify('Extended Profile not found', color='negative')
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
    institution = institutions_col.find_one({'_id': ObjectId(profile['institution_id'])})
    main_color = institution.get('theme_color', 'rgb(154, 44, 84)') if institution else 'rgb(154, 44, 84)'
    
    # State variables
    parsed_data = []
    current_headers = []
    file_uploaded = False
    show_upload_section = True
    show_manual_section = False
    
    def handle_file_upload(e):
        nonlocal parsed_data, current_headers, file_uploaded
        
        try:
            file_name = e.name
            file_content = e.content.read()
            
            # Parse the file
            expected_headers = profile.get('headers', [])
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
    
    def toggle_upload_section(value):
        nonlocal show_upload_section
        show_upload_section = value
        if value:
            upload_section.style('display: block;')
        else:
            upload_section.style('display: none;')
    
    def toggle_manual_section(value):
        nonlocal show_manual_section
        show_manual_section = value
        if value:
            manual_section.style('display: block;')
        else:
            manual_section.style('display: none;')
    
    def show_data_table():
        """Display the parsed data in an editable table"""
        if not parsed_data:
            return
        
        # Clear previous table
        data_table_container.clear()
        
        with data_table_container:
            ui.label('📊 Parsed Data Table').style(
                f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
            )
            
            ui.label(f'Parsed {len(parsed_data)} rows. Edit the data below:').style(
                'color: var(--text-secondary); margin-bottom: 1.5rem;'
            )
            
            # Create editable table
            for row_index, row_data in enumerate(parsed_data):
                with ui.card().style('background: white; border: 1px solid #e9ecef; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;'):
                    ui.label(f'Row {row_index + 1}').style(
                        'font-weight: bold; color: var(--text-primary); margin-bottom: 0.5rem;'
                    )
                    
                    # Create input fields for each header
                    with ui.row().style('flex-wrap: wrap; gap: 1rem;'):
                        for header in current_headers:
                            with ui.column().style('min-width: 200px;'):
                                ui.label(header).style(
                                    'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.25rem;'
                                )
                                
                                # Check if cell is empty and highlight it
                                cell_value = row_data.get(header, '')
                                is_empty = not cell_value.strip()
                                
                                input_field = ui.input(
                                    label='',
                                    value=cell_value,
                                    placeholder=f'Enter {header}'
                                ).style(f'width: 100%; border: {"2px solid #dc3545" if is_empty else "1px solid #e9ecef"};')
                                
                                # Store reference to input field
                                row_data[f'input_{header}'] = input_field
    
    def save_as_draft():
        """Save current data as draft"""
        if not parsed_data:
            ui.notify('No data to save. Please upload a file first.', color='warning')
            return
        
        try:
            # Collect data from input fields
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
            
            # Save to database
            draft_doc = {
                'profile_id': ObjectId(profile_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'institution_id': ObjectId(profile['institution_id']),
                'academic_year_id': profile.get('academic_cycle_id'),
                'data': collected_data,
                'status': 'draft',
                'type': 'extended_profile',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Check if draft already exists
            existing_draft = criteria_submissions_col.find_one({
                'profile_id': ObjectId(profile_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'status': 'draft',
                'type': 'extended_profile'
            })
            
            if existing_draft:
                # Update existing draft
                criteria_submissions_col.update_one(
                    {'_id': existing_draft['_id']},
                    {'$set': {'data': collected_data, 'updated_at': datetime.now()}}
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
        if not parsed_data:
            ui.notify('No data to submit. Please upload a file first.', color='warning')
            return
        
        try:
            # Collect data from input fields
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
            
            # Save to database as submitted
            submission_doc = {
                'profile_id': ObjectId(profile_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'institution_id': ObjectId(profile['institution_id']),
                'academic_year_id': profile.get('academic_cycle_id'),
                'data': collected_data,
                'status': 'submitted',
                'type': 'extended_profile',
                'submitted_at': datetime.now(),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Check if submission already exists
            existing_submission = criteria_submissions_col.find_one({
                'profile_id': ObjectId(profile_id),
                'program_id': ObjectId(program_id) if program_id else None,
                'department_id': ObjectId(department_id) if department_id else None,
                'type': 'extended_profile'
            })
            
            if existing_submission:
                # Update existing submission
                criteria_submissions_col.update_one(
                    {'_id': existing_submission['_id']},
                    {'$set': {
                        'data': collected_data, 
                        'status': 'submitted',
                        'submitted_at': datetime.now(),
                        'updated_at': datetime.now()
                    }}
                )
                ui.notify('Submission updated successfully!', color='positive')
            else:
                # Create new submission
                criteria_submissions_col.insert_one(submission_doc)
                ui.notify('Data submitted successfully!', color='positive')
                
        except Exception as e:
            ui.notify(f'Error submitting data: {str(e)}', color='negative')
    
    def save_manual_draft():
        """Save manual entry as draft"""
        try:
            # Collect data from manual input fields
            collected_data = []
            row_values = {}
            for header in headers:
                input_field = manual_data.get(header)
                if input_field and hasattr(input_field, 'value'):
                    row_values[header] = input_field.value
                else:
                    row_values[header] = ''
            
            if any(row_values.values()):  # Only save if there's some data
                collected_data.append(row_values)
                
                # Save to database as draft
                draft_doc = {
                    'profile_id': ObjectId(profile_id),
                    'program_id': ObjectId(program_id) if program_id else None,
                    'department_id': ObjectId(department_id) if department_id else None,
                    'institution_id': ObjectId(profile['institution_id']),
                    'academic_year_id': profile.get('academic_cycle_id'),
                    'data': collected_data,
                    'status': 'draft',
                    'type': 'extended_profile',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                # Check if draft already exists
                existing_draft = criteria_submissions_col.find_one({
                    'profile_id': ObjectId(profile_id),
                    'program_id': ObjectId(program_id) if program_id else None,
                    'department_id': ObjectId(department_id) if department_id else None,
                    'status': 'draft',
                    'type': 'extended_profile'
                })
                
                if existing_draft:
                    # Update existing draft
                    criteria_submissions_col.update_one(
                        {'_id': existing_draft['_id']},
                        {'$set': {'data': collected_data, 'updated_at': datetime.now()}}
                    )
                    ui.notify('Manual entry draft updated successfully!', color='positive')
                else:
                    # Create new draft
                    criteria_submissions_col.insert_one(draft_doc)
                    ui.notify('Manual entry draft saved successfully!', color='positive')
            else:
                ui.notify('Please enter some data before saving.', color='warning')
                
        except Exception as e:
            ui.notify(f'Error saving manual entry draft: {str(e)}', color='negative')
    
    def submit_manual_entry():
        """Submit manual entry"""
        try:
            # Collect data from manual input fields
            collected_data = []
            row_values = {}
            for header in headers:
                input_field = manual_data.get(header)
                if input_field and hasattr(input_field, 'value'):
                    row_values[header] = input_field.value
                else:
                    row_values[header] = ''
            
            if any(row_values.values()):  # Only submit if there's some data
                collected_data.append(row_values)
                
                # Save to database as submitted
                submission_doc = {
                    'profile_id': ObjectId(profile_id),
                    'program_id': ObjectId(program_id) if program_id else None,
                    'department_id': ObjectId(department_id) if department_id else None,
                    'institution_id': ObjectId(profile['institution_id']),
                    'academic_year_id': profile.get('academic_cycle_id'),
                    'data': collected_data,
                    'status': 'submitted',
                    'type': 'extended_profile',
                    'submitted_at': datetime.now(),
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                # Check if submission already exists
                existing_submission = criteria_submissions_col.find_one({
                    'profile_id': ObjectId(profile_id),
                    'program_id': ObjectId(program_id) if program_id else None,
                    'department_id': ObjectId(department_id) if department_id else None,
                    'type': 'extended_profile'
                })
                
                if existing_submission:
                    # Update existing submission
                    criteria_submissions_col.update_one(
                        {'_id': existing_submission['_id']},
                        {'$set': {
                            'data': collected_data, 
                            'status': 'submitted',
                            'submitted_at': datetime.now(),
                            'updated_at': datetime.now()
                        }}
                    )
                    ui.notify('Manual entry submitted successfully!', color='positive')
                else:
                    # Create new submission
                    criteria_submissions_col.insert_one(submission_doc)
                    ui.notify('Manual entry submitted successfully!', color='positive')
            else:
                ui.notify('Please enter some data before submitting.', color='warning')
                
        except Exception as e:
            ui.notify(f'Error submitting manual entry: {str(e)}', color='negative')
    
    # Main UI
    with ui.column().style('width: 100%; max-width: 1200px; margin: 0 auto; padding: 2rem;'):
        # Header
        ui.label(profile.get('name', 'Fill Extended Profile')).style(
            f'font-size: 2.5rem; font-weight: bold; color: {main_color}; margin-bottom: 0.5rem; text-align: center;'
        )
        
        ui.label(f'{entity_type}: {entity_name}').style(
            'font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 2rem; text-align: center;'
        )
        
        # Show deadline if available
        if profile.get('deadline'):
            deadline_str = profile['deadline'].strftime('%Y-%m-%d')
            with ui.card().style('background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; margin-bottom: 2rem; border-radius: 8px;'):
                ui.label('⏰ Deadline').style('font-weight: bold; color: #856404; margin-bottom: 0.5rem;')
                ui.label(f'Submission deadline: {deadline_str}').style('color: #856404;')
        
        # Show headers for reference
        headers = profile.get('headers', [])
        if headers:
            with ui.card().style('background: #f8f9fa; border: 1px solid #e9ecef; padding: 1.5rem; margin-bottom: 2rem; border-radius: 10px;'):
                ui.label('📋 Expected Headers').style(
                    f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
                )
                ui.label('Your uploaded file should contain these columns (case-insensitive matching):').style(
                    'color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.9rem;'
                )
                with ui.row().style('flex-wrap: wrap; gap: 0.5rem;'):
                    for i, header in enumerate(headers):
                        ui.label(header).style(
                            'background: white; color: var(--text-primary); padding: 0.5rem 1rem; border-radius: 6px; border: 1px solid #e9ecef; font-weight: 500; font-size: 0.9rem;'
                        )
        
        # Entry Method Selection
        with ui.card().classes('beautiful-card').style('width: 100%; padding: 2rem; margin-bottom: 2rem;'):
            ui.label('📋 Choose Entry Method').style(
                f'font-size: 1.5rem; font-weight: bold; color: {main_color}; margin-bottom: 1.5rem;'
            )
            
            with ui.row().style('gap: 2rem; align-items: center;'):
                ui.checkbox('📁 File Upload', value=True, on_change=lambda e: toggle_upload_section(e.value)).style('font-size: 1.1rem; font-weight: 600;')
                ui.checkbox('📝 Manual Entry', value=False, on_change=lambda e: toggle_manual_section(e.value)).style('font-size: 1.1rem; font-weight: 600;')
        
        # File Upload Section (conditional)
        upload_section = ui.column().style('width: 100%;')
        with upload_section:
            with ui.card().style('background: white; border: 2px dashed #e9ecef; padding: 2rem; margin-bottom: 2rem; border-radius: 10px; text-align: center;'):
                ui.label('📤 Upload Spreadsheet').style(
                    f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
                )
                ui.label('Upload your Excel/CSV file. Headers will be automatically matched to expected columns.').style(
                    'color: var(--text-secondary); margin-bottom: 1.5rem;'
                )
                
                # File upload component
                file_upload = ui.upload(
                    label='Choose File',
                    on_upload=handle_file_upload,
                    multiple=False,
                    accept='.xlsx,.xls,.csv'
                ).style(f'background: {main_color}; color: white; padding: 1rem; border-radius: 8px; border: none;')
                
                ui.label('Supported formats: .xlsx, .xls, .csv').style(
                    'font-size: 0.9rem; color: var(--text-secondary); margin-top: 1rem;'
                )
                
                # Data Table Section (below upload box)
                if parsed_data:
                    ui.separator().style('margin: 2rem 0; background: var(--border);')
                    
                    ui.label('📊 Parsed Data Table').style(
                        f'font-size: 1.3rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem;'
                    )
                    
                    # Create editable data table
                    show_data_table()
        
        # Manual Data Entry Section (conditional)
        manual_section = ui.column().style('width: 100%; display: none;')
        with manual_section:
            ui.separator().style('margin: 2rem 0; background: #e9ecef;')
            ui.label('📝 Manual Data Entry').style(
                f'font-size: 1.2rem; font-weight: bold; color: {main_color}; margin-bottom: 1rem; text-align: center;'
            )
            
            # Create manual entry form
            manual_data = {}
            with ui.card().style('background: white; border: 2px dashed #e9ecef; padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 8px;'):
                ui.label('Row 1 (Manual Entry)').style(
                    'font-weight: bold; color: var(--text-primary); margin-bottom: 1rem; text-align: center;'
                )
                with ui.row().style('flex-wrap: wrap; gap: 1rem; justify-content: center;'):
                    for header in headers:
                        with ui.column().style('min-width: 200px;'):
                            ui.label(header).style(
                                'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.25rem;'
                            )
                            input_field = ui.input(
                                label='',
                                value='',
                                placeholder=f'Enter {header}'
                            ).style('width: 100%; border: 2px dashed #e9ecef;')
                            manual_data[header] = input_field
            
            # Action buttons for manual entry
            with ui.row().style('gap: 1rem; margin-bottom: 2rem; justify-content: center;'):
                ui.button('💾 Save Manual Entry as Draft', on_click=lambda: save_manual_draft()).style(
                    'background: #6c757d; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                )
                ui.button('✅ Submit Manual Entry', on_click=lambda: submit_manual_entry()).style(
                    f'background: {main_color}; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                )
        
        # Action Buttons for file upload
        with ui.row().style('width: 100%; gap: 1rem; justify-content: center; margin-top: 2rem;'):
            ui.button('💾 Save as Draft', on_click=save_as_draft).style(
                f'background: var(--warning-color); color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 600; font-size: 1.1rem;'
            )
            
            ui.button('📤 Submit', on_click=submit_data).style(
                f'background: {main_color}; color: white; padding: 1rem 2rem; border-radius: 8px; border: none; font-weight: 600; font-size: 1.1rem;'
            )
