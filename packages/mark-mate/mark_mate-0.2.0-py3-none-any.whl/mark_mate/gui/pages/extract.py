"""
Extract page for MarkMate GUI.
"""

import flet as ft
import asyncio
import os
from typing import Optional, Callable
from ..adapters.cli_adapter import CLIAdapter


def create_extract_page(progress_callback: Optional[Callable] = None):
    """Create extract page UI."""
    
    # State variables
    selected_folder = ft.Ref[ft.Text]()
    output_file = ft.Ref[ft.TextField]()
    github_urls_file = ft.Ref[ft.TextField]()
    wordpress_checkbox = ft.Ref[ft.Checkbox]()
    dry_run_checkbox = ft.Ref[ft.Checkbox]()
    max_students = ft.Ref[ft.TextField]()
    extract_button = ft.Ref[ft.ElevatedButton]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    progress_text = ft.Ref[ft.Text]()
    results_text = ft.Ref[ft.Text]()
    
    cli_adapter = CLIAdapter()
    
    async def pick_folder(e):
        """Handle folder selection."""
        folder_picker = ft.FilePicker(on_result=on_folder_picked)
        e.page.overlay.append(folder_picker)
        e.page.update()
        await folder_picker.get_directory_path(dialog_title="Select Processed Submissions Folder")
    
    def on_folder_picked(e: ft.FilePickerResultEvent):
        """Handle folder picker result."""
        if e.path:
            folder_path = e.path
            selected_folder.current.value = folder_path
            selected_folder.current.update()
            
            # Auto-populate output file
            parent_dir = os.path.dirname(folder_path)
            output_file.current.value = os.path.join(parent_dir, "extracted_content.json")
            output_file.current.update()
            
            # Auto-populate GitHub URLs file if it exists
            github_file = os.path.join(folder_path, "github_urls.txt")
            if os.path.exists(github_file):
                github_urls_file.current.value = github_file
                github_urls_file.current.update()
    
    async def pick_github_file(e):
        """Handle GitHub URLs file selection."""
        file_picker = ft.FilePicker(on_result=on_github_file_picked)
        e.page.overlay.append(file_picker)
        e.page.update()
        await file_picker.pick_files(
            dialog_title="Select GitHub URLs File",
            allow_multiple=False,
            allowed_extensions=["txt"]
        )
    
    def on_github_file_picked(e: ft.FilePickerResultEvent):
        """Handle GitHub file picker result."""
        if e.files:
            github_urls_file.current.value = e.files[0].path
            github_urls_file.current.update()
    
    async def run_extract(e):
        """Execute extract operation."""
        if not selected_folder.current.value:
            show_error("Please select a processed submissions folder first")
            return
        
        if not output_file.current.value:
            show_error("Please specify an output file")
            return
        
        # Disable extract button and show progress
        extract_button.current.disabled = True
        progress_bar.current.visible = True
        progress_text.current.visible = True
        progress_text.current.value = "Starting extraction..."
        extract_button.current.update()
        progress_bar.current.update()
        progress_text.current.update()
        
        try:
            def update_progress(message: str, percent: Optional[float] = None):
                progress_text.current.value = message
                if percent is not None:
                    progress_bar.current.value = percent / 100.0
                progress_text.current.update()
                progress_bar.current.update()
            
            # Parse max_students
            max_students_val = None
            if max_students.current.value and max_students.current.value.strip():
                try:
                    max_students_val = int(max_students.current.value.strip())
                except ValueError:
                    show_error("Max students must be a valid number")
                    return
            
            # Run extract operation
            result = await cli_adapter.extract_async(
                submissions_folder=selected_folder.current.value,
                output=output_file.current.value,
                wordpress=wordpress_checkbox.current.value,
                github_urls=github_urls_file.current.value if github_urls_file.current.value else None,
                dry_run=dry_run_checkbox.current.value,
                max_students=max_students_val,
                progress_callback=update_progress
            )
            
            # Show results
            if result.get("success"):
                results_text.current.value = f"✅ Content extraction completed successfully!\n\n📊 Processing complete:\n• Output file: {output_file.current.value}\n• WordPress mode: {'Enabled' if wordpress_checkbox.current.value else 'Disabled'}\n• GitHub URLs: {'Used' if github_urls_file.current.value else 'Not provided'}\n• Dry run: {'Yes' if dry_run_checkbox.current.value else 'No'}\n\nReady for next step: Grade submissions"
                results_text.current.color = ft.Colors.GREEN_700
            else:
                results_text.current.value = f"❌ Extraction failed: {result.get('error', 'Unknown error')}"
                results_text.current.color = ft.Colors.RED_700
                
        except Exception as ex:
            results_text.current.value = f"❌ Error: {str(ex)}"
            results_text.current.color = ft.Colors.RED_700
        
        finally:
            # Re-enable extract button and hide progress
            extract_button.current.disabled = False
            progress_bar.current.visible = False
            progress_text.current.visible = False
            results_text.current.visible = True
            extract_button.current.update()
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
                "Extract Content",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Text(
                "Process and extract content from student submissions",
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
                        ft.Text("Processed Submissions Folder:", weight=ft.FontWeight.BOLD),
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
                        label="Output JSON file path",
                        hint_text="extracted_content.json",
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # GitHub URLs File
                    ft.Row([
                        ft.Icon(ft.Icons.LINK, color=ft.Colors.PURPLE_600),
                        ft.Text("GitHub URLs File (Optional):", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Row([
                        ft.TextField(
                            ref=github_urls_file,
                            label="GitHub URLs mapping file",
                            hint_text="github_urls.txt",
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=pick_github_file,
                        ),
                    ]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Processing Options
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.ORANGE_600),
                        ft.Text("Processing Options:", weight=ft.FontWeight.BOLD),
                    ]),
                    
                    ft.Column([
                        ft.Checkbox(
                            ref=wordpress_checkbox,
                            label="Enable WordPress-specific processing",
                            value=False,
                        ),
                        ft.Checkbox(
                            ref=dry_run_checkbox,
                            label="Dry run (preview without extraction)",
                            value=False,
                        ),
                    ], spacing=5),
                    
                    # Max Students Limit
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.INDIGO_600),
                        ft.Text("Max Students (Optional):", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=max_students,
                        label="Maximum number of students to process",
                        hint_text="Leave empty for all students",
                        width=200,
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Extract Button
                    ft.ElevatedButton(
                        ref=extract_button,
                        text="Start Extraction",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=run_extract,
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