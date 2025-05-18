import dearpygui.dearpygui as dpg
import pandas as pd
import numpy as np

# Global data
app_data = {
    "excel_file": None,
    "sheets": [],
    "dataframes": {},
    "current_df": None
}

# Load Excel and populate sheets
def load_excel_callback(sender, file):
    try:
        file_path = file['file_path_name']
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        app_data["sheets"] = xls.sheet_names
        app_data["dataframes"] = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        app_data["excel_file"] = file_path

        dpg.set_value("status_text", f"Loaded: {file_path}")
        dpg.configure_item("sheet_combo", items=app_data["sheets"])

    except Exception as e:
        dpg.set_value("status_text", f"Error loading file: {e}")

# When a sheet is selected, update column dropdowns and checkboxes
def display_columns_callback(sender, app_data_local):
    sheet = dpg.get_value("sheet_combo")
    df = app_data["dataframes"].get(sheet)

    if df is not None:
        app_data["current_df"] = df
        dpg.set_value("columns_text", f"Columns in '{sheet}':\n{', '.join(df.columns)}")
        dpg.configure_item("x_col_combo", items=list(df.columns))
        if dpg.does_item_exist("pie_col_combo"):
            dpg.configure_item("pie_col_combo", items=list(df.columns))

        # Clear and rebuild Y column checkboxes
        dpg.delete_item("y_col_checkboxes", children_only=True)
        for col in df.columns:
            dpg.add_checkbox(label=col, tag=f"ycol_chk_{col}", parent="y_col_checkboxes")

    else:
        dpg.set_value("columns_text", "Invalid sheet or no data.")

# Generate analysis text
def generate_basic_analysis(df, y_cols):
    analysis_lines = []

    for col in y_cols:
        col_data = pd.to_numeric(df[col], errors='coerce').dropna()
        if col_data.empty:
            analysis_lines.append(f"• {col}: No valid numeric data.\n")
            continue

        count = col_data.count()
        mean = col_data.mean()
        median = col_data.median()
        std = col_data.std()
        minimum = col_data.min()
        maximum = col_data.max()

        stats_text = (
            f"{col}:\n"
            f"    - Count: {count}\n"
            f"    - Mean: {mean:.2f}\n"
            f"    - Median: {median:.2f}\n"
            f"    - Std Dev: {std:.2f}\n"
            f"    - Min: {minimum:.2f}\n"
            f"    - Max: {maximum:.2f}"
        )

        insight = ""
        if abs(mean - median) / (std + 1e-6) > 0.5:
            skew_type = "right" if mean > median else "left"
            insight += f"\n    - Insight: May be {skew_type}-skewed."
        if std / (mean + 1e-6) > 0.5:
            insight += "\n    - Insight: High variability in data."

        try:
            x_numeric = np.arange(len(col_data))
            slope, _ = np.polyfit(x_numeric, col_data.values, 1)
            if abs(slope) > 0.01:
                trend = "increasing" if slope > 0 else "decreasing"
                insight += f"\n    - Insight: Trend is {trend}."
        except Exception:
            pass

        analysis_lines.append(stats_text + insight + "\n")

    return "\n".join(analysis_lines)


def plot_callback():
    df = app_data.get("current_df")
    if df is None:
        dpg.set_value("columns_text", "No data loaded.")
        return

    x_col = dpg.get_value("x_col_combo")
    if not x_col:
        dpg.set_value("columns_text", "Please select an X column.")
        return

    # Gather selected Y columns from checkboxes
    y_cols = [col for col in df.columns if dpg.does_item_exist(f"ycol_chk_{col}") and dpg.get_value(f"ycol_chk_{col}")]
    if not y_cols:
        dpg.set_value("columns_text", "Please select at least one Y column.")
        return

    try:
        def clean_column(series):
            return pd.to_numeric(series.astype(str).str.replace(r"[^\d.]+", "", regex=True), errors='coerce')

        x_data = clean_column(df[x_col])
        valid_mask = x_data.notna()
        x_data = x_data[valid_mask]

        if x_data.empty:
            dpg.set_value("columns_text", "No valid X data to plot.")
            return

        dpg.delete_item("plot_area", children_only=True)

        with dpg.plot(label="Chart", height=300, width=-1, parent="plot_area"):
            dpg.add_plot_axis(dpg.mvXAxis, label=x_col)
            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Values")

            for y_col in y_cols:
                y_data = clean_column(df[y_col])[valid_mask]
                if y_data.empty:
                    continue
                dpg.add_line_series(x_data.tolist(), y_data.tolist(), label=f"{y_col}", parent=y_axis)

        # Generate and display basic analysis
        analysis_text = generate_basic_analysis(df, y_cols)
        dpg.set_value("summary_text", analysis_text)

    except Exception as e:
        dpg.set_value("columns_text", f"Plot error: {e}")


def reset_callback():
    app_data["current_df"] = None
    app_data["excel_file"] = None
    app_data["sheets"] = []
    app_data["dataframes"] = {}

    dpg.set_value("sheet_combo", "")
    dpg.configure_item("sheet_combo", items=[])  # Clear old sheet list
    dpg.set_value("x_col_combo", "")
    dpg.configure_item("x_col_combo", items=[])
    dpg.set_value("columns_text", "")
    dpg.set_value("status_text", "Reset.")
    dpg.set_value("summary_text", "")
    dpg.delete_item("y_col_checkboxes", children_only=True)
    dpg.delete_item("plot_area", children_only=True)


# GUI Setup
dpg.create_context()

with dpg.window(label="Excel Visualizer", width=1080, height=720):
    dpg.add_button(label="Select Excel File", callback=lambda: dpg.show_item("file_dialog"))
    dpg.add_text("", tag="status_text")
    dpg.add_combo([], label="Sheet", tag="sheet_combo", callback=display_columns_callback)
    dpg.add_text("", tag="columns_text")

    dpg.add_separator()

    dpg.add_text("Choose X column:")
    dpg.add_combo([], label="X Axis", tag="x_col_combo")

    dpg.add_text("Select Y columns:")
    dpg.add_child_window(tag="y_col_checkboxes", height=120, autosize_x=True)

    dpg.add_button(label="Plot", callback=plot_callback)
    dpg.add_button(label="Reset", callback=reset_callback)

    dpg.add_spacer(height=10)
    dpg.add_child_window(height=320, tag="plot_area", autosize_x=True)

    dpg.add_separator()

    dpg.add_tab_bar(tag="analysis_tabs")

    with dpg.tab(label="Basic Analysis", parent="analysis_tabs"):
        dpg.add_text("Summary Statistics:")
        dpg.add_child_window(tag="summary_container", autosize_x=True, height=500)
        with dpg.child_window(parent="summary_container", autosize_x=True, autosize_y=True):
            dpg.add_text("", tag="summary_text", wrap=800)

    with dpg.tab(label="Notes", parent="analysis_tabs"):
        dpg.add_input_text(multiline=True, height=100, width=-1, label="Your Notes")

    with dpg.file_dialog(
        directory_selector=False, show=False, callback=load_excel_callback, tag="file_dialog",
        width=880, height=520
    ):
        dpg.add_file_extension(".xlsx", color=(0, 255, 0, 255))
        dpg.add_file_extension(".xls", color=(255, 255, 0, 255))

dpg.create_viewport(title='Excel Visualizer', width=1080, height=720)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
