from PySide6.QtWidgets import QMessageBox


def prompt(question: str) -> bool:
    user_response = QMessageBox.question(
        None, "User Confirmation", question, QMessageBox.Yes | QMessageBox.No
    )

    return user_response == QMessageBox.Yes


def error(error_title: str, error_message: str):
    QMessageBox.critical(None, error_title, error_message)
