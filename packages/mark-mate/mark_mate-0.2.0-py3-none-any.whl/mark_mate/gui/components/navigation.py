"""
Navigation sidebar component for MarkMate GUI.
"""

import flet as ft
from typing import Callable


def create_navigation_sidebar(on_page_change: Callable[[str], None], selected_page: str = "consolidate"):
    """Create navigation sidebar with command buttons."""
    
    # Navigation items with icons and descriptions
    nav_items = [
        {
            "id": "consolidate",
            "title": "Consolidate",
            "icon": ft.Icons.FOLDER_OPEN,
            "description": "Organize submissions",
        },
        {
            "id": "scan",
            "title": "Scan",
            "icon": ft.Icons.SEARCH,
            "description": "Find GitHub URLs",
        },
        {
            "id": "extract",
            "title": "Extract",
            "icon": ft.Icons.DESCRIPTION,
            "description": "Process content",
        },
        {
            "id": "grade",
            "title": "Grade",
            "icon": ft.Icons.GRADING,
            "description": "AI-powered grading",
        },
        {
            "id": "config",
            "title": "Configuration",
            "icon": ft.Icons.SETTINGS,
            "description": "Generate configs",
        },
    ]
    
    nav_buttons = []
    
    for item in nav_items:
        is_selected = item["id"] == selected_page
        
        button = ft.Container(
            content=ft.Row([
                ft.Icon(
                    item["icon"],
                    color=ft.Colors.WHITE if is_selected else ft.Colors.BLUE_700,
                    size=20,
                ),
                ft.Column([
                    ft.Text(
                        item["title"],
                        size=14,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        color=ft.Colors.WHITE if is_selected else ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        item["description"],
                        size=10,
                        color=ft.Colors.WHITE70 if is_selected else ft.Colors.GREY_600,
                    ),
                ], spacing=2),
            ], spacing=10),
            padding=ft.padding.all(10),
            margin=ft.margin.only(bottom=5),
            bgcolor=ft.Colors.BLUE_700 if is_selected else ft.Colors.TRANSPARENT,
            border_radius=8,
            on_click=lambda e, page_id=item["id"]: on_page_change(page_id),
            ink=True,
        )
        
        nav_buttons.append(button)
    
    return ft.Column([
        # Logo/branding area
        ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.SCHOOL,
                    color=ft.Colors.BLUE_700,
                    size=32,
                ),
                ft.Text(
                    "MarkMate",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
        ),
        
        ft.Divider(color=ft.Colors.GREY_300),
        
        # Navigation buttons
        ft.Container(
            content=ft.Column(nav_buttons, spacing=0),
            padding=ft.padding.all(10),
        ),
        
        # Workflow indicator (future enhancement)
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "Workflow Progress",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_600,
                ),
                ft.ProgressBar(
                    value=0.0,
                    bgcolor=ft.Colors.GREY_200,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(
                    "0 of 4 steps completed",
                    size=10,
                    color=ft.Colors.GREY_500,
                ),
            ], spacing=5),
            padding=ft.padding.all(10),
            margin=ft.margin.only(top=20),
        ),
        
    ], spacing=0)