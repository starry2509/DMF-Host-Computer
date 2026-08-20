import logging
from datetime import datetime
import os
import sys
class QTextBrowserLogger(logging.Handler):
    def __init__(self, text_browser=None):
        super().__init__()
        self.text_browser = text_browser
        self.colors = {
            logging.DEBUG: 'black',
            logging.INFO: 'blue',
            logging.WARNING: 'orange',
            logging.ERROR: 'red',
            logging.CRITICAL: 'purple'
        }
    def emit(self, record):
        if self.text_browser is None:
            return
        log_time = datetime.now().strftime("%H:%M:%S")
        log_level = logging.getLevelName(record.levelno)
        log_message = self.format(record)
        color = self.colors.get(record.levelno, 'black')
        log_entry = f'<span style="color:{color}">[{log_time}] [{log_level}] {log_message}</span>'
        self.text_browser.append(log_entry)
        self.text_browser.moveCursor(self.text_browser.textCursor().End)
        self.text_browser.ensureCursorVisible()


class LevelRangeFilter(logging.Filter):
    def __init__(self, min_level, max_level):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level
    def filter(self, record):
        return self.min_level <= record.levelno <= self.max_level
class BrowseLog:
    def __init__(self, text_browser1=None, text_browser2=None):
        self.text_browser1 = text_browser1
        self.text_browser2 = text_browser2

        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_file_path = os.path.join(base_path, 'logger', 'logger_data')
        if not os.path.exists(self.log_file_path):
            os.makedirs(self.log_file_path)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        if self.logger.handlers:
            self.logger.handlers = []

        self.qt_handler1 = None
        self.qt_handler2 = None
        self.file_handler = None  # 通用文件处理器

        if text_browser1:#记录开关操作
            self.qt_handler1 = QTextBrowserLogger(text_browser1)
            self.qt_handler1.setLevel(logging.DEBUG)
            filter_debug_info = LevelRangeFilter(logging.DEBUG,logging.DEBUG)
            self.qt_handler1.addFilter(filter_debug_info)
            self.qt_formatter1 = logging.Formatter('%(message)s')
            self.qt_handler1.setFormatter(self.qt_formatter1)
            self.logger.addHandler(self.qt_handler1)

        if text_browser2:#记录串口数据
            self.qt_handler2 = QTextBrowserLogger(text_browser2)
            self.qt_handler2.setLevel(logging.INFO)
            filter_debug_info = LevelRangeFilter(logging.INFO, logging.INFO)
            self.qt_handler2.addFilter(filter_debug_info)
            self.qt_formatter2 = logging.Formatter('%(message)s')
            self.qt_handler2.setFormatter(self.qt_formatter2)
            self.logger.addHandler(self.qt_handler2)
        
        # 创建文件处理器（按需启用）
        file_name = "{}.log".format(datetime.now().strftime("%Y-%m-%d"))
        log_file = os.path.join(self.log_file_path, file_name)
        self.file_handler = logging.FileHandler(log_file, mode='a+', encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s', 
                                         datefmt='%Y-%m-%d %H:%M:%S')
        self.file_handler.setFormatter(file_formatter)
    def log(self, record_to_file, message, level=logging.INFO):
        """
        记录日志
        :param record_to_file: True表示同时记录到文件，False表示只在QTextBrowser显示
        :param message: 日志信息
        :param level: 日志级别，默认为logging.INFO
        """
        # 如果记录到文件，临时添加文件处理器
        file_handler_added = False
        if record_to_file:
            if self.file_handler not in self.logger.handlers:
                self.logger.addHandler(self.file_handler)
                file_handler_added = True
        self.logger.log(level, message)
        if file_handler_added:
            self.logger.removeHandler(self.file_handler)
    def debug(self, record_to_file, message):
        self.log(record_to_file, message, logging.DEBUG)
    def info(self, record_to_file, message):
        self.log(record_to_file, message, logging.INFO)
    def warning(self, record_to_file, message):
        self.log(record_to_file, message, logging.WARNING)
    def error(self, record_to_file, message):
        self.log(record_to_file, message, logging.ERROR)
    def critical(self, record_to_file, message):
        self.log(record_to_file, message, logging.CRITICAL)
    def read_log_file(self, date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_name = "{}.log".format(date_str)
        log_file = os.path.join(self.log_file_path, file_name)
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"读取日志文件失败: {e}"
        else:
            return f"日志文件不存在: {log_file}"
