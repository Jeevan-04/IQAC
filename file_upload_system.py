"""
Comprehensive File Upload and Data Table System for IQAC Management

This system implements:
1. File upload (Excel/CSV) with validation
2. Automatic data parsing and extraction
3. Dynamic table creation with headers
4. Editable input fields for each cell
5. Data validation and error handling
6. Save as Draft and Submit functionality
7. Manual data entry for missing/incomplete data
"""

import pandas as pd
import csv
import io
from typing import List, Dict, Any
import traceback

class FileUploadSystem:
    """Handles file upload, parsing, and data table management"""
    
    def __init__(self, headers: List[str]):
        self.headers = headers
        self.data_rows = []
        self.parsed_data = []
        
    def parse_file(self, file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        Parse uploaded file and extract data
        
        Args:
            file_content: Raw file content as bytes
            file_name: Name of the uploaded file
            
        Returns:
            Dict containing parsed data and status
        """
        try:
            if file_name.endswith('.csv'):
                return self._parse_csv(file_content)
            elif file_name.endswith(('.xlsx', '.xls')):
                return self._parse_excel(file_content)
            else:
                return {
                    'success': False,
                    'error': 'Unsupported file format. Please use .csv, .xlsx, or .xls files.',
                    'data': []
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error parsing file: {str(e)}',
                'data': []
            }
    
    def _parse_csv(self, file_content: bytes) -> Dict[str, Any]:
        """Parse CSV file content"""
        try:
            # Decode CSV content
            csv_content = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Extract data rows
            data_rows = []
            for row in csv_reader:
                # Ensure all headers are present, fill missing ones with empty string
                clean_row = {}
                for header in self.headers:
                    clean_row[header] = row.get(header, '')
                data_rows.append(clean_row)
            
            return {
                'success': True,
                'data': data_rows,
                'message': f'Successfully parsed {len(data_rows)} rows from CSV'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'CSV parsing error: {str(e)}',
                'data': []
            }
    
    def _parse_excel(self, file_content: bytes) -> Dict[str, Any]:
        """Parse Excel file content"""
        try:
            # Read Excel content
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Convert to list of dictionaries
            data_rows = []
            for _, row in df.iterrows():
                clean_row = {}
                for header in self.headers:
                    # Try to get value from row, fallback to empty string
                    value = row.get(header, '')
                    if pd.isna(value):
                        value = ''
                    clean_row[header] = str(value)
                data_rows.append(clean_row)
            
            return {
                'success': True,
                'data': data_rows,
                'message': f'Successfully parsed {len(data_rows)} rows from Excel'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Excel parsing error: {str(e)}',
                'data': []
            }
    
    def validate_data(self, data_rows: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validate parsed data for completeness and relevance
        
        Args:
            data_rows: List of data rows as dictionaries
            
        Returns:
            Dict containing validation results
        """
        validation_results = {
            'total_rows': len(data_rows),
            'complete_rows': 0,
            'incomplete_rows': 0,
            'empty_rows': 0,
            'issues': []
        }
        
        for i, row in enumerate(data_rows):
            row_num = i + 1
            empty_cells = 0
            total_cells = len(self.headers)
            
            for header in self.headers:
                if not row.get(header, '').strip():
                    empty_cells += 1
            
            if empty_cells == total_cells:
                validation_results['empty_rows'] += 1
                validation_results['issues'].append(f'Row {row_num}: Completely empty row')
            elif empty_cells > 0:
                validation_results['incomplete_rows'] += 1
                validation_results['issues'].append(f'Row {row_num}: {empty_cells}/{total_cells} cells empty')
            else:
                validation_results['complete_rows'] += 1
        
        return validation_results
    
    def collect_data_from_inputs(self, data_rows: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Collect data from input fields after user editing
        
        Args:
            data_rows: List of data rows with input field references
            
        Returns:
            List of collected data as dictionaries
        """
        collected_data = []
        
        for row_data in data_rows:
            row_values = {}
            for header in self.headers:
                input_field = row_data.get(f'input_{header}')
                if input_field and hasattr(input_field, 'value'):
                    row_values[header] = input_field.value
                else:
                    row_values[header] = row_data.get(header, '')
            collected_data.append(row_values)
        
        return collected_data
    
    def save_as_draft(self, data_rows: List[Dict[str, Any]], criteria_id: str, program_id: str) -> Dict[str, Any]:
        """
        Save data as draft
        
        Args:
            data_rows: List of data rows with input field references
            criteria_id: ID of the criteria being filled
            program_id: ID of the program
            
        Returns:
            Dict containing save status
        """
        try:
            # Collect data from input fields
            collected_data = self.collect_data_from_inputs(data_rows)
            
            # Validate collected data
            validation = self.validate_data(collected_data)
            
            # Here you would save to a drafts collection in the database
            # For now, we'll just return success
            draft_data = {
                'criteria_id': criteria_id,
                'program_id': program_id,
                'data': collected_data,
                'validation': validation,
                'status': 'draft',
                'created_at': '2024-01-01T00:00:00Z',  # Would use actual datetime
                'updated_at': '2024-01-01T00:00:00Z'
            }
            
            return {
                'success': True,
                'message': f'Draft saved successfully! {len(collected_data)} rows stored.',
                'draft_data': draft_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error saving draft: {str(e)}'
            }
    
    def submit_data(self, data_rows: List[Dict[str, Any]], criteria_id: str, program_id: str) -> Dict[str, Any]:
        """
        Submit data for final processing
        
        Args:
            data_rows: List of data rows with input field references
            criteria_id: ID of the criteria being filled
            program_id: ID of the program
            
        Returns:
            Dict containing submit status
        """
        try:
            # Collect data from input fields
            collected_data = self.collect_data_from_inputs(data_rows)
            
            # Validate collected data
            validation = self.validate_data(collected_data)
            
            # Check if there are incomplete rows
            if validation['incomplete_rows'] > 0:
                return {
                    'success': False,
                    'warning': f'Found {validation["incomplete_rows"]} incomplete rows. Please fill all required fields before submitting.',
                    'validation': validation
                }
            
            # Here you would save to the main data collection in the database
            # For now, we'll just return success
            submitted_data = {
                'criteria_id': criteria_id,
                'program_id': program_id,
                'data': collected_data,
                'validation': validation,
                'status': 'submitted',
                'submitted_at': '2024-01-01T00:00:00Z',  # Would use actual datetime
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }
            
            return {
                'success': True,
                'message': f'Data submitted successfully! {len(collected_data)} rows processed.',
                'submitted_data': submitted_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error submitting data: {str(e)}'
            }

# Example usage in NiceGUI
def create_file_upload_interface(headers: List[str], criteria_id: str, program_id: str):
    """
    Create the complete file upload interface in NiceGUI
    
    This function demonstrates how to integrate the FileUploadSystem with NiceGUI
    """
    import nicegui.ui as ui
    
    # Initialize the file upload system
    upload_system = FileUploadSystem(headers)
    
    def handle_file_upload(e):
        """Handle file upload and create data table"""
        try:
            # Parse the uploaded file
            result = upload_system.parse_file(e.content, e.name)
            
            if not result['success']:
                ui.notify(result['error'], color='negative')
                return
            
            # Get parsed data
            data_rows = result['data']
            
            # Validate the data
            validation = upload_system.validate_data(data_rows)
            
            # Show data table
            data_table_container.style('display: block;')
            
            with data_table_container:
                ui.label('📊 Data Table').style(
                    'font-size: 1.5rem; font-weight: bold; color: rgb(154, 44, 84); margin-bottom: 1rem;'
                )
                
                ui.label(f'Parsed {len(data_rows)} rows from {e.name}').style(
                    'color: var(--text-secondary); margin-bottom: 0.5rem;'
                )
                
                # Show validation summary
                if validation['incomplete_rows'] > 0:
                    ui.label(f'⚠️ {validation["incomplete_rows"]} rows have incomplete data. Please fill empty cells manually.').style(
                        'color: var(--warning-color); margin-bottom: 1rem; padding: 0.5rem; background: #fff3cd; border-radius: 6px;'
                    )
                
                # Create editable data table
                if data_rows:
                    # Create a grid of input fields for each row
                    for row_index, row_data in enumerate(data_rows):
                        with ui.card().style('background: white; border: 1px solid #e9ecef; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;'):
                            ui.label(f'Row {row_index + 1}').style(
                                'font-weight: bold; color: var(--text-primary); margin-bottom: 0.5rem;'
                            )
                            
                            # Create input fields for each header
                            with ui.row().style('flex-wrap: wrap; gap: 1rem;'):
                                for header in headers:
                                    with ui.column().style('min-width: 200px;'):
                                        ui.label(header).style(
                                            'font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.25rem;'
                                        )
                                        
                                        # Check if cell is empty
                                        cell_value = row_data.get(header, '')
                                        is_empty = not cell_value.strip()
                                        
                                        input_field = ui.input(
                                            label='',
                                            value=cell_value,
                                            placeholder=f'Enter {header}'
                                        ).style(f'width: 100%; border: {"2px solid #dc3545" if is_empty else "1px solid #e9ecef"};')
                                        
                                        # Store reference to input field for later data collection
                                        row_data[f'input_{header}'] = input_field
                    
                    # Action buttons
                    with ui.row().style('gap: 1rem; margin-top: 1.5rem; justify-content: center;'):
                        ui.button('💾 Save as Draft', on_click=lambda: save_as_draft(data_rows)).style(
                            'background: #6c757d; color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                        )
                        ui.button('✅ Submit', on_click=lambda: submit_data(data_rows)).style(
                            'background: rgb(154, 44, 84); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; border: none; font-weight: 600;'
                        )
                else:
                    ui.label('No data found in the file. Please check the file format and headers.').style(
                        'color: var(--warning-color); text-align: center; padding: 2rem;'
                    )
            
            ui.notify(f'File "{e.name}" parsed successfully! {len(data_rows)} rows loaded. Please review and edit the data.', color='positive')
            
        except Exception as e:
            ui.notify(f'Error processing file: {str(e)}', color='negative')
            traceback.print_exc()
    
    def save_as_draft(data_rows):
        """Save data as draft"""
        result = upload_system.save_as_draft(data_rows, criteria_id, program_id)
        if result['success']:
            ui.notify(result['message'], color='positive')
        else:
            ui.notify(result['error'], color='negative')
    
    def submit_data(data_rows):
        """Submit data for final processing"""
        result = upload_system.submit_data(data_rows, criteria_id, program_id)
        if result['success']:
            ui.notify(result['message'], color='positive')
        elif 'warning' in result:
            ui.notify(result['warning'], color='warning')
        else:
            ui.notify(result['error'], color='negative')
    
    # Create the UI components
    with ui.card().style('background: white; border: 2px dashed #e9ecef; padding: 2rem; margin-bottom: 2rem; border-radius: 10px; text-align: center;'):
        ui.label('📤 Upload Spreadsheet').style(
            'font-size: 1.3rem; font-weight: bold; color: rgb(154, 44, 84); margin-bottom: 1rem;'
        )
        ui.label('Upload your Excel/CSV file with data matching the headers above').style(
            'color: var(--text-secondary); margin-bottom: 1.5rem;'
        )
        
        # File upload component
        file_upload = ui.upload(
            label='Choose File',
            on_upload=handle_file_upload
        ).style('background: rgb(154, 44, 84); color: white; padding: 1rem; border-radius: 8px; border: none;')
        
        ui.label('Supported formats: .xlsx, .xls, .csv').style(
            'font-size: 0.9rem; color: var(--text-secondary); margin-top: 1rem;'
        )
    
    # Data table container (initially hidden)
    data_table_container = ui.column().style('display: none;')
    
    return data_table_container

# Example of how to use this in your main application
if __name__ == "__main__":
    # Example headers
    example_headers = ['Student Name', 'Roll Number', 'Subject', 'Marks', 'Grade']
    
    # Example usage
    print("File Upload System initialized with headers:", example_headers)
    print("This system provides:")
    print("1. File upload and parsing (CSV/Excel)")
    print("2. Data validation and completeness checking")
    print("3. Dynamic table creation with editable cells")
    print("4. Save as Draft functionality")
    print("5. Submit data functionality")
    print("6. Error handling and user feedback")
