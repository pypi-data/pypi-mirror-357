from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtGui import QImage, QPixmap
from .redis_subscriber import RedisSubscriber


class ImageDisplayThread(QThread):
    new_image_signal = Signal(QImage)

    def __init__(self, redis_subscriber):
        super().__init__()
        self.redis_subscriber = redis_subscriber

    def run(self):
        for img in self.redis_subscriber.listen():
            qimage = self.convert_to_qimage(img)
            self.new_image_signal.emit(qimage)

    @staticmethod
    def convert_to_qimage(img):
        img = img.convert("RGB")
        width, height = img.size
        bytes_per_line = 3 * width
        img_data = img.tobytes("raw", "RGB")
        return QImage(img_data, width, height, bytes_per_line, QImage.Format_RGB888)


class MainWindow(QWidget):
    def __init__(self, broker, channel, decode_format):
        super().__init__()

        self.setWindowTitle("Liteboty Stream")
        self.setGeometry(100, 100, 640, 480)  # Default window size set to 640x480
        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.layout.addWidget(self.image_label)

        # 添加刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.restart_stream)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)

        self.broker = broker  # 保存 broker
        self.channel = channel  # 保存 channel
        self.decode_format = decode_format  # 保存 decode_format
        self.start_stream()

    def start_stream(self):
        # Initialize RedisSubscriber
        redis_subscriber = RedisSubscriber(self.broker, self.channel, self.decode_format)
        self.image_thread = ImageDisplayThread(redis_subscriber)
        self.image_thread.new_image_signal.connect(self.display_image)
        self.image_thread.start()

    def restart_stream(self):
        # 停止旧的线程
        if hasattr(self, 'image_thread') and self.image_thread.isRunning():
            self.image_thread.terminate()
            self.image_thread.wait()

        # 重新启动流
        self.start_stream()

    def display_image(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        self.update_image(pixmap)

    def update_image(self, pixmap):
        # Scale the image to fit the window, keeping aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        # 获取图像的尺寸
        pixmap = self.image_label.pixmap()
        if pixmap:
            image_size = pixmap.size()

            # 根据图像大小动态设置窗口的最小尺寸
            self.setMinimumSize(image_size.width(), image_size.height())
            self.update_image(pixmap)  # 更新图像大小以适应窗口
        super().resizeEvent(event)