from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from tkinter import StringVar
from ui_components.dropdown import create_dropdown
from ui_components.error_msg import display_message
from sqlalchemy.exc import SQLAlchemyError
import threading

load_dotenv()

dropdown_widgets = []
final_uid_callback = None

def on_category_change(*args, category, cat_mapped_value, property_frame, root, on_final_uid=None, clear_uid_table=None):
    global final_uid_callback
    final_uid_callback = on_final_uid

    for widget in property_frame.winfo_children():
        widget.destroy()
    dropdown_widgets.clear()

    # Fetch DB URL from environment
    db_url_key = f"NEON_DB_{category}_URL"
    db_path = os.getenv(db_url_key)
    print(db_path)
    if not db_path:
        display_message(property_frame, f"Environment variable {db_url_key} not found.", msg_type="error")
        return

    if not category or not cat_mapped_value:
        display_message(property_frame, f"Invalid Category Selected", msg_type="error")
        return

    def db_worker():
        try:
            engine = create_engine(db_path)
            conn = engine.connect()
        except SQLAlchemyError as e:
            root.after(0, lambda: display_message(property_frame, f"Database connection error: {e}", msg_type="error"))
            return

        # Get table names from Headers
        try:
            result = conn.execute(text(f"""SELECT "Properties" FROM "Headers" """)).fetchall()
        except SQLAlchemyError as e:
            result = []
        properties = [row[0] for row in result]
        uid_parts = [""] * len(properties)
        prop_values = ["-1"] * len(properties)
        uid_var = StringVar(value="B" + cat_mapped_value)

        # Prepare all property options in advance
        all_options = []
        all_results = []
        for header in properties:
            table_name = header
            # Check for 'Filter' column
            try:
                filter_result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = :table AND column_name = :column
                """), {'table': table_name, 'column': 'Filter'}).fetchall()
            except SQLAlchemyError:
                filter_result = []
            has_filter = bool(filter_result)
            if has_filter:
                stmt = text(f"""
                    SELECT id, "{table_name}_key", "{table_name}_value", "Filter"
                    FROM "{table_name}"
                """)
            else:
                stmt = text(f"""
                    SELECT id, "{table_name}_key", "{table_name}_value"
                    FROM "{table_name}"
                """)
            try:
                results = conn.execute(stmt).fetchall()
            except SQLAlchemyError:
                results = []
            options = [row[1] for row in results]
            all_options.append(options)
            all_results.append(results)

        def create_dropdowns_ui():
            def on_any_dropdown_change(*args):
                for i, widget in enumerate(dropdown_widgets):
                    value = widget.var.get()
                    if value not in widget.options:
                        for w in dropdown_widgets[i+1:]:
                            w.grid_remove()
                        break
                    else:
                        if i+1 < len(dropdown_widgets):
                            dropdown_widgets[i+1].set_enabled(True)

            def create_property_dropdown(header_index, prop_values):
                if header_index >= len(properties):
                    return

                header = properties[header_index]
                prop_var = StringVar(value=f"Select {header}")
                options = all_options[header_index]
                results = all_results[header_index]

                def on_property_change(*args, prop_var=prop_var, header_index=header_index):
                    if clear_uid_table:
                        clear_uid_table()
                    prop_values[header_index] = prop_var.get()
                    for i in range(header_index + 1, len(prop_values)):
                        prop_values[i] = "-1"
                        uid_parts[i] = ""

                    for i in range(header_index + 1, len(dropdown_widgets)):
                        widget = dropdown_widgets[i]
                        if hasattr(widget, "destroy"):
                            widget.destroy()
                    dropdown_widgets[:] = dropdown_widgets[:header_index + 1]

                    value = None
                    for row in results:
                        if row[1] == prop_values[header_index]:
                            value = row[2]
                            break

                    if value not in (None, "-1"):
                        uid_parts[header_index] = value
                        full_uid = "B" + cat_mapped_value + "".join(uid_parts)
                        uid_var.set(full_uid)

                        if all(uid_parts):
                            selected_props = [(properties[i], prop_values[i]) for i in range(len(properties))]
                            if final_uid_callback:
                                final_uid_callback(full_uid, selected_props)

                    create_property_dropdown(header_index + 1, prop_values)
                    on_any_dropdown_change()

                prop_var.trace_add("write", on_property_change)
                dropdown, _ = create_dropdown(property_frame, f"{header}:", options, row=header_index + 1, var=prop_var)
                dropdown_widget = dropdown[0] if isinstance(dropdown, (tuple, list)) else dropdown
                dropdown_widgets.append(dropdown_widget)
                if header_index != 0:
                    dropdown_widget.set_enabled(False)

            create_property_dropdown(0, prop_values)

        root.after(0, create_dropdowns_ui)

    threading.Thread(target=db_worker, daemon=True).start()
