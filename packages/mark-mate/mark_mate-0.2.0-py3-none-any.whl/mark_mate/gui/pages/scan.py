"""
Scan page for MarkMate GUI.
"""

import flet as ft
import asyncio
import os
from typing import Optional, Callable
from ..adapters.cli_adapter import CLIAdapter
from ..utils.progress import ProgressTracker


def create_scan_page(progress_callback: Optional[Callable] = None):
    """Create scan page UI."""
    
    # State variables
    selected_folder = ft.Ref[ft.Text]()
    output_file = ft.Ref[ft.TextField]()
    encoding_dropdown = ft.Ref[ft.Dropdown]()
    scan_button = ft.Ref[ft.ElevatedButton]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    progress_text = ft.Ref[ft.Text]()
    results_text = ft.Ref[ft.Text]()
    
    cli_adapter = CLIAdapter()
    
    async def pick_folder(e):
        """Handle folder selection."""
        folder_picker = ft.FilePicker(on_result=on_folder_picked)
        e.page.overlay.append(folder_picker)
        e.page.update()
        await folder_picker.get_directory_path(dialog_title="Select Submissions Folder")
    
    def on_folder_picked(e: ft.FilePickerResultEvent):
        """Handle folder picker result."""
        if e.path:
            folder_path = e.path
            selected_folder.current.value = folder_path
            selected_folder.current.update()
            
            # Auto-populate output file
            output_file.current.value = os.path.join(folder_path, "github_urls.txt")
            output_file.current.update()
    
    async def run_scan(e):
        """Execute scan operation."""
        if not selected_folder.current.value:
            show_error("Please select a submissions folder first")
            return
        
        if not output_file.current.value:
            show_error("Please specify an output file")
            return
        
        # Disable scan button and show progress
        scan_button.current.disabled = True
        progress_bar.current.visible = True
        progress_text.current.visible = True
        progress_text.current.value = "Starting scan..."
        scan_button.current.update()
        progress_bar.current.update()
        progress_text.current.update()
        
        try:
            def update_progress(message: str, percent: Optional[float] = None):
                progress_text.current.value = message
                if percent is not None:
                    progress_bar.current.value = percent / 100.0
                progress_text.current.update()
                progress_bar.current.update()
            
            # Run scan operation
            result = await cli_adapter.scan_async(
                submissions_folder=selected_folder.current.value,
                output=output_file.current.value,
                encoding=encoding_dropdown.current.value,
                progress_callback=update_progress
            )
            
            # Show results
            if result.get("success"):
                urls_found = result.get("urls_found", 0)
                students_with_urls = result.get("students_with_urls", 0)
                total_students = result.get("total_students", 0)
                results_text.current.value = f"✅ Scan completed successfully!\n\n📊 Results:\n• Found {urls_found} GitHub URLs\n• {students_with_urls} of {total_students} students have URLs\n• Results saved to: {output_file.current.value}\n\nYou can edit the mapping file to add or correct URLs before extraction."
                results_text.current.color = ft.Colors.GREEN_700
            else:
                results_text.current.value = f"❌ Scan failed: {result.get('error', 'Unknown error')}"
                results_text.current.color = ft.Colors.RED_700
                
        except Exception as ex:
            results_text.current.value = f"❌ Error: {str(ex)}"
            results_text.current.color = ft.Colors.RED_700
        
        finally:
            # Re-enable scan button and hide progress
            scan_button.current.disabled = False
            progress_bar.current.visible = False
            progress_text.current.visible = False
            results_text.current.visible = True
            scan_button.current.update()
            progress_bar.current.update()
            progress_text.current.update()
            results_text.current.update()
    
    def show_error(message: str):
        """Show error message."""
        results_text.current.value = f"❌ {message}"
        results_text.current.color = ft.Colors.RED_700
        results_text.current.visible = True
        results_text.current.update()
    
    return ft.Container(
        content=ft.Column([
            # Header
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
            
            # Input Section
            ft.Container(
                content=ft.Column([
                    # Folder Selection
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color=ft.Colors.BLUE_600),
                        ft.Text("Submissions Folder:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Row([
                        ft.Text(
                            "No folder selected",
                            ref=selected_folder,
                            expand=True,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=pick_folder,
                        ),
                    ]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Output File
                    ft.Row([
                        ft.Icon(ft.Icons.SAVE, color=ft.Colors.GREEN_600),
                        ft.Text("Output File:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=output_file,
                        label="Output file path",
                        hint_text="github_urls.txt",
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Encoding Selection
                    ft.Row([
                        ft.Icon(ft.Icons.TRANSLATE, color=ft.Colors.PURPLE_600),
                        ft.Text("Text Encoding:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Dropdown(
                        ref=encoding_dropdown,
                        label="Encoding",
                        value="utf-8",
                        options=[
                            ft.dropdown.Option("utf-8", "UTF-8 (Default)"),
                            ft.dropdown.Option("utf-16", "UTF-16"),
                            ft.dropdown.Option("cp1252", "Windows-1252"),
                            ft.dropdown.Option("latin-1", "Latin-1"),
                            ft.dropdown.Option("cp1251", "Cyrillic"),
                            ft.dropdown.Option("shift_jis", "Japanese"),
                            ft.dropdown.Option("euc-kr", "Korean"),
                        ],
                        width=200,
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Scan Button
                    ft.ElevatedButton(
                        ref=scan_button,
                        text="Start Scan",
                        icon=ft.Icons.SEARCH,
                        on_click=run_scan,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_700,
                            padding=ft.padding.all(15),
                        ),
                    ),
                    
                    # Progress Indicators
                    ft.ProgressBar(
                        ref=progress_bar,
                        visible=False,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        ref=progress_text,
                        visible=False,
                        color=ft.Colors.BLUE_700,
                    ),
                    
                    # Results
                    ft.Text(
                        ref=results_text,
                        visible=False,
                        size=14,
                    ),
                    
                ], spacing=10),
                padding=ft.padding.all(20),
                bgcolor=ft.Colors.GREY_50,
                border_radius=ft.border_radius.all(10),
            ),
            
        ], spacing=10),
        expand=True,
        padding=ft.padding.all(20),
    )