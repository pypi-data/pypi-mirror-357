"""
Scan page for MarkMate GUI.
"""

import flet as ft


def create_scan_page():
    """Create scan page UI."""
    return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Scan for GitHub URLs",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
                ft.Text(
                    "Find and extract GitHub repository URLs from submissions",
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
                            "This page will provide an interface for scanning submissions for GitHub URLs.",
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