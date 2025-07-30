"""
Header component for MarkMate GUI.
"""

import flet as ft


def create_header(status_text: str = "Ready"):
    """Create header component showing app title and status."""
    return ft.Container(
        content=ft.Row([
            # App title and subtitle
            ft.Column([
                ft.Text(
                    "MarkMate",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(
                    "Your AI Teaching Assistant for Assignments and Assessment",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ]),
            # Status indicator
            ft.Container(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.CIRCLE,
                        color=ft.Colors.GREEN,
                        size=12,
                    ),
                    ft.Text(
                        status_text,
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                ]),
                alignment=ft.alignment.center_right,
            ),
        ], 
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.WHITE,
    )