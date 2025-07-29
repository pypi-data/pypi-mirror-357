from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QToolBar,
    QDialog, QVBoxLayout, QLineEdit,
    QPushButton, QFormLayout, QFileDialog,
    QHBoxLayout, QLabel, QSpinBox
)
from PySide6.QtGui import QAction
from .liteboty_stream import MainWindow
from .mp4_publisher import MP4Publisher
from pathlib import Path


class NewStreamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新的视频流")

        layout = QFormLayout()

        self.broker = QLineEdit()
        self.broker.setText("10.8.2.2:6379")
        self.broker.setPlaceholderText("例如: 10.8.2.2:6379")
        layout.addRow("Redis地址:", self.broker)

        self.channel = QLineEdit()
        self.channel.setText("/video/raw")
        self.channel.setPlaceholderText("例如: /video/raw")
        layout.addRow("订阅频道:", self.channel)

        self.decode = QLineEdit()
        self.decode.setText("RGB")
        layout.addRow("解码格式:", self.decode)

        buttons = QVBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow("", buttons)

        self.setLayout(layout)


class NewSimulationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建仿真视频流")
        self.mp4_file = ""

        layout = QFormLayout()

        # Redis 配置
        self.broker = QLineEdit()
        self.broker.setText("10.8.2.2:6379")
        self.broker.setPlaceholderText("例如: 10.8.2.2:6379")
        layout.addRow("Redis地址:", self.broker)

        self.channel = QLineEdit()
        self.channel.setText("/video/simulation")
        self.channel.setPlaceholderText("例如: /video/simulation")
        layout.addRow("发布频道:", self.channel)

        # MP4 文件选择
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("选择 MP4 视频文件")
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_button)
        layout.addRow("视频文件:", file_layout)

        # 添加分辨率提示
        resolution_label = QLabel("视频将被调整为 640x480 分辨率")
        resolution_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addRow("", resolution_label)

        # FPS 设置
        fps_layout = QHBoxLayout()
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(25)
        self.fps_spinbox.setSuffix(" fps")
        self.use_original_fps = QPushButton("使用原始帧率")
        self.use_original_fps.clicked.connect(self.set_original_fps)
        fps_layout.addWidget(self.fps_spinbox)
        fps_layout.addWidget(self.use_original_fps)
        layout.addRow("帧率:", fps_layout)

        # 按钮
        buttons = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow("", buttons)

        self.setLayout(layout)
        self.setMinimumWidth(400)

        # 原始视频帧率
        self.original_fps = None

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mkv);;所有文件 (*)"
        )
        if file_path:
            self.mp4_file = file_path
            self.file_path.setText(file_path)

            # 尝试获取原始帧率
            try:
                import cv2
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    self.original_fps = cap.get(cv2.CAP_PROP_FPS)
                    cap.release()
            except Exception as e:
                print(f"无法读取视频帧率: {e}")

    def set_original_fps(self):
        if self.original_fps:
            self.fps_spinbox.setValue(int(self.original_fps))

    def validate_and_accept(self):
        if not self.mp4_file:
            QMessageBox.warning(self, "验证失败", "请选择一个视频文件")
            return

        if not Path(self.mp4_file).exists():
            QMessageBox.warning(self, "验证失败", "选择的视频文件不存在")
            return

        self.accept()


class StreamUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频流监控系统")
        self.setGeometry(100, 100, 1200, 800)

        # 存储活动的发布者
        self.active_publishers = {}

        # 创建MDI区域
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_tool_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        new_stream = QAction("新建视频流", self)
        new_stream.setShortcut("Ctrl+N")
        new_stream.triggered.connect(self.add_new_stream)
        file_menu.addAction(new_stream)

        # 添加新建仿真菜单项
        new_simulation = QAction("新建仿真", self)
        new_simulation.setShortcut("Ctrl+M")
        new_simulation.triggered.connect(self.add_new_simulation)
        file_menu.addAction(new_simulation)

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 窗口菜单
        window_menu = menubar.addMenu("窗口")

        cascade = QAction("层叠排列", self)
        cascade.triggered.connect(self.mdi.cascadeSubWindows)
        window_menu.addAction(cascade)

        tile = QAction("平铺排列", self)
        tile.triggered.connect(self.mdi.tileSubWindows)
        window_menu.addAction(tile)

    def create_tool_bar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        new_stream_btn = QAction("新建视频流", self)
        new_stream_btn.triggered.connect(self.add_new_stream)
        toolbar.addAction(new_stream_btn)

        # 添加新建仿真按钮
        new_simulation_btn = QAction("新建仿真", self)
        new_simulation_btn.triggered.connect(self.add_new_simulation)
        toolbar.addAction(new_simulation_btn)

    def add_new_stream(self):
        dialog = NewStreamDialog(self)
        if dialog.exec() == QDialog.Accepted:
            broker = dialog.broker.text()
            channel = dialog.channel.text()
            decode = dialog.decode.text()

            # 创建新的视频流窗口
            sub_window = MainWindow(broker, channel, decode)
            mdi_window = self.mdi.addSubWindow(sub_window)
            mdi_window.setWindowTitle(f"视频流 - {broker} {channel}")
            mdi_window.show()

    def add_new_simulation(self):
        dialog = NewSimulationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            broker = dialog.broker.text()
            channel = dialog.channel.text()
            mp4_file = dialog.mp4_file
            fps = dialog.fps_spinbox.value()

            try:
                # 创建并启动MP4发布者，明确指定目标尺寸为 640x480
                publisher = MP4Publisher(mp4_file, broker, channel, fps, target_width=640, target_height=480)
                publisher.start()

                # 保存发布者引用，以便关闭窗口时停止
                publisher_id = f"{broker}:{channel}:{mp4_file}"
                self.active_publishers[publisher_id] = publisher

                # 创建新的视频流窗口来查看发布的内容
                sub_window = MainWindow(broker, channel, "RGB")
                mdi_window = self.mdi.addSubWindow(sub_window)

                # 视频文件名
                file_name = Path(mp4_file).name
                mdi_window.setWindowTitle(f"仿真流 - {file_name} ({channel})")

                # 设置关闭事件
                mdi_window.destroyed.connect(lambda: self.stop_publisher(publisher_id))
                mdi_window.show()

            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "错误", f"创建仿真视频流失败: {str(e)}")

    def stop_publisher(self, publisher_id):
        """停止指定的发布者"""
        if publisher_id in self.active_publishers:
            try:
                self.active_publishers[publisher_id].stop()
                del self.active_publishers[publisher_id]
            except Exception as e:
                print(f"停止发布者时出错: {e}")

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        # 停止所有活动的发布者
        for publisher in self.active_publishers.values():
            try:
                publisher.stop()
            except:
                pass
        super().closeEvent(event)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)
    window = StreamUI()
    window.show()
    sys.exit(app.exec())
