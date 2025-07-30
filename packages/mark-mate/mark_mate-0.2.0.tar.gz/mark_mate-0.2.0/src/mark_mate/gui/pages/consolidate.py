"""
Consolidate page for MarkMate GUI.
"""

import flet as ft
import asyncio
import os
from typing import Optional, Callable
from ..adapters.cli_adapter import CLIAdapter


def create_consolidate_page(progress_callback: Optional[Callable] = None):
    """Create consolidate page UI."""
    
    # State variables
    selected_folder = ft.Ref[ft.Text]()
    output_dir = ft.Ref[ft.TextField]()
    no_zip_checkbox = ft.Ref[ft.Checkbox]()
    wordpress_checkbox = ft.Ref[ft.Checkbox]()
    keep_mac_files_checkbox = ft.Ref[ft.Checkbox]()
    consolidate_button = ft.Ref[ft.ElevatedButton]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    progress_text = ft.Ref[ft.Text]()
    results_text = ft.Ref[ft.Text]()
    
    cli_adapter = CLIAdapter()
    
    async def pick_folder(e):
        """Handle folder selection."""
        folder_picker = ft.FilePicker(on_result=on_folder_picked)
        e.page.overlay.append(folder_picker)
        e.page.update()
        await folder_picker.get_directory_path(dialog_title="Select Raw Submissions Folder")
    
    def on_folder_picked(e: ft.FilePickerResultEvent):
        """Handle folder picker result."""
        if e.path:
            folder_path = e.path
            selected_folder.current.value = folder_path
            selected_folder.current.update()
            
            # Auto-populate output directory
            parent_dir = os.path.dirname(folder_path)
            output_dir.current.value = os.path.join(parent_dir, "processed_submissions")
            output_dir.current.update()
    
    async def run_consolidate(e):
        """Execute consolidate operation."""
        if not selected_folder.current.value:
            show_error("Please select a raw submissions folder first")
            return
        
        if not output_dir.current.value:
            show_error("Please specify an output directory")
            return
        
        # Disable consolidate button and show progress
        consolidate_button.current.disabled = True
        progress_bar.current.visible = True
        progress_text.current.visible = True
        progress_text.current.value = "Starting consolidation..."
        consolidate_button.current.update()
        progress_bar.current.update()
        progress_text.current.update()
        
        try:
            def update_progress(message: str, percent: Optional[float] = None):
                progress_text.current.value = message
                if percent is not None:
                    progress_bar.current.value = percent / 100.0
                progress_text.current.update()
                progress_bar.current.update()
            
            # Run consolidate operation
            result = await cli_adapter.consolidate_async(
                folder_path=selected_folder.current.value,
                output_dir=output_dir.current.value,
                no_zip=no_zip_checkbox.current.value,
                wordpress=wordpress_checkbox.current.value,
                keep_mac_files=keep_mac_files_checkbox.current.value,
                progress_callback=update_progress
            )
            
            # Show results
            if result.get("success"):
                results_text.current.value = f"✅ Consolidation completed successfully!\n\n📁 Processing complete:\n• Output directory: {output_dir.current.value}\n• ZIP handling: {'Discarded' if no_zip_checkbox.current.value else 'Extracted'}\n• WordPress mode: {'Enabled' if wordpress_checkbox.current.value else 'Disabled'}\n• Mac files: {'Kept' if keep_mac_files_checkbox.current.value else 'Filtered'}\n\nReady for next step: Scan for GitHub URLs"
                results_text.current.color = ft.Colors.GREEN_700
            else:
                results_text.current.value = f"❌ Consolidation failed: {result.get('error', 'Unknown error')}"
                results_text.current.color = ft.Colors.RED_700
                
        except Exception as ex:
            results_text.current.value = f"❌ Error: {str(ex)}"
            results_text.current.color = ft.Colors.RED_700
        
        finally:
            # Re-enable consolidate button and hide progress
            consolidate_button.current.disabled = False
            progress_bar.current.visible = False
            progress_text.current.visible = False
            results_text.current.visible = True
            consolidate_button.current.update()
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
            
            # Input Section
            ft.Container(
                content=ft.Column([
                    # Folder Selection
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, color=ft.Colors.BLUE_600),
                        ft.Text("Raw Submissions Folder:", weight=ft.FontWeight.BOLD),
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
                    
                    # Output Directory
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER_SPECIAL, color=ft.Colors.GREEN_600),
                        ft.Text("Output Directory:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=output_dir,
                        label="Output directory path",
                        hint_text="processed_submissions",
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Processing Options
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.PURPLE_600),
                        ft.Text("Processing Options:", weight=ft.FontWeight.BOLD),
                    ]),
                    
                    ft.Column([
                        ft.Checkbox(
                            ref=no_zip_checkbox,
                            label="Discard ZIP files instead of extracting",
                            value=False,
                        ),
                        ft.Checkbox(
                            ref=wordpress_checkbox,
                            label="Enable WordPress-specific processing",
                            value=False,
                        ),
                        ft.Checkbox(
                            ref=keep_mac_files_checkbox,
                            label="Keep Mac system files (.DS_Store, etc.)",
                            value=False,
                        ),
                    ], spacing=5),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Consolidate Button
                    ft.ElevatedButton(
                        ref=consolidate_button,
                        text="Start Consolidation",
                        icon=ft.Icons.FOLDER_COPY,
                        on_click=run_consolidate,
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