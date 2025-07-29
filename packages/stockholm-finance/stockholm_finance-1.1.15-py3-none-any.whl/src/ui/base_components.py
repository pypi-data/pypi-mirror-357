#!/usr/bin/env python3
"""
Base UI Components for Stockholm Dashboard
Contains foundational widgets that other modules inherit from
"""

from typing import Optional, Tuple

from textual.events import MouseDown, MouseMove, MouseUp
from textual.widgets import DataTable, Static


class LoadingNotification(Static):
    """Small loading notification widget that appears in bottom right corner"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_current = 0
        self.progress_total = 0
        self.loading_message = "Loading..."

    def update_progress(self, current: int, total: int, message: str = "Loading..."):
        """Update the progress and message"""
        self.progress_current = current
        self.progress_total = total
        self.loading_message = message

        if total > 0:
            percentage = int((current / total) * 100)
            progress_bar = "█" * (percentage // 10) + "░" * (10 - (percentage // 10))
            # Escape square brackets to avoid Textual markup interpretation
            self.update(
                f"🔄 {message}\n\\[{progress_bar}\\] {current}/{total} ({percentage}%)"
            )
        else:
            self.update(f"🔄 {message}")

    def show_loading(self, message: str = "Loading..."):
        """Show loading without progress"""
        self.loading_message = message
        self.update(f"🔄 {message}")
        self.add_class("loading-visible")

    def hide_loading(self):
        """Hide the loading notification"""
        self.remove_class("loading-visible")


class AdjustableDataTable(DataTable):
    """Base class for data tables with adjustable columns, sorting, and no text truncation"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.show_cursor = True

        # Column width configuration - to be overridden by subclasses
        self.column_widths = {}

        # Track if columns have been set up
        self.columns_initialized = False

        # Mouse drag state for column resizing
        self.is_dragging = False
        self.drag_column_index = None
        self.drag_start_x = None
        self.drag_start_width = None
        self.drag_occurred = False  # Track if a drag actually happened

        # Sorting state
        self.sort_column = None
        self.sort_reverse = False
        self.current_data = []  # Store current data for sorting

    def on_mount(self) -> None:
        # Add columns with configurable widths if they are set up
        if self.column_widths:
            self._add_columns()

    def _add_columns(self) -> None:
        """Add columns with configurable widths and sort indicators"""
        if not self.column_widths or self.columns_initialized:
            return

        for col_name, width in self.column_widths.items():
            # Add sort indicator to column name
            display_name = self._get_column_display_name(col_name)
            self.add_column(display_name, width=width, key=col_name)

        self.columns_initialized = True

    def _get_column_display_name(self, col_name: str) -> str:
        """Get column display name with sort indicator"""
        if self.sort_column == col_name:
            arrow = " ↓" if self.sort_reverse else " ↑"
            return f"{col_name}{arrow}"
        return col_name

    def ensure_columns_initialized(self) -> None:
        """Ensure columns are initialized - call this after column_widths is set"""
        if not self.columns_initialized and self.column_widths:
            self._add_columns()

    def _rebuild_with_new_widths(self) -> None:
        """Rebuild the table with updated column widths"""
        try:
            # Prevent rebuilding if columns aren't properly initialized
            if not self.column_widths:
                return

            # Store current data - to be implemented by subclasses
            current_data = self._get_current_data()

            # Clear and rebuild columns
            self.clear(columns=True)
            self.columns_initialized = False  # Reset flag before rebuilding
            self._add_columns()

            # Re-populate data if available
            if current_data:
                self._repopulate_data(current_data)
        except Exception as e:
            # Handle any errors during rebuild gracefully
            self.app.notify(f"Column adjustment failed: {str(e)}", severity="error")

    def _get_current_data(self):
        """Get current table data - to be implemented by subclasses"""
        return []

    def _repopulate_data(self, data):
        """Re-populate table with data - to be implemented by subclasses"""
        pass

    def reset_column_widths(self) -> None:
        """Reset all columns to their default widths"""
        # Store original widths - to be implemented by subclasses
        self.column_widths = self._get_default_column_widths()
        self._rebuild_with_new_widths()

    def _get_default_column_widths(self) -> dict:
        """Get default column widths - to be implemented by subclasses"""
        return {}

    def on_mouse_down(self, event: MouseDown) -> None:
        """Handle mouse down events for column resizing"""
        if not self.column_widths or not self.columns_initialized:
            return

        # Check if the click is near a column border
        column_index, is_near_border = self._get_column_at_position(event.x)

        if is_near_border and column_index is not None:
            # Start dragging
            self.is_dragging = True
            self.drag_column_index = column_index
            self.drag_start_x = event.x

            # Get the current width of the column being resized
            column_keys = list(self.column_widths.keys())
            if column_index < len(column_keys):
                column_name = column_keys[column_index]
                self.drag_start_width = self.column_widths[column_name]

            # Capture mouse to receive all mouse events
            self.capture_mouse()
            event.prevent_default()

    def on_mouse_move(self, event: MouseMove) -> None:
        """Handle mouse move events for column resizing"""
        if not self.is_dragging or self.drag_column_index is None:
            # Check if we're hovering over a column border to show resize cursor
            if self.column_widths and self.columns_initialized:
                _, is_near_border = self._get_column_at_position(event.x)
                # Note: Textual doesn't have cursor changing, but we could show a visual indicator
            return

        # Calculate the change in position
        delta_x = event.x - self.drag_start_x

        # If we've moved more than a few pixels, consider it a drag
        if abs(delta_x) > 3:
            self.drag_occurred = True

        # Calculate new width (minimum of 5 characters)
        new_width = max(5, self.drag_start_width + int(delta_x))

        # Update the column width
        column_keys = list(self.column_widths.keys())
        if self.drag_column_index < len(column_keys):
            column_name = column_keys[self.drag_column_index]
            self.column_widths[column_name] = new_width

            # Rebuild the table with new widths
            self._rebuild_with_new_widths()

    def on_mouse_up(self, event: MouseUp) -> None:
        """Handle mouse up events to end column resizing"""
        if self.is_dragging:
            self.is_dragging = False
            self.drag_column_index = None
            self.drag_start_x = None
            self.drag_start_width = None

            # Release mouse capture
            self.release_mouse()

            # Column width adjusted - no notification needed

            # Reset drag_occurred flag after a short delay to allow header event to check it
            self.set_timer(0.1, self._reset_drag_flag)

    def _reset_drag_flag(self) -> None:
        """Reset the drag occurred flag"""
        self.drag_occurred = False

    def _get_column_at_position(self, x: float) -> Tuple[Optional[int], bool]:
        """Get the column index at the given x position and whether it's near a border"""
        if not self.column_widths:
            return None, False

        # Get the actual rendered column positions from the DataTable
        # We need to account for padding and separators
        column_keys = list(self.column_widths.keys())

        # Try to use the DataTable's internal column positioning if available
        try:
            # Calculate positions based on actual column widths including padding
            current_x = 0
            cell_padding = getattr(
                self, "cell_padding", 1
            )  # Default padding is usually 1

            for i, column_name in enumerate(column_keys):
                column_width = self.column_widths[column_name]
                # Add padding to the column width for actual rendered width
                rendered_width = column_width + (cell_padding * 2)
                column_end = current_x + rendered_width

                # Check if we're near the right border of this column (within 3 characters for better detection)
                if abs(x - column_end) <= 3:
                    return i, True

                # Check if we're within this column
                if current_x <= x < column_end:
                    return i, False

                current_x = column_end

                # Add separator space between columns (usually 1 character)
                if i < len(column_keys) - 1:  # Don't add separator after last column
                    current_x += 1

        except Exception:
            # Fallback to simpler calculation if the above fails
            current_x = 0
            for i, column_name in enumerate(column_keys):
                column_width = self.column_widths[column_name]
                column_end = current_x + column_width + 2  # Add some padding

                # Check if we're near the right border of this column
                if abs(x - column_end) <= 3:
                    return i, True

                # Check if we're within this column
                if current_x <= x < column_end:
                    return i, False

                current_x = column_end + 1  # Add separator space

        return None, False

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Handle column header clicks for sorting"""
        # Don't sort if a drag operation just occurred (column resizing)
        if self.drag_occurred:
            return

        column_key = event.column_key

        # Toggle sort direction if same column, otherwise start with ascending
        if self.sort_column == column_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_key
            self.sort_reverse = False

        # Re-sort and update the table
        self._sort_and_update()

        # Sort change applied - no notification needed

    def _sort_and_update(self) -> None:
        """Sort current data and update table display efficiently"""
        if not self.current_data or not self.sort_column:
            return

        # Sort the data
        sorted_data = self._sort_data(
            self.current_data, self.sort_column, self.sort_reverse
        )

        # Efficient update: just update the column headers and re-populate data
        # Don't clear/rebuild the entire table structure
        self._update_column_headers()
        self._fast_repopulate(sorted_data)

    def _sort_data(self, data: list, sort_column: str, reverse: bool) -> list:
        """Sort data by column - to be implemented by subclasses"""
        return data

    def _update_column_headers(self) -> None:
        """Update column headers with sort indicators efficiently"""
        # Since Textual DataTable doesn't support updating column headers directly,
        # we need to rebuild the table structure with updated column headers
        try:
            # Store current data before rebuilding
            current_data = self._get_current_data()

            # Clear and rebuild columns with updated sort indicators
            self.clear(columns=True)
            self.columns_initialized = False
            self._add_columns()  # This will call _get_column_display_name with current sort state

            # Re-populate with current data
            if current_data:
                self._repopulate_data(current_data)

        except Exception:
            # If header update fails, fall back to notification
            # This ensures the sorting still works even if header update fails
            sort_direction = "descending" if self.sort_reverse else "ascending"
            self.app.notify(
                f"Sorted by {self.sort_column} ({sort_direction})", timeout=2
            )

    def _fast_repopulate(self, data: list) -> None:
        """Fast repopulation - to be implemented by subclasses"""
        # Default implementation falls back to full rebuild
        self.clear()
        self._repopulate_data(data)

    def _update_table_display(self, data: list) -> None:
        """Update table display with sorted data - to be implemented by subclasses"""
        pass
