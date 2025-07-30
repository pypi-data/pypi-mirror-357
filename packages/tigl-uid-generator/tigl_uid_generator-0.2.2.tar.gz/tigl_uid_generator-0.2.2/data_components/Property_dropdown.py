# data_components/property_dropdown.py

from dotenv import load_dotenv
import os
from backend.connect_to_db import get_db
from ui_components.dropdown import create_dropdown
from ui_components.error_msg import display_message
from PySide6.QtWidgets import QLabel

from backend.DB_Operations import (
    fetch_properties_for_category,
    has_filter_column,
    fetch_property_details_with_filter,
    fetch_property_details_without_filter
)

load_dotenv()

dynamic_property_widgets = []
final_uid_callback = None

def on_category_change(category, cat_mapped_value, form_layout, on_final_uid, clear_results):
    global final_uid_callback, dynamic_property_widgets

    while dynamic_property_widgets:
        widget_to_remove = dynamic_property_widgets.pop(0)
        widget_to_remove.setParent(None)
        widget_to_remove.deleteLater()
    
    if not category or not cat_mapped_value:
        return

    final_uid_callback = on_final_uid
    
    db_url_key = f"NEON_DB_{category}_URL"
    db_path = os.getenv(db_url_key)
    db_gen = get_db(db_path)
    db = next(db_gen)
    if not db_path:
        display_message(form_layout.parent(), f"Environment variable {db_url_key} not found.", msg_type="error")
        return

    
    
    try:
        

        properties_result = fetch_properties_for_category(db)
        properties = [row[0] for row in properties_result]
            
        uid_parts = [""] * len(properties)
        prop_values = ["-1"] * len(properties)
        
        active_rows_in_chain = []

        def create_property_dropdown(header_index):
            if header_index >= len(properties):
                if all(part not in ("", None) for part in uid_parts):
                    full_uid = "B" + str(cat_mapped_value) + "".join(map(str, uid_parts))
                    selected_props = [(properties[i], prop_values[i]) for i in range(len(properties))]
                    if final_uid_callback:
                        final_uid_callback(full_uid, selected_props)
                return

            header = properties[header_index]
            table_name = header

            

            has_filter = has_filter_column(db, table_name)

            results = []
            if has_filter:
                    cummulative_prop_val = ""
                    previous_selections = [v for v in prop_values[:header_index] if v != "-1"]

                    for item in previous_selections:
                        if not cummulative_prop_val:
                            cummulative_prop_val = item
                        else:
                            cummulative_prop_val += "_" + item
                        
                        query_result = fetch_property_details_with_filter(
                            db, table_name, item, cummulative_prop_val
                        )

                        if query_result:
                            results = query_result
                            break

            if not results:
                    results = fetch_property_details_without_filter(db, table_name)

            options = [""] + [row[1] for row in results]

            label = QLabel(f"{header}:")
            dropdown = create_dropdown(options)
            
            form_layout.addRow(label, dropdown)
            
            dynamic_property_widgets.append(label)
            dynamic_property_widgets.append(dropdown)
            active_rows_in_chain.append((label, dropdown))

            def on_property_change(selected_text):
                clear_results()
                
                rows_to_be_removed = active_rows_in_chain[header_index + 1:]
                del active_rows_in_chain[header_index + 1:]
                for lbl, drp in rows_to_be_removed:
                    if lbl in dynamic_property_widgets: dynamic_property_widgets.remove(lbl)
                    if drp in dynamic_property_widgets: dynamic_property_widgets.remove(drp)
                for lbl, drp in rows_to_be_removed:
                    lbl.setParent(None); lbl.deleteLater()
                    drp.setParent(None); drp.deleteLater()

                if not selected_text:
                    uid_parts[header_index] = ""
                    prop_values[header_index] = "-1"
                    return

                prop_values[header_index] = selected_text
                
                # DB functions return (id, key, value, ...), so value is at index 2
                value = next((row[2] for row in results if row[1] == selected_text), None)
                uid_parts[header_index] = str(value) if value is not None else ""

                create_property_dropdown(header_index + 1)

            dropdown.currentTextChanged.connect(on_property_change)

        create_property_dropdown(0)

    except Exception as e:
        print(f"An unexpected error occurred in on_category_change: {e}")