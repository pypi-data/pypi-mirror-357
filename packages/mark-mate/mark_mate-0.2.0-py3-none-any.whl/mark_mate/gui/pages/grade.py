"""
Grade page for MarkMate GUI.
"""

import flet as ft
import asyncio
import os
from typing import Optional, Callable
from ..adapters.cli_adapter import CLIAdapter


def create_grade_page(progress_callback: Optional[Callable] = None):
    """Create grade page UI."""
    
    # State variables
    extracted_content_file = ft.Ref[ft.TextField]()
    assignment_spec_file = ft.Ref[ft.TextField]()
    output_file = ft.Ref[ft.TextField]()
    rubric_file = ft.Ref[ft.TextField]()
    config_file = ft.Ref[ft.TextField]()
    max_students = ft.Ref[ft.TextField]()
    dry_run_checkbox = ft.Ref[ft.Checkbox]()
    grade_button = ft.Ref[ft.ElevatedButton]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    progress_text = ft.Ref[ft.Text]()
    results_text = ft.Ref[ft.Text]()
    
    cli_adapter = CLIAdapter()
    
    async def pick_extracted_content(e):
        """Handle extracted content file selection."""
        file_picker = ft.FilePicker(on_result=on_extracted_content_picked)
        e.page.overlay.append(file_picker)
        e.page.update()
        await file_picker.pick_files(
            dialog_title="Select Extracted Content JSON",
            allow_multiple=False,
            allowed_extensions=["json"]
        )
    
    def on_extracted_content_picked(e: ft.FilePickerResultEvent):
        """Handle extracted content file picker result."""
        if e.files:
            file_path = e.files[0].path
            extracted_content_file.current.value = file_path
            extracted_content_file.current.update()
            
            # Auto-populate output file
            parent_dir = os.path.dirname(file_path)
            output_file.current.value = os.path.join(parent_dir, "grading_results.json")
            output_file.current.update()
    
    async def pick_assignment_spec(e):
        """Handle assignment specification file selection."""
        file_picker = ft.FilePicker(on_result=on_assignment_spec_picked)
        e.page.overlay.append(file_picker)
        e.page.update()
        await file_picker.pick_files(
            dialog_title="Select Assignment Specification",
            allow_multiple=False,
            allowed_extensions=["txt", "md", "pdf", "docx"]
        )
    
    def on_assignment_spec_picked(e: ft.FilePickerResultEvent):
        """Handle assignment spec file picker result."""
        if e.files:
            assignment_spec_file.current.value = e.files[0].path
            assignment_spec_file.current.update()
    
    async def pick_rubric_file(e):
        """Handle rubric file selection."""
        file_picker = ft.FilePicker(on_result=on_rubric_picked)
        e.page.overlay.append(file_picker)
        e.page.update()
        await file_picker.pick_files(
            dialog_title="Select Rubric File (Optional)",
            allow_multiple=False,
            allowed_extensions=["txt", "md", "pdf", "docx"]
        )
    
    def on_rubric_picked(e: ft.FilePickerResultEvent):
        """Handle rubric file picker result."""
        if e.files:
            rubric_file.current.value = e.files[0].path
            rubric_file.current.update()
    
    async def pick_config_file(e):
        """Handle config file selection."""
        file_picker = ft.FilePicker(on_result=on_config_picked)
        e.page.overlay.append(file_picker)
        e.page.update()
        await file_picker.pick_files(
            dialog_title="Select Grading Configuration (Optional)",
            allow_multiple=False,
            allowed_extensions=["yaml", "yml"]
        )
    
    def on_config_picked(e: ft.FilePickerResultEvent):
        """Handle config file picker result."""
        if e.files:
            config_file.current.value = e.files[0].path
            config_file.current.update()
    
    async def run_grading(e):
        """Execute grading operation."""
        if not extracted_content_file.current.value:
            show_error("Please select an extracted content JSON file first")
            return
        
        if not assignment_spec_file.current.value:
            show_error("Please select an assignment specification file")
            return
        
        if not output_file.current.value:
            show_error("Please specify an output file")
            return
        
        # Disable grade button and show progress
        grade_button.current.disabled = True
        progress_bar.current.visible = True
        progress_text.current.visible = True
        progress_text.current.value = "Starting AI grading..."
        grade_button.current.update()
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
            
            # Run grading operation
            result = await cli_adapter.grade_async(
                extracted_content=extracted_content_file.current.value,
                assignment_spec=assignment_spec_file.current.value,
                output=output_file.current.value,
                rubric=rubric_file.current.value if rubric_file.current.value else None,
                max_students=max_students_val,
                dry_run=dry_run_checkbox.current.value,
                config=config_file.current.value if config_file.current.value else None,
                progress_callback=update_progress
            )
            
            # Show results
            if result.get("success"):
                results_text.current.value = f"✅ AI grading completed successfully!\n\n📊 Grading complete:\n• Results saved to: {output_file.current.value}\n• Configuration: {'Custom' if config_file.current.value else 'Auto-configured'}\n• Rubric: {'Separate file' if rubric_file.current.value else 'Extracted from assignment'}\n• Dry run: {'Yes' if dry_run_checkbox.current.value else 'No'}\n\nGrading results are ready for review and export!"
                results_text.current.color = ft.Colors.GREEN_700
            else:
                results_text.current.value = f"❌ Grading failed: {result.get('error', 'Unknown error')}"
                results_text.current.color = ft.Colors.RED_700
                
        except Exception as ex:
            results_text.current.value = f"❌ Error: {str(ex)}"
            results_text.current.color = ft.Colors.RED_700
        
        finally:
            # Re-enable grade button and hide progress
            grade_button.current.disabled = False
            progress_bar.current.visible = False
            progress_text.current.visible = False
            results_text.current.visible = True
            grade_button.current.update()
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
            
            # Input Section
            ft.Container(
                content=ft.Column([
                    # Extracted Content File
                    ft.Row([
                        ft.Icon(ft.Icons.DATA_OBJECT, color=ft.Colors.BLUE_600),
                        ft.Text("Extracted Content JSON:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Row([
                        ft.TextField(
                            ref=extracted_content_file,
                            label="Extracted content JSON file",
                            hint_text="extracted_content.json",
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=pick_extracted_content,
                        ),
                    ]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Assignment Specification File
                    ft.Row([
                        ft.Icon(ft.Icons.ASSIGNMENT, color=ft.Colors.GREEN_600),
                        ft.Text("Assignment Specification:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Row([
                        ft.TextField(
                            ref=assignment_spec_file,
                            label="Assignment specification file",
                            hint_text="assignment_spec.txt",
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=pick_assignment_spec,
                        ),
                    ]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Output File
                    ft.Row([
                        ft.Icon(ft.Icons.SAVE, color=ft.Colors.PURPLE_600),
                        ft.Text("Output File:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=output_file,
                        label="Output JSON file path",
                        hint_text="grading_results.json",
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Optional Files Section
                    ft.Text("Optional Files:", weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    
                    # Rubric File
                    ft.Row([
                        ft.Icon(ft.Icons.RULE, color=ft.Colors.ORANGE_600),
                        ft.Text("Separate Rubric File:", weight=ft.FontWeight.W_500),
                    ]),
                    ft.Row([
                        ft.TextField(
                            ref=rubric_file,
                            label="Rubric file (optional)",
                            hint_text="Leave empty to extract from assignment",
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=pick_rubric_file,
                        ),
                    ]),
                    
                    # Config File
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS_APPLICATIONS, color=ft.Colors.INDIGO_600),
                        ft.Text("Grading Configuration:", weight=ft.FontWeight.W_500),
                    ]),
                    ft.Row([
                        ft.TextField(
                            ref=config_file,
                            label="Configuration YAML file (optional)",
                            hint_text="Leave empty for auto-configuration",
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "Browse",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=pick_config_file,
                        ),
                    ]),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Processing Options
                    ft.Row([
                        ft.Icon(ft.Icons.TUNE, color=ft.Colors.TEAL_600),
                        ft.Text("Processing Options:", weight=ft.FontWeight.BOLD),
                    ]),
                    
                    ft.Column([
                        ft.Checkbox(
                            ref=dry_run_checkbox,
                            label="Dry run (preview without API calls)",
                            value=False,
                        ),
                    ], spacing=5),
                    
                    # Max Students Limit
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.PINK_600),
                        ft.Text("Max Students (Optional):", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=max_students,
                        label="Maximum number of students to grade",
                        hint_text="Leave empty for all students",
                        width=200,
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Grade Button
                    ft.ElevatedButton(
                        ref=grade_button,
                        text="Start AI Grading",
                        icon=ft.Icons.PSYCHOLOGY,
                        on_click=run_grading,
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