"""Visual theme for the EWOD control console."""

from PyQt5.QtWidgets import QWidget


APP_STYLE = """
QMainWindow,
QWidget#centralwidget {
    background: #edf3f7;
    color: #1d3042;
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 10pt;
}

QFrame#appHeader {
    background: #102f4c;
    border: 1px solid #1d486b;
    border-radius: 16px;
}

QLabel#appTitle {
    color: #ffffff;
    font-size: 18pt;
    font-weight: 700;
}

QLabel#appSubtitle {
    color: #b9d1e4;
    font-size: 9pt;
}

QLabel#headerStatus {
    background: #193e5e;
    border: 1px solid #3d6b8d;
    border-radius: 14px;
    color: #dcecf7;
    font-weight: 600;
    padding: 7px 14px;
}

QLabel#headerStatus[state="connected"] {
    background: #0f766e;
    border-color: #5eead4;
    color: #ecfffc;
}

QLabel#headerStatus[state="notice"] {
    background: #9a5b13;
    border-color: #f3bd63;
    color: #fff7e8;
}

QGroupBox {
    background: #ffffff;
    border: 1px solid #d6e0e8;
    border-radius: 13px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    background: #ffffff;
    color: #245777;
    padding: 0 8px;
    left: 12px;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #c6d5e0;
    border-radius: 8px;
    color: #244158;
    min-height: 31px;
    padding: 4px 12px;
}

QPushButton:hover {
    background: #eaf5fb;
    border-color: #4c9ac2;
    color: #113d59;
}

QPushButton:pressed {
    background: #cfe8f5;
}

QPushButton:disabled {
    background: #eef2f5;
    border-color: #d7e0e6;
    color: #9aa9b4;
}

QPushButton#button_open_serial_port,
QPushButton#button_sta,
QPushButton#button_start1,
QPushButton#button_start2,
QPushButton#button_start3 {
    background: #1877aa;
    border-color: #1877aa;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#button_open_serial_port:hover,
QPushButton#button_sta:hover,
QPushButton#button_start1:hover,
QPushButton#button_start2:hover,
QPushButton#button_start3:hover {
    background: #145f89;
    border-color: #145f89;
}

QPushButton#button_end,
QPushButton#button_pause1,
QPushButton#button_pause2,
QPushButton#button_pause3 {
    background: #fff7e8;
    border-color: #e7b65d;
    color: #82510b;
}

QLineEdit,
QComboBox {
    background: #f8fbfd;
    border: 1px solid #c7d6e0;
    border-radius: 7px;
    color: #1d3042;
    min-height: 30px;
    padding: 2px 8px;
    selection-background-color: #b9def0;
}

QLineEdit:focus,
QComboBox:focus {
    background: #ffffff;
    border: 2px solid #3f91b8;
}

QComboBox::drop-down {
    border: 0;
    width: 24px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #b9cdd9;
    selection-background-color: #d9eef8;
    selection-color: #173d55;
}

QLabel#linkStatus {
    background: #f2f5f7;
    border: 1px solid #cbd8df;
    border-radius: 10px;
    color: #687b88;
    font-weight: 600;
    min-width: 52px;
    padding: 5px 8px;
}

QLabel#linkStatus[state="ok"] {
    background: #dff7ee;
    border-color: #53b892;
    color: #126b52;
}

QLabel#linkStatus[state="error"] {
    background: #ffebe9;
    border-color: #e27b73;
    color: #9c2e29;
}

QTextBrowser {
    background: #102536;
    border: 1px solid #1d435e;
    border-radius: 9px;
    color: #d2e7f0;
    padding: 8px;
    selection-background-color: #2e7192;
}

QGraphicsView,
QLabel#label_cam_view {
    background: #f6fafc;
    border: 1px solid #cbdbe5;
    border-radius: 10px;
}

QLabel#label_cam_view {
    background: #0a1e30;
    color: #9fc3d7;
    font-size: 24pt;
    font-weight: 700;
}

QFrame#button_container {
    background: #e9f1f5;
    border: 1px solid #d1e0e8;
    border-radius: 12px;
}

QPushButton#button_up,
QPushButton#button_down,
QPushButton#button_left,
QPushButton#button_right,
QPushButton#button_zoomout,
QPushButton#button_zoomin {
    background: #ffffff;
    border: 1px solid #b9d0dd;
    border-radius: 13px;
}

QPushButton#button_up:hover,
QPushButton#button_down:hover,
QPushButton#button_left:hover,
QPushButton#button_right:hover,
QPushButton#button_zoomout:hover,
QPushButton#button_zoomin:hover {
    background: #dff2f9;
    border-color: #4095bd;
}

QTabWidget::pane {
    background: #ffffff;
    border: 1px solid #d5e1e8;
    border-radius: 9px;
    top: -1px;
}

QTabBar::tab {
    background: #e8eff3;
    border: 1px solid #d2e0e7;
    border-bottom: 0;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    color: #597080;
    min-height: 29px;
    padding: 5px 13px;
}

QTabBar::tab:hover {
    background: #dcecf3;
    color: #1b5575;
}

QTabBar::tab:selected {
    background: #ffffff;
    border-top: 3px solid #2d8db6;
    color: #164b68;
    font-weight: 700;
}

QTableWidget {
    alternate-background-color: #f5f9fb;
    background: #ffffff;
    border: 1px solid #d3e0e7;
    border-radius: 8px;
    gridline-color: #dce7ed;
    selection-background-color: #cfeaf5;
    selection-color: #153b52;
}

QHeaderView::section {
    background: #e8f0f4;
    border: 0;
    border-bottom: 1px solid #cbdce5;
    color: #36566b;
    font-weight: 700;
    padding: 7px;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #edf3f7;
    border: 0;
    margin: 2px;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #b9cfda;
    border-radius: 5px;
    min-height: 25px;
    min-width: 25px;
}

QScrollBar::handle:hover {
    background: #86b5c8;
}

QStatusBar {
    background: #dfeaf0;
    color: #4d6879;
}
"""


def apply_theme(window):
    """Clear one-off widget styles and apply the shared application theme."""
    for widget in window.findChildren(QWidget):
        if widget.styleSheet():
            widget.setStyleSheet("")
    window.setStyleSheet(APP_STYLE)
