# app/pages/login.py
from nicegui import ui
from app.utils.auth import verify_login

def login_page():
    with ui.column().classes('items-center justify-center min-h-screen'):
        ui.label('IQAC / NAAC Portal').classes('text-3xl font-bold text-center mb-6')

        with ui.card().classes('w-[400px] mx-auto p-8 shadow-lg flex flex-col'):
            ui.label('Login').classes('text-xl font-semibold text-center mb-6 w-full')
            with ui.column().classes('w-full').style('gap: 0'):
                email = ui.input('Email').props('outlined').style('width: 100%; margin-bottom: 1rem;').classes('w-full')
                password = ui.input('Password', password=True).props('outlined').style('width: 100%; margin-bottom: 1rem;').classes('w-full')
                role = ui.select(
                    ['Platform Owner', 'Institution Head', 'School Head', 'Program Head', 'Department Head', 'Validator'],
                    label='Login as'
                ).props('outlined').style('width: 100%; margin-bottom: 1.5rem;').classes('w-full')
                message = ui.label('').classes('text-red-500 mb-2 w-full text-center')
                def attempt_login():
                    success, msg = verify_login(email.value, password.value, role.value)
                    if success:
                        ui.open('/dashboard')
                    else:
                        message.set_text(msg)
                ui.button('Login', on_click=attempt_login).props('color=primary').style('width: 100%; font-weight: 600;').classes('w-full')

        ui.link('Forgot Password?', '/forgot-password').classes('text-blue-600 text-sm mt-4 text-center')
