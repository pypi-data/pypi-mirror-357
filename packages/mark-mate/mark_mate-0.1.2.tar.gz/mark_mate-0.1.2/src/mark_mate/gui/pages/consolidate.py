"""
Consolidate page for MarkMate GUI.
"""

import flet as ft


def create_consolidate_page():
    """Create consolidate page UI."""
    return ft.Container(
        content=ft.Column([
            # Page title
            ft.Text(
                "Consolidate Submissions",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Text(
                "Organize and extract student submission files",
                size=14,
                color=ft.Colors.GREY_600,
            ),
            
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Coming soon placeholder
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
                        "This page will provide a user-friendly interface for consolidating student submissions.",
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "For now, please use the CLI command: mark-mate consolidate",
                        size=12,
                        color=ft.Colors.GREY_500,
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