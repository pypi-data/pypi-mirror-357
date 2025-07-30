#!/usr/bin/env python3
"""
MarkMate GUI Main Application

Cross-platform desktop application for MarkMate using Flet framework.
"""

import asyncio
import logging
from typing import Optional

import flet as ft

from .components.navigation import create_navigation_sidebar
from .components.header import create_header
from .pages.consolidate import create_consolidate_page
from .pages.scan import create_scan_page
from .pages.extract import create_extract_page
from .pages.grade import create_grade_page
from .pages.config import create_config_page

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarkMateApp:
    """Main MarkMate GUI application."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_page = "consolidate"
        
        # Configure page
        self.page.title = "MarkMate - AI Teaching Assistant"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 900
        self.page.window_min_height = 600
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the main application UI."""
        # Create page content container (will be updated when navigation changes)
        self.content_container = ft.Container(
            content=create_consolidate_page(),
            expand=True,
            padding=ft.padding.all(20),
        )
        
        # Main container with navigation and content
        main_container = ft.Container(
            content=ft.Row([
                # Navigation sidebar
                ft.Container(
                    content=create_navigation_sidebar(self.on_page_change, self.current_page),
                    width=250,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    padding=ft.padding.all(10),
                ),
                # Main content area
                ft.Container(
                    content=ft.Column([
                        # Header
                        create_header(),
                        ft.Divider(height=1, color=ft.Colors.GREY_300),
                        # Page content
                        self.content_container,
                    ]),
                    expand=True,
                ),
            ]),
            expand=True,
        )
        
        self.page.add(main_container)
    
    def on_page_change(self, page_name: str):
        """Handle navigation page changes."""
        logger.info(f"Navigating to page: {page_name}")
        
        self.current_page = page_name
        
        # Update the content based on selected page
        if page_name == "consolidate":
            self.content_container.content = create_consolidate_page()
        elif page_name == "scan":
            self.content_container.content = create_scan_page()
        elif page_name == "extract":
            self.content_container.content = create_extract_page()
        elif page_name == "grade":
            self.content_container.content = create_grade_page()
        elif page_name == "config":
            self.content_container.content = create_config_page()
        
        # Rebuild the navigation with updated selection
        nav_container = self.page.controls[0].content.controls[0]
        nav_container.content = create_navigation_sidebar(self.on_page_change, self.current_page)
        
        self.page.update()


def main_sync(page: ft.Page):
    """Main function for Flet app."""
    app = MarkMateApp(page)


def main():
    """Main entry point for the GUI application."""
    logger.info("Starting MarkMate GUI application")
    
    try:
        # Run the Flet app
        ft.app(
            target=main_sync,
            name="MarkMate",
        )
    except Exception as e:
        logger.error(f"Failed to start GUI application: {e}")
        raise


if __name__ == "__main__":
    main()