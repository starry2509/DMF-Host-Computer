from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGroupBox, QPushButton, QSizePolicy, QTabWidget, QHBoxLayout,
                             QVBoxLayout, QFrame, QComboBox, QLineEdit,
                             QGraphicsView, QTextBrowser, QGridLayout, QHeaderView,
                             QTableWidget, QAbstractScrollArea, QAbstractItemView, QLabel)
from PyQt5.QtCore import QSize,Qt,QLocale,QMetaObject
from PyQt5.QtGui import QIcon, QPainter, QFont, QKeySequence
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from utils.path_helper import get_resource_path

class UI(object):
    def _make_temperature_plot(self, parent, title):
        """创建温度/功率双轴曲线控件。"""
        widget = PlotWidget(parent)
        widget.setBackground("w")
        widget.setTitle(title, color='#333')
        widget.setLabel("bottom", "时间 (s)")
        plot_item = widget.getPlotItem()
        bottom_axis = plot_item.getAxis("bottom")
        left_axis = plot_item.getAxis("left")
        right_axis = plot_item.getAxis("right")
        # 坐标轴样式（与him一致）
        bottom_axis.setPen(pg.mkPen(color=(0, 0, 0, 255), width=1))
        # 左轴刻度颜色为红色
        left_axis.setPen(pg.mkPen(color='red', width=1))
        left_axis.setTextPen(pg.mkPen(color='red'))
        # 右轴刻度颜色为绿色
        right_axis.setPen(pg.mkPen(color='green', width=1))
        right_axis.setTextPen(pg.mkPen(color='green'))
        plot_item.showAxis('right', True)
        left_axis.setLabel("温度(°C)", color='red')  # 左轴标签（温度）红色
        right_axis.setLabel("功率(W)", color='green')  # 右轴标签（功率）绿色
        widget.showGrid(x=True, y=True, alpha=0.15)
        plot_item.getViewBox().setAutoPan(y=True)
        plot_item.enableAutoRange(axis='y', enable=True)
        plot_item.enableAutoRange(axis='x', enable=True)  # 启用X轴自动范围
        left_axis.enableAutoSIPrefix(enable=True)
        right_axis.enableAutoSIPrefix(enable=True)
        plot_item.getViewBox().setLimits(xMin=0)  # X轴最小值限制为0
        temp_curve = widget.plot([], [], pen=pg.mkPen(color="red", width=2), name="温度")
        # 创建右轴的ViewBox（用于功率曲线，X轴与主ViewBox同步）
        power_viewbox = pg.ViewBox()
        plot_item.scene().addItem(power_viewbox)
        plot_item.getViewBox().sigXRangeChanged.connect(
            lambda: power_viewbox.setXRange(*plot_item.getViewBox().viewRange()[0])
        )
        right_axis.linkToView(power_viewbox)
        # 设置功率轴的固定范围和刻度（0-5，间隔0.5）
        power_viewbox.setYRange(0, 5, padding=0)
        power_viewbox.setLimits(yMin=0, yMax=5)
        right_axis.setTicks([[(i * 0.5, f'{i * 0.5:.1f}') for i in range(0, 11)]])  # 0到5，间隔0.5
        power_curve = pg.PlotDataItem([], [], pen=pg.mkPen(color="green", width=2), name="功率")
        power_viewbox.addItem(power_curve)
        # 限制只能Y轴缩放，X轴根据数据自动调整
        plot_item.getViewBox().setMouseEnabled(x=False, y=True)
        power_viewbox.setMouseEnabled(x=False, y=False)  # 禁用功率轴的Y轴缩放
        plot_item.layout.addItem(power_viewbox, 2, 1)
        return widget, temp_curve, power_viewbox, power_curve

    def _make_temperature_controls(self, tab, channel, pid_edit_style, button_style):
        """创建温度通道底部 PID 与操作按钮行。"""
        layout = QHBoxLayout()
        target = QLineEdit(tab)
        target.setPlaceholderText("设定温度(℃)")
        target.setStyleSheet(pid_edit_style)
        p_edit = QLineEdit(tab)
        p_edit.setPlaceholderText("P参数")
        p_edit.setStyleSheet(pid_edit_style)
        i_edit = QLineEdit(tab)
        i_edit.setPlaceholderText("I参数")
        i_edit.setStyleSheet(pid_edit_style)
        d_edit = QLineEdit(tab)
        d_edit.setPlaceholderText("D参数")
        d_edit.setStyleSheet(pid_edit_style)
        btn_start = QPushButton(tab)
        btn_start.setText("开始")
        btn_start.setStyleSheet(button_style)
        btn_pause = QPushButton(tab)
        btn_pause.setText("暂停")
        btn_pause.setStyleSheet(button_style)
        btn_save = QPushButton(tab)
        btn_save.setText("保存")
        btn_save.setStyleSheet(button_style)
        btn_load = QPushButton(tab)
        btn_load.setText("加载")
        btn_load.setStyleSheet(button_style)
        btn_clear = QPushButton(tab)
        btn_clear.setText("清除")
        btn_clear.setStyleSheet(button_style)
        for w in (target, p_edit, i_edit, d_edit, btn_start, btn_pause, btn_save, btn_load, btn_clear):
            layout.addWidget(w)
        setattr(self, f'lineEdit_target_temp{channel}', target)
        setattr(self, f'lineEdit_P{channel}', p_edit)
        setattr(self, f'lineEdit_I{channel}', i_edit)
        setattr(self, f'lineEdit_D{channel}', d_edit)
        setattr(self, f'button_start{channel}', btn_start)
        setattr(self, f'button_pause{channel}', btn_pause)
        setattr(self, f'button_save{channel}', btn_save)
        setattr(self, f'button_load{channel}', btn_load)
        setattr(self, f'button_clear{channel}', btn_clear)
        return layout

    def _build_temperature_tab(self, channel, pid_edit_style, button_style):
        """组装单个温度监测 Tab（曲线 + 控件行）。"""
        tab = QWidget(self.tabWidget2)
        setattr(self, f'tab_tem{channel}', tab)
        layout = QVBoxLayout(tab)
        setattr(self, f'layout_V_Right_V2_V{channel}', layout)
        widget, temp_curve, power_viewbox, power_curve = self._make_temperature_plot(
            tab, f"通道{channel} 温度曲线（双击放大）"
        )
        setattr(self, f'temperature_widget{channel}', widget)
        setattr(self, f'temperature_curve{channel}', temp_curve)
        setattr(self, f'power_viewbox{channel}', power_viewbox)
        setattr(self, f'power_curve{channel}', power_curve)
        btn_layout = self._make_temperature_controls(tab, channel, pid_edit_style, button_style)
        setattr(self, f'layout_V_Right_V2_V{channel}_H1', btn_layout)
        layout.addWidget(widget)
        layout.addLayout(btn_layout)
        layout.setStretch(0, 10)
        layout.setStretch(1, 1)
        return tab

    def SetUpUi(self,MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600,1075)
        MainWindow.setIconSize(QSize(60,60))
        MainWindow.setWindowIcon(QIcon(get_resource_path("../icon/dmf.png")))
        MainWindow.setWindowTitle("玻璃基驱动线路板专用驱动器 V2.1.0")
        screen = QApplication.primaryScreen().geometry()
        size = MainWindow.geometry()
        MainWindow.move((screen.width() - size.width()) // 2,
                  (screen.height() - size.height()) // 2)
        """
        创建 QWidget 作为主窗口MainWindow的中心部件，承载界面内容的 “容器基础”,继承于QMainWindow
        """
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        """
        总体水平布局
        """
        self.layout_H = QHBoxLayout(self.centralwidget)
        self.layout_H.setContentsMargins(3, 3, 3, 3)
        self.layout_H.setObjectName("layout_h")
        """左侧"""
        self.groupBox1 = QGroupBox(self.centralwidget)
        self.groupBox1.setContentsMargins(3, 3, 3, 3)
        self.groupBox1.setTitle("系统初始化")
        self.groupBox1.setStyleSheet("""
            QGroupBox {border: 1px solid;margin-top: 1.5ex;padding: 10px;}
            QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}
        """)
        """中间垂直布局"""
        self.layout_V_Middle = QVBoxLayout(self.centralwidget)
        self.layout_V_Middle.setContentsMargins(3, 3, 3, 3)
        self.layout_V_Middle.setObjectName("layout_V_Middle")
        """右侧垂直布局"""
        self.layout_V_Right = QVBoxLayout(self.centralwidget)
        self.layout_V_Right.setContentsMargins(3, 3, 3, 3)
        self.layout_V_Right.setObjectName("layout_V_Right")
        """左侧部分"""
        self.layout_V_Left = QVBoxLayout(self.groupBox1)
        """分组框一"""
        self.groupBox1_1 = QGroupBox(self.groupBox1)
        self.groupBox1_1.setTitle("一 串口设置")
        self.groupBox1_1.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.gird_layout = QGridLayout(self.groupBox1_1)
        self.comboBox = QComboBox(self.groupBox1_1)

        button_style = "QPushButton { background-color: white;} QPushButton::pressed { background-color: #e6e6e6; }"
        label_button_style = "QLabel { background-color: white; border: 1px solid #ddd; padding: 5px;}"

        self.button_open_serial_port = QPushButton(self.groupBox1_1)
        self.button_open_serial_port.setText("打开串口")
        self.button_open_serial_port.setStyleSheet(button_style)
        self.button_flush_serial_port = QPushButton(self.groupBox1_1)
        self.button_flush_serial_port.setText("刷新")
        self.button_flush_serial_port.setStyleSheet(button_style)
        self.button_close_serial_port = QPushButton(self.groupBox1_1)
        self.button_close_serial_port.setText("关闭串口")
        self.button_close_serial_port.setStyleSheet(button_style)


        self.button1 = QPushButton(self.groupBox1_1)
        self.button1.setText("芯片物理连接正常:")
        self.button1.setStyleSheet(button_style)
        self.label1_button= QLabel(self.groupBox1_1)
        self.label1_button.setStyleSheet(label_button_style)
        self.label1_button.setText("正常")
        self.label1_button.setAlignment(Qt.AlignCenter)

        self.button2 = QPushButton(self.groupBox1_1)
        self.button2.setText("左侧加热连接正常:")
        self.button2.setStyleSheet(button_style)
        self.label2_button = QLabel(self.groupBox1_1)
        self.label2_button.setStyleSheet(label_button_style)
        self.label2_button.setText("正常")
        self.label2_button.setAlignment(Qt.AlignCenter)

        self.button3 = QPushButton(self.groupBox1_1)
        self.button3.setText("右侧加热连接正常:")
        self.button3.setStyleSheet(button_style)
        self.label3_button = QLabel(self.groupBox1_1)
        self.label3_button.setStyleSheet(label_button_style)
        self.label3_button.setText("正常")
        self.label3_button.setAlignment(Qt.AlignCenter)

        self.gird_layout.addWidget(self.comboBox,0,0,1,7)
        self.gird_layout.addWidget(self.button_open_serial_port,1,0,1,3)
        self.gird_layout.addWidget(self.button_flush_serial_port, 1, 3, 1, 1)
        self.gird_layout.addWidget(self.button_close_serial_port,1,4,1,3)
        self.gird_layout.addWidget(self.button1,3,0,1,4)
        self.gird_layout.addWidget(self.label1_button,3,6,1,1)
        self.gird_layout.addWidget(self.button2, 4, 0, 1, 4)
        self.gird_layout.addWidget(self.label2_button, 4, 6, 1, 1)
        self.gird_layout.addWidget(self.button3, 5, 0, 1, 4)
        self.gird_layout.addWidget(self.label3_button, 5, 6, 1, 1)
        """分组框二"""
        self.groupBox1_2 = QGroupBox(self.groupBox1)
        self.groupBox1_2.setTitle("二 参数设置")
        self.groupBox1_2.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.grid_layout2 = QGridLayout(self.groupBox1_2)
        self.button4 = QLabel(self.groupBox1_2)
        self.button4.setText("驱动电压设置/V:")
        self.button4.setStyleSheet(label_button_style)
        self.button4.setAlignment(Qt.AlignCenter)  # 文字居中显示
        self.lineEdit1 = QLineEdit(self.groupBox1_2)
        self.button5= QLabel(self.groupBox1_2)
        self.button5.setText("驱动模式设置AC|DC:")
        self.button5.setStyleSheet(label_button_style)
        self.button5.setAlignment(Qt.AlignCenter)  # 文字居中显示
        self.lineEdit2 = QLineEdit(self.groupBox1_2)
        self.button6= QLabel(self.groupBox1_2)
        self.button6.setText("测试驱动时间设置1:")
        self.button6.setStyleSheet(label_button_style)
        self.button6.setAlignment(Qt.AlignCenter)  # 文字居中显示
        self.lineEdit3_1 = QLineEdit(self.groupBox1_2)
        self.button7= QLabel(self.groupBox1_2)
        self.button7.setText("测试驱动时间设置2:")
        self.button7.setStyleSheet(label_button_style)
        self.button7.setAlignment(Qt.AlignCenter)  # 文字居中显示
        self.lineEdit3_2 = QLineEdit(self.groupBox1_2)
        self.grid_layout2.addWidget(self.button4,0,0,1,3)
        self.grid_layout2.addWidget(self.lineEdit1, 0, 4, 1, 3)
        self.grid_layout2.addWidget(self.button5, 1, 0, 1, 3)
        self.grid_layout2.addWidget(self.lineEdit2, 1, 4, 1, 3)
        self.grid_layout2.addWidget(self.button6, 2, 0, 1, 3)
        self.grid_layout2.addWidget(self.lineEdit3_1, 2, 4, 1, 3)
        self.grid_layout2.addWidget(self.button7, 3, 0, 1, 3)
        self.grid_layout2.addWidget(self.lineEdit3_2, 3, 4, 1, 3)
        """分组框三"""
        self.groupBox1_3 = QGroupBox(self.groupBox1)
        self.groupBox1_3.setTitle("三 日志信息")
        self.groupBox1_3.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.layout_V_Left_V3 = QVBoxLayout(self.groupBox1_3)
        self.log_information = QTextBrowser(self.groupBox1_3)
        self.layout_V_Left_V3.addWidget(self.log_information)
        """分组框四"""
        self.groupBox1_4 = QGroupBox(self.groupBox1)
        self.groupBox1_4.setTitle("四 串口数据信息")
        self.groupBox1_4.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                                QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.layout_V_Left_V4 = QHBoxLayout(self.groupBox1_4)

        self.serial_information = QTextBrowser(self.groupBox1_4)
        self.layout_V_Left_V4.addWidget(self.serial_information)

        self.layout_V_Left.addWidget(self.groupBox1_1)
        self.layout_V_Left.addWidget(self.groupBox1_2)
        self.layout_V_Left.addWidget(self.groupBox1_3)
        self.layout_V_Left.addWidget(self.groupBox1_4)
        self.layout_V_Left.setStretch(0, 1)
        self.layout_V_Left.setStretch(1, 1)
        self.layout_V_Left.setStretch(2, 1)
        self.layout_V_Left.setStretch(3, 1)
        """
        中间部分 
        """
        """上侧"""
        self.groupBox2 = QGroupBox(self.centralwidget)
        self.groupBox2.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.layout_V_Middle_V1 = QVBoxLayout(self.groupBox2)
        self.graphicsView1 = QGraphicsView(self.groupBox2)
        self.graphicsView1.setRenderHint(QPainter.Antialiasing, False)
        self.graphicsView1.setRenderHint(QPainter.SmoothPixmapTransform)
        self.layout_V_Middle_V1.addWidget(self.graphicsView1)
        """下侧"""
        self.groupBox3 = QGroupBox(self.centralwidget)
        self.groupBox3.setStyleSheet("""QGroupBox {border: 1px solid;border-radius: 15px;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.layout_V_Middle_V2 = QVBoxLayout(self.groupBox3)
        self.tabWidget = QTabWidget(self.groupBox3)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setElideMode(Qt.ElideRight)
        self.tabWidget.setUsesScrollButtons(False)

        self.tab1 = QWidget(self.tabWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tab1.sizePolicy().hasHeightForWidth())

        self.button_container = QFrame(self.tab1)
        self.button_container.setStyleSheet("QFrame { background-color: #808080; }")  # 更深的灰色背景
        self.grid_layout3 = QGridLayout(self.button_container)
        self.grid_layout3.setContentsMargins(10, 10, 10, 10)  # 设置内边距

        square_button_style = "QPushButton { background-color: white; border: 1px solid #ddd; border-radius: 10px; min-width: 80px; min-height: 80px; max-width: 100px; max-height: 100px; padding: 0px;} QPushButton::pressed { background-color: #e6e6e6; }"
        icon_size = QSize(100, 100)  # 图标大小，填满按钮框
        
        self.button_up = QPushButton(self.button_container)
        self.button_up.setSizePolicy(sizePolicy)
        self.button_up.setIcon(QIcon(get_resource_path("icon/up1.png")))
        self.button_up.setIconSize(icon_size)
        self.button_up.setStyleSheet(square_button_style)
        self.button_up.setShortcut(Qt.Key_Up)
        self.button_down = QPushButton(self.button_container)
        self.button_down.setSizePolicy(sizePolicy)
        self.button_down.setIcon(QIcon(get_resource_path("icon/down1.png")))
        self.button_down.setIconSize(icon_size)
        self.button_down.setStyleSheet(square_button_style)
        self.button_down.setShortcut(Qt.Key_Down)
        self.button_left = QPushButton(self.button_container)
        self.button_left.setSizePolicy(sizePolicy)
        self.button_left.setIcon(QIcon(get_resource_path("icon/left1.png")))
        self.button_left.setIconSize(icon_size)
        self.button_left.setStyleSheet(square_button_style)
        self.button_left.setShortcut(Qt.Key_Left)
        self.button_right = QPushButton(self.button_container)
        self.button_right.setSizePolicy(sizePolicy)
        self.button_right.setIcon(QIcon(get_resource_path("icon/right1.png")))
        self.button_right.setIconSize(icon_size)
        self.button_right.setStyleSheet(square_button_style)
        self.button_right.setShortcut(Qt.Key_Right)
        self.button_zoomout = QPushButton(self.button_container)
        self.button_zoomout.setSizePolicy(sizePolicy)
        self.button_zoomout.setIcon(QIcon(get_resource_path("icon/zoomout.png")))
        self.button_zoomout.setIconSize(icon_size)
        self.button_zoomout.setStyleSheet(square_button_style)
        self.button_zoomout.setShortcut(QKeySequence("Shift+-"))  # 快捷键：Shift+减号
        self.button_zoomin = QPushButton(self.button_container)
        self.button_zoomin.setSizePolicy(sizePolicy)
        self.button_zoomin.setIcon(QIcon(get_resource_path("icon/zoomin.png")))
        self.button_zoomin.setIconSize(icon_size)
        self.button_zoomin.setStyleSheet(square_button_style)
        self.button_zoomin.setShortcut(QKeySequence("Shift+="))  # 快捷键：Shift+等号（即加号键）
        
        # 调整布局，使6个按钮分布美观：十字形状+两侧缩放按钮
        # 布局：5列，上下左右形成十字，缩放按钮在下方两侧
        self.grid_layout3.addWidget(self.button_up, 0, 2, 1, 1)    # 上，居中
        self.grid_layout3.addWidget(self.button_left, 1, 1, 1, 1)  # 左
        self.grid_layout3.addWidget(self.button_right, 1, 3, 1, 1) # 右
        self.grid_layout3.addWidget(self.button_down, 2, 2, 1, 1)  # 下，居中
        self.grid_layout3.addWidget(self.button_zoomout, 3, 0, 1, 1) # 缩小，左下
        self.grid_layout3.addWidget(self.button_zoomin, 3, 4, 1, 1)  # 放大，右下

        # 将按钮容器添加到tab1的布局中
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.setContentsMargins(0, 0, 0, 0)
        tab1_layout.addWidget(self.button_container)

        self.tab2 = QWidget(self.tabWidget)
        self.layout_V_Middle_V3 = QVBoxLayout(self.tab2)
        self.tab2_tab = QTableWidget(self.tab2)
        self.tab2_tab.verticalHeader().setVisible(True)
        self.tab2_tab.setAutoFillBackground(False)
        self.tab2_tab.setLocale(QLocale(QLocale.Chinese, QLocale.China))
        self.tab2_tab.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.tab2_tab.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.tab2_tab.setDragEnabled(True)
        self.tab2_tab.setDragDropOverwriteMode(False)
        self.tab2_tab.setDragDropMode(QAbstractItemView.DragDrop)
        self.tab2_tab.setDefaultDropAction(Qt.CopyAction)
        self.tab2_tab.setAlternatingRowColors(True)
        self.tab2_tab.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tab2_tab.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab2_tab.setTextElideMode(Qt.ElideMiddle)
        self.tab2_tab.setStyleSheet("""
            QHeaderView::section {border: 1px solid black;}
            QTableWidget::item:selected {background-color: #a6d5ff;}
        """)

        self.tab2_tab.setColumnCount(3)
        self.tab2_tab.setRowCount(0)
        self.tab2_tab.setHorizontalHeaderLabels(["帧", "驱动时间(S)", "开启摄像头"])

        self.tab2_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        header = self.tab2_tab.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.tab2_tab.verticalHeader().setDefaultSectionSize(24)
        self.tab2_tab.verticalHeader().setSortIndicatorShown(False)
        self.tab2_tab.verticalHeader().setStretchLastSection(False)

        self.layout_V_Middle_V3_H1 = QHBoxLayout()
        self.button_add = QPushButton(self.tab2)
        self.button_add.setText("增加")
        self.button_add.setStyleSheet(button_style)
        self.button_del = QPushButton(self.tab2)
        self.button_del.setText("删减")
        self.button_del.setStyleSheet(button_style)
        self.button_sta = QPushButton(self.tab2)
        self.button_sta.setText("开始")
        self.button_sta.setStyleSheet(button_style)
        self.button_end = QPushButton(self.tab2)
        self.button_end.setText("结束")
        self.button_end.setStyleSheet(button_style)
        self.button_save_data=QPushButton(self.tab2)
        self.button_save_data.setText("保存")
        self.button_save_data.setStyleSheet(button_style)
        self.button_load_data = QPushButton(self.tab2)
        self.button_load_data.setText("加载")
        self.button_load_data.setStyleSheet(button_style)
        self.layout_V_Middle_V3_H1.addWidget(self.button_add)
        self.layout_V_Middle_V3_H1.addWidget(self.button_del)
        self.layout_V_Middle_V3_H1.addWidget(self.button_sta)
        self.layout_V_Middle_V3_H1.addWidget(self.button_end)
        self.layout_V_Middle_V3_H1.addWidget(self.button_save_data)
        self.layout_V_Middle_V3_H1.addWidget(self.button_load_data)
        self.layout_V_Middle_V3.addWidget(self.tab2_tab)
        self.layout_V_Middle_V3.addLayout(self.layout_V_Middle_V3_H1)
        self.layout_V_Middle_V3.setStretch(0, 10)
        self.layout_V_Middle_V3.setStretch(1, 1)

        self.tab3 = QWidget(self.tabWidget)
        self.layout_droplet = QVBoxLayout(self.tab3)

        self.droplet_plot_widget = PlotWidget(self.tab3)
        self.droplet_plot_widget.setBackground("w")
        self.droplet_plot_widget.setLabel("bottom", "电极位置")
        self.droplet_plot_widget.setLabel("left", "检测概率")

        plot_item = self.droplet_plot_widget.getPlotItem()
        bottom_axis = plot_item.getAxis("bottom")
        left_axis = plot_item.getAxis("left")
        axis_pen = pg.mkPen(color="black", width=2)
        bottom_axis.setPen(axis_pen)
        left_axis.setPen(axis_pen)
        left_ticks = [[(i / 10.0, f"{i / 10.0:.1f}") for i in range(0, 11)]]
        left_axis.setTicks(left_ticks)
        bottom_ticks = [(i, str(i)) for i in range(0, 121, 10)]
        bottom_axis.setTicks([bottom_ticks])

        view_box = plot_item.getViewBox()
        view_box.setMouseEnabled(x=False, y=False)
        plot_item.hideButtons()
        view_box.setRange(xRange=(0, 121), yRange=(0, 1), padding=0.0)
        self.droplet_x = list(range(0, 121))
        self.droplet_y = [0] *121
        self.droplet_segment_count = 0
        self.droplet_curve = self.droplet_plot_widget.plot(
            self.droplet_x,
            self.droplet_y,
            pen=pg.mkPen(color="black", width=3),
            name="液滴检测",
        )
        self.droplet_text_items=[]
        self.button_detect_droplet = QPushButton(self.tab3)
        self.button_detect_droplet.setText("液滴位置检测")
        # 按钮长度变小并居中显示
        self.button_detect_droplet.setStyleSheet("QPushButton { background-color: white; max-width: 150px;} QPushButton::pressed { background-color: #e6e6e6; }")
        self.layout_droplet_buttons = QHBoxLayout()
        self.layout_droplet_buttons.addStretch()  # 添加弹性空间，使按钮居中
        self.layout_droplet_buttons.addWidget(self.button_detect_droplet)
        self.layout_droplet_buttons.addStretch()  # 添加弹性空间，使按钮居中

        self.layout_droplet.addWidget(self.droplet_plot_widget)
        self.layout_droplet.addLayout(self.layout_droplet_buttons)
        self.layout_droplet.setStretch(0, 10)
        self.layout_droplet.setStretch(1, 1)

        self.tabWidget.addTab(self.tab1,"手动操作界面")
        self.tabWidget.addTab(self.tab2,"自动操作界面")
        self.tabWidget.addTab(self.tab3,"液滴位置检测界面")
        self.layout_V_Middle_V2.addWidget(self.tabWidget)

        self.layout_V_Middle.addWidget(self.groupBox2)
        self.layout_V_Middle.addWidget(self.groupBox3)
        self.layout_V_Middle.setStretch(0, 1)
        self.layout_V_Middle.setStretch(1, 1)
        """
        右边部分
        """
        self.groupBox4 = QGroupBox(self.centralwidget)
        self.groupBox4.setStyleSheet("""QGroupBox {border: 1px solid;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.groupBox4.setTitle("摄像头采集窗口（双击放大）")
        self.layout_V_Right_V1 = QVBoxLayout(self.groupBox4)
        self.layout_V_Right_V1.setContentsMargins(0, 0, 0, 0)
        self.layout_V_Right_V1.setSpacing(0)
        
        # 摄像头图像显示区域
        self.label_cam_view = QLabel(self.groupBox4)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_cam_view.sizePolicy().hasHeightForWidth())
        self.label_cam_view.setSizePolicy(sizePolicy)
        self.label_cam_view.setFrameShape(QFrame.WinPanel)
        self.label_cam_view.setAlignment(Qt.AlignCenter)
        # CAM字体加大加粗
        cam_font = QFont()
        cam_font.setPointSize(24)  # 增大字号
        cam_font.setBold(True)     # 加粗
        self.label_cam_view.setFont(cam_font)
        self.label_cam_view.setText("CAM")
        self.label_cam_view.setObjectName("label_cam_view")
        
        # 按钮区域
        self.layout_V_Right_V1_H1 = QHBoxLayout()
        self.layout_V_Right_V1_H1.setSpacing(0)
        self.layout_V_Right_V1_H1.setObjectName("horizontalLayout_cam")

        self.button_open_camera = QPushButton(self.groupBox4)
        self.button_open_camera.setText("打开摄像头")
        self.button_open_camera.setStyleSheet(button_style)
        self.button_open_camera.setObjectName("button_open_camera")
        
        self.button_close_camera = QPushButton(self.groupBox4)
        self.button_close_camera.setText("关闭摄像头")
        self.button_close_camera.setStyleSheet(button_style)
        self.button_close_camera.setObjectName("button_close_camera")
        
        self.button_take_picture = QPushButton(self.groupBox4)
        self.button_take_picture.setText("拍照")
        self.button_take_picture.setStyleSheet(button_style)
        self.button_take_picture.setObjectName("button_take_picture")

        self.button_record_picture = QPushButton(self.groupBox4)
        self.button_record_picture.setText("录像")
        self.button_record_picture.setStyleSheet(button_style)
        self.button_record_picture.setObjectName("button_take_record")
        
        self.layout_V_Right_V1_H1.addWidget(self.button_open_camera)
        self.layout_V_Right_V1_H1.addWidget(self.button_close_camera)
        self.layout_V_Right_V1_H1.addWidget(self.button_take_picture)
        self.layout_V_Right_V1_H1.addWidget(self.button_record_picture)
        
        # 添加到主布局
        self.layout_V_Right_V1.addWidget(self.label_cam_view)
        self.layout_V_Right_V1.addLayout(self.layout_V_Right_V1_H1)
        self.layout_V_Right_V1.setStretch(0, 15)  # 图像区域占据更多空间
        self.layout_V_Right_V1.setStretch(1, 1)   # 按钮区域占较少空间

        self.groupBox5 = QGroupBox(self.centralwidget)
        self.groupBox5.setStyleSheet("""QGroupBox {border: 1px solid;margin-top: 1.5ex;padding: 10px;}
                                        QGroupBox::title {subcontrol-origin: margin;subcontrol-position: top center;padding: 0 5px;}""")
        self.groupBox5.setTitle("温度/荧光监测窗口")
        self.layout_V_Right_V2 = QVBoxLayout(self.groupBox5)
        self.tabWidget2 = QTabWidget(self.groupBox5)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget2.setSizePolicy(sizePolicy)
        self.tabWidget2.setAutoFillBackground(False)
        self.tabWidget2.setMovable(False)
        self.tabWidget2.setTabShape(QTabWidget.Rounded)
        self.tabWidget2.setElideMode(Qt.ElideRight)
        self.tabWidget2.setUsesScrollButtons(False)

        # PID参数输入框边框加黑样式
        pid_edit_style = "QLineEdit { border: 2px solid #000000; }"
        self._build_temperature_tab(1, pid_edit_style, button_style)
        self._build_temperature_tab(2, pid_edit_style, button_style)
        self._build_temperature_tab(3, pid_edit_style, button_style)

        # 荧光读取 Tab（布局与温度通道一致：曲线在上，控件在下；共用左侧系统串口）
        self.tab_fluor = QWidget(self.tabWidget2)
        self.layout_fluor_main = QVBoxLayout(self.tab_fluor)

        self.fluorescence_widget = PlotWidget(self.tab_fluor)
        self.fluorescence_widget.setBackground("w")
        self.fluorescence_widget.setTitle("荧光曲线（双击放大）", color='#333')
        self.fluorescence_widget.setLabel("bottom", "时间 (s)")
        plot_item_fluor = self.fluorescence_widget.getPlotItem()
        fluor_axis = plot_item_fluor.getAxis("left")
        fluor_axis.setPen(pg.mkPen(color=(128, 0, 128), width=1))
        fluor_axis.setTextPen(pg.mkPen(color=(128, 0, 128)))
        fluor_axis.setLabel("荧光强度", color=(128, 0, 128))
        self.fluorescence_widget.showGrid(x=True, y=True, alpha=0.15)
        plot_item_fluor.getViewBox().setAutoPan(y=True)
        plot_item_fluor.enableAutoRange(axis='y', enable=True)
        plot_item_fluor.enableAutoRange(axis='x', enable=True)
        plot_item_fluor.getViewBox().setLimits(xMin=0)
        plot_item_fluor.getViewBox().setMouseEnabled(x=False, y=True)
        self.fluorescence_curve = self.fluorescence_widget.plot(
            [], [], pen=pg.mkPen(color=(128, 0, 128), width=2), name="荧光"
        )

        self.layout_fluor_H1 = QHBoxLayout()
        self.layout_fluor_H1.setSpacing(2)
        self.layout_fluor_H1.setContentsMargins(0, 0, 0, 0)
        fluor_value_style = "QLineEdit { border: 2px solid #000000; padding: 0 4px; }"
        fluor_ctrl_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button_fluor_method1 = QPushButton(self.tab_fluor)
        self.button_fluor_method1.setText("开始①")
        self.button_fluor_method1.setStyleSheet(button_style)
        self.lineEdit_fluor_excitation = QLineEdit(self.tab_fluor)
        self.lineEdit_fluor_excitation.setPlaceholderText("激发时间")
        self.lineEdit_fluor_excitation.setText("20")
        self.lineEdit_fluor_excitation.setAlignment(Qt.AlignCenter)
        self.lineEdit_fluor_excitation.setStyleSheet(fluor_value_style)
        self.button_fluor_method2 = QPushButton(self.tab_fluor)
        self.button_fluor_method2.setText("开始②")
        self.button_fluor_method2.setStyleSheet(button_style)
        self.lineEdit_fluor_interval = QLineEdit(self.tab_fluor)
        self.lineEdit_fluor_interval.setPlaceholderText("间隔时间")
        self.lineEdit_fluor_interval.setText("500")
        self.lineEdit_fluor_interval.setAlignment(Qt.AlignCenter)
        self.lineEdit_fluor_interval.setStyleSheet(fluor_value_style)
        self.button_fluor_led = QPushButton(self.tab_fluor)
        self.button_fluor_led.setText("打开LED")
        self.button_fluor_led.setStyleSheet(button_style)
        self.button_fluor_save = QPushButton(self.tab_fluor)
        self.button_fluor_save.setText("保存")
        self.button_fluor_save.setStyleSheet(button_style)
        self.button_fluor_load = QPushButton(self.tab_fluor)
        self.button_fluor_load.setText("加载")
        self.button_fluor_load.setStyleSheet(button_style)
        self.button_fluor_clear = QPushButton(self.tab_fluor)
        self.button_fluor_clear.setText("清除")
        self.button_fluor_clear.setStyleSheet(button_style)
        for ctrl, stretch in (
            (self.button_fluor_method1, 1),
            (self.lineEdit_fluor_excitation, 2),
            (self.button_fluor_method2, 1),
            (self.lineEdit_fluor_interval, 2),
            (self.button_fluor_led, 1),
            (self.button_fluor_save, 1),
            (self.button_fluor_load, 1),
            (self.button_fluor_clear, 1),
        ):
            ctrl.setSizePolicy(fluor_ctrl_policy)
            ctrl.setMaximumHeight(20)
            self.layout_fluor_H1.addWidget(ctrl, stretch)

        self.layout_fluor_main.setSpacing(0)
        self.layout_fluor_main.setContentsMargins(0, 0, 0, 0)
        self.layout_fluor_main.addWidget(self.fluorescence_widget)
        self.layout_fluor_main.addLayout(self.layout_fluor_H1)
        self.layout_fluor_main.setStretch(0, 1)
        self.layout_fluor_main.setStretch(1, 0)

        self.tab_fluor.setLayout(self.layout_fluor_main)
        self.tabWidget2.addTab(self.tab_tem1,'温度曲线绘制通道一')
        self.tabWidget2.addTab(self.tab_tem2,'温度曲线绘制通道二')
        self.tabWidget2.addTab(self.tab_tem3, '温度曲线绘制通道三')
        self.tabWidget2.addTab(self.tab_fluor, '荧光读取')
        self.layout_V_Right_V2.addWidget(self.tabWidget2)
        self.layout_V_Right.addWidget(self.groupBox4)
        self.layout_V_Right.addWidget(self.groupBox5)
        self.layout_V_Right.setStretch(0, 5)
        self.layout_V_Right.setStretch(1, 5)
        """
        总体
        """
        self.layout_H.addWidget(self.groupBox1)
        self.layout_H.addLayout(self.layout_V_Middle)
        self.layout_H.addLayout(self.layout_V_Right)
        self.layout_H.setStretch(0,1)
        self.layout_H.setStretch(1,3)
        self.layout_H.setStretch(2,3)
        MainWindow.setCentralWidget(self.centralwidget)
        QMetaObject.connectSlotsByName(MainWindow)