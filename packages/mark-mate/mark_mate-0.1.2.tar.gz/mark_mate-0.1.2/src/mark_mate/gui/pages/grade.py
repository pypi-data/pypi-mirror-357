"""
Grade page for MarkMate GUI.
"""

import flet as ft


def create_grade_page():
    """Create grade page UI."""
    return ft.Container(
            content=ft.Column([
                ft.Text(
                    "AI-Powered Grading",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(
                    "Grade submissions using Claude, GPT-4o, and Gemini with statistical aggregation",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.CONSTRUCTION,
                            size=64,
                            color=ft.Colors.ORANGE,
                        ),
                        ft.Text(
                            "Coming Soon",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE,
                        ),
                        ft.Text(
                            "This page will provide an interface for configuring and running AI-powered grading.",
                            size=14,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ]),
            expand=True,
        )