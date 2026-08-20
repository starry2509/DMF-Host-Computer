import cv2
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap

CAM_NUMBER = 0
class CAMERA_MODULE:
    def __init__(self, cam_number=CAM_NUMBER, logger=None):
        self.cam_number = cam_number
        self.log = logger
        self.cap = None
    
    def init(self):
        self.cap = cv2.VideoCapture(self.cam_number)
        self.log.debug(False,f'初始化摄像头{self.cam_number}')
    
    def open_cam(self):
        self.init()
        if self.cap.isOpened():
            self.log.debug(True,f'摄像头{self.cam_number}打开成功')
            return True
        else:
            self.log.debug(True,f'摄像头{self.cam_number}打开失败')
            return False
    
    def close_cam(self):
        if self.cap is not None:
            self.cap.release()
            self.log.debug(True,f'摄像头{self.cam_number}释放成功')
    
    def cam_setting(self):
        self.log.debug(False,'配置摄像头中')
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.cam_number)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 500)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
            self.cap.set(cv2.CAP_PROP_FPS, 10)
            # self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 启用自动曝光
            # self.cap.set(cv2.CAP_PROP_EXPOSURE, -1)  # 曝光（负值表示自动曝光）
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 1)  # 亮度 0.0-1.0
    def cam_read(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 水平翻转,很有必要
                frame = cv2.flip(frame, 1)

                # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                # opencv 默认图像格式是rgb qimage要使用BRG,这里进行格式转换,不用这个的话,图像就变色了,困扰了半天,翻了一堆资料
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame = self.image_processer(frame)
                ret = True
            else:
                frame = None
                ret = False
        else:
            frame = None
            ret = False
        return (ret, frame)
    def image_processer(self, frame):
        return frame

    def __del__(self):
        if self.cap is not None:
            self.cap.release()
        self.log.debug(False,'程序退出释放摄像头资源')


class CameraLogic:
    
    def __init__(self, label_view, button_open, button_close, button_take_picture=None, 
                 button_record_picture=None,logger=None, cam_number=0):
        """
        初始化摄像头逻辑控制器
        :param label_view: 显示图像的QLabel控件
        :param button_open: 打开摄像头按钮
        :param button_close: 关闭摄像头按钮
        :param button_take_picture: 拍照按钮（可选）
        :param button_record_picture: 录像按钮（可选）
        :param cam_number: 摄像头编号
        """
        self.label_cam_view = label_view
        self.button_open_camera = button_open
        self.button_close_camera = button_close
        self.button_take_picture = button_take_picture
        self.button_record_picture = button_record_picture
        self.logger = logger
        
        # 创建摄像头模块 - 基于CAM_MODULE.py中的CAMERA_MODULE
        self.camera_module = CAMERA_MODULE(cam_number=cam_number, logger=self.logger)
        self.camera_module.cam_setting()
        
        # 初始化定时器 - 基于LOGIC_CAM.py的方式
        self.timer_camera = QTimer()
        self.timer_camera.timeout.connect(self.show_image)
        
        # 连接按钮信号 - 基于LOGIC_CAM.py
        self.button_open_camera.clicked.connect(self.open_camera)
        self.button_close_camera.clicked.connect(self.close_camera)
        if self.button_take_picture is not None:
            self.button_take_picture.clicked.connect(self.take_picture)
        if self.button_record_picture is not None:
            self.button_record_picture.clicked.connect(self.record_picture)
        
        # 配置显示camera的label - 禁用setScaledContents，我们手动缩放
        self.label_cam_view.setScaledContents(False)
        self.label_cam_view.setAlignment(Qt.AlignCenter)
        
        # 保存label的初始尺寸，用于固定图像显示大小
        self.fixed_label_size = None
        
        # 当前帧缓存（用于拍照）
        self.current_frame = None
        self.current_qimage = None
    
    def open_camera(self):
        if not self.camera_module.open_cam():
            self.label_cam_view.setText('摄像头打开失败')
            return False

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        self.label_cam_view.updateGeometry()
        label_size = self.label_cam_view.size()

        if label_size.width() > 10 and label_size.height() > 10:
            self.fixed_label_size = label_size
        elif self.fixed_label_size is None:
            hint_size = self.label_cam_view.sizeHint()
            if hint_size.width() > 10 and hint_size.height() > 10:
                self.fixed_label_size = hint_size
        
        self.label_cam_view.setText('')
        self.timer_camera.start(40)

        self.button_open_camera.setEnabled(False)
        self.button_close_camera.setEnabled(True)
        if self.button_take_picture is not None:
            self.button_take_picture.setEnabled(True)
        if self.button_record_picture is not None:
            self.button_record_picture.setEnabled(True)
        
        return True
    
    def close_camera(self):
        self.timer_camera.stop()
        self.camera_module.close_cam()
        self.button_open_camera.setEnabled(True)
        self.button_close_camera.setEnabled(False)
        if self.button_take_picture is not None:
            self.button_take_picture.setEnabled(False)
        if self.button_record_picture is not None:
            self.button_record_picture.setEnabled(False)

        self.label_cam_view.setText('CAM')
        self.current_frame = None
        self.current_qimage = None
    
    def show_image(self):
        ret, frame = self.camera_module.cam_read()
        if not ret or frame is None:
            self.label_cam_view.setText('Error:摄像头图像获取失败！')
            self.close_camera()
            return False
        self.current_frame = frame
        frame_2_show = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.current_qimage = frame_2_show

        if self.fixed_label_size is None:
            label_size = self.label_cam_view.size()
            if label_size.width() > 10 and label_size.height() > 10:
                self.fixed_label_size = label_size
            else:
                self.fixed_label_size = self.label_cam_view.sizeHint()

        if self.fixed_label_size is not None and self.fixed_label_size.width() > 10 and self.fixed_label_size.height() > 10:
            target_size = self.fixed_label_size
        else:
            current_size = self.label_cam_view.size()
            if current_size.width() > 10 and current_size.height() > 10:
                target_size = current_size
                if self.fixed_label_size is None:
                    self.fixed_label_size = current_size
            else:
                self.label_cam_view.setPixmap(QPixmap.fromImage(self.current_qimage))
                return

        scaled_pixmap = QPixmap.fromImage(frame_2_show).scaled(
            target_size.width(), 
            target_size.height(), 
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        )
        self.label_cam_view.setPixmap(scaled_pixmap)

    def take_picture(self):
        if self.current_qimage is not None:
            pixmap = QPixmap.fromImage(self.current_qimage)
            pixmap.save('photo.jpg')
            return True
        else:
            return False
    def record_picture(self):
        pass
    
    def cleanup(self):
        if self.timer_camera.isActive():
            self.timer_camera.stop()
        self.close_camera()
        if self.camera_module is not None:
            self.camera_module.__del__()

CameraModule = CAMERA_MODULE
