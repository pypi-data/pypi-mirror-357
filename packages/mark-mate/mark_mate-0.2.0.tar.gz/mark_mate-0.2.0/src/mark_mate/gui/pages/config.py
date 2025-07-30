"""
Configuration page for MarkMate GUI.
"""

import flet as ft
import asyncio
import os
from typing import Optional, Callable
from ..adapters.cli_adapter import CLIAdapter


def create_config_page(progress_callback: Optional[Callable] = None):
    """Create config page UI."""
    
    # State variables
    template_dropdown = ft.Ref[ft.Dropdown]()
    provider_dropdown = ft.Ref[ft.Dropdown]()
    output_file = ft.Ref[ft.TextField]()
    force_checkbox = ft.Ref[ft.Checkbox]()
    generate_button = ft.Ref[ft.ElevatedButton]()
    progress_bar = ft.Ref[ft.ProgressBar]()
    progress_text = ft.Ref[ft.Text]()
    results_text = ft.Ref[ft.Text]()
    
    cli_adapter = CLIAdapter()
    
    def on_template_change(e):
        """Handle template selection change."""
        if template_dropdown.current.value == "single-provider":
            provider_dropdown.current.visible = True
            provider_dropdown.current.update()
        else:
            provider_dropdown.current.visible = False
            provider_dropdown.current.update()
    
    async def run_generate_config(e):
        """Execute config generation operation."""
        if not output_file.current.value:
            show_error("Please specify an output file")
            return
        
        # Disable generate button and show progress
        generate_button.current.disabled = True
        progress_bar.current.visible = True
        progress_text.current.visible = True
        progress_text.current.value = "Generating configuration..."
        generate_button.current.update()
        progress_bar.current.update()
        progress_text.current.update()
        
        try:
            def update_progress(message: str, percent: Optional[float] = None):
                progress_text.current.value = message
                if percent is not None:
                    progress_bar.current.value = percent / 100.0
                progress_text.current.update()
                progress_bar.current.update()
            
            # Run generate config operation
            result = await cli_adapter.generate_config_async(
                output=output_file.current.value,
                template=template_dropdown.current.value,
                provider=provider_dropdown.current.value if provider_dropdown.current.visible else None,
                force=force_checkbox.current.value,
                progress_callback=update_progress
            )
            
            # Show results
            if result.get("success"):
                results_text.current.value = f"✅ Configuration generated successfully!\n\n📁 Configuration details:\n• Template: {template_dropdown.current.value}\n• Output file: {output_file.current.value}\n• Provider: {provider_dropdown.current.value if provider_dropdown.current.visible else 'Multiple providers'}\n• Force overwrite: {'Yes' if force_checkbox.current.value else 'No'}\n\nYou can now use this configuration file for grading!"
                results_text.current.color = ft.Colors.GREEN_700
            else:
                results_text.current.value = f"❌ Configuration generation failed: {result.get('error', 'Unknown error')}"
                results_text.current.color = ft.Colors.RED_700
                
        except Exception as ex:
            results_text.current.value = f"❌ Error: {str(ex)}"
            results_text.current.color = ft.Colors.RED_700
        
        finally:
            # Re-enable generate button and hide progress
            generate_button.current.disabled = False
            progress_bar.current.visible = False
            progress_text.current.visible = False
            results_text.current.visible = True
            generate_button.current.update()
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
                "Configuration Generator",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE_700,
            ),
            ft.Text(
                "Generate and customize grading configuration templates",
                size=14,
                color=ft.Colors.GREY_600,
            ),
            
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            
            # Configuration Options
            ft.Container(
                content=ft.Column([
                    # Template Selection
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.BLUE_600),
                        ft.Text("Configuration Template:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Dropdown(
                        ref=template_dropdown,
                        label="Template Type",
                        value="full",
                        options=[
                            ft.dropdown.Option("full", "Full - All providers with comprehensive settings"),
                            ft.dropdown.Option("minimal", "Minimal - Simple single-provider setup"),
                            ft.dropdown.Option("cost-optimized", "Cost-Optimized - Budget-friendly configuration"),
                            ft.dropdown.Option("single-provider", "Single Provider - Focus on one LLM"),
                        ],
                        on_change=on_template_change,
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Provider Selection (conditional)
                    ft.Row([
                        ft.Icon(ft.Icons.SMART_TOY, color=ft.Colors.GREEN_600),
                        ft.Text("LLM Provider (for single-provider template):", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Dropdown(
                        ref=provider_dropdown,
                        label="Provider",
                        value="anthropic",
                        options=[
                            ft.dropdown.Option("anthropic", "Anthropic (Claude)"),
                            ft.dropdown.Option("openai", "OpenAI (GPT)"),
                            ft.dropdown.Option("gemini", "Google (Gemini)"),
                        ],
                        visible=False,
                        width=300,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Output File
                    ft.Row([
                        ft.Icon(ft.Icons.SAVE, color=ft.Colors.PURPLE_600),
                        ft.Text("Output File:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.TextField(
                        ref=output_file,
                        label="Configuration file path",
                        hint_text="grading_config.yaml",
                        value="grading_config.yaml",
                        expand=True,
                    ),
                    
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    # Options
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.ORANGE_600),
                        ft.Text("Options:", weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Checkbox(
                        ref=force_checkbox,
                        label="Force overwrite existing file",
                        value=False,
                    ),
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    
                    # Generate Button
                    ft.ElevatedButton(
                        ref=generate_button,
                        text="Generate Configuration",
                        icon=ft.Icons.BUILD,
                        on_click=run_generate_config,
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
            
            # Information Section
            ft.Container(
                content=ft.Column([
                    ft.Text("Configuration Templates:", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text("• Full: Multi-provider setup with Claude, GPT-4o, and Gemini", size=12),
                    ft.Text("• Minimal: Simple configuration for quick setup", size=12),
                    ft.Text("• Cost-Optimized: Budget-friendly settings with cost controls", size=12),
                    ft.Text("• Single Provider: Focus on one LLM with multiple runs", size=12),
                ], spacing=5),
                padding=ft.padding.all(15),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=ft.border_radius.all(8),
                margin=ft.margin.only(top=20),
            ),
            
        ], spacing=10),
        expand=True,
        padding=ft.padding.all(20),
    )