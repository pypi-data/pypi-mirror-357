from PySide6.QtWidgets import QLabel


def display_message(frame, message, msg_type="error"):
    """Display a message in the given frame."""
    # Remove existing message label if any
    for child in frame.findChildren(QLabel):
        if getattr(child, "_is_msg_label", False):
            child.deleteLater()

    color_map = {
        "error": "#fa3030",      # Red
        "success": "#2cc231",    # Green
        "info": "#2196f3",       # Blue
        "warning": "#ff9800"     # Orange
    }
    msg_color = color_map.get(msg_type, "#ffffff")

    msg_label = QLabel(message, frame)
    msg_label.setStyleSheet(
        f"color: {msg_color}; background-color: #1e1e1e; font-weight: bold; font-family: 'Segoe UI'; font-size: 10pt;"
    )
    msg_label.setWordWrap(True)
    msg_label._is_msg_label = True  # Tag the label so we can identify and replace it
    msg_label.setObjectName("msg_label")
    frame.layout().addWidget(msg_label)


def clear_message(frame):
    """Remove message label from the frame if present."""
    for child in frame.findChildren(QLabel):
        if getattr(child, "_is_msg_label", False):
            child.deleteLater()
