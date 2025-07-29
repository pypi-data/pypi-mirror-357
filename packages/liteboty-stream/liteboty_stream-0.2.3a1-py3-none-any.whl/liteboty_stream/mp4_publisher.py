import cv2
import time
import redis
import threading

from pathlib import Path
from io import BytesIO
from PIL import Image
from liteboty.core.message import Message, MessageType


class MP4Publisher:
    def __init__(self, mp4_file, broker, channel, fps=None, target_width=640, target_height=480):
        self.mp4_file = Path(mp4_file)
        self.broker = broker
        self.channel = channel

        # 目标分辨率（默认设为640x480以匹配SegService）
        self.target_width = target_width
        self.target_height = target_height

        # 初始化 Redis 客户端
        host, port = broker.split(":")
        self.redis_client = redis.Redis(host=host, port=int(port))

        # 打开视频文件
        self.cap = cv2.VideoCapture(str(self.mp4_file))
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.mp4_file}")

        # 获取视频属性
        self.original_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        # 如果指定了 fps，则使用指定的，否则使用视频的原始 fps
        self.fps = fps if fps else self.video_fps
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 发布控制
        self.running = False
        self.thread = None
        self.frame_counter = 0

    def start(self):
        """开始发布视频帧"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._publish_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """停止发布视频帧"""
        self.running = False
        if self.thread:
            self.thread.join()

        # 释放视频资源
        if self.cap and self.cap.isOpened():
            self.cap.release()

    def _publish_loop(self):
        """发布视频帧循环"""
        try:
            while self.running:
                start_time = time.time()

                # 读取下一帧
                ret, frame = self.cap.read()
                if not ret:
                    # 视频结束，循环播放
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.frame_counter = 0
                    continue

                # 调整帧大小为目标尺寸
                if frame.shape[1] != self.target_width or frame.shape[0] != self.target_height:
                    frame = cv2.resize(frame, (self.target_width, self.target_height))

                # 将 OpenCV BGR 格式转换为 JPEG
                ret, jpeg_data = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                binary_frame = jpeg_data.tobytes()

                # 准备元数据
                metadata = {
                    'frame_id': self.frame_counter,
                    'image_width': self.target_width,
                    'image_height': self.target_height,
                    'time_stamp': time.time(),
                    'source': f'mp4_file:{self.mp4_file.name}'
                }

                # 创建消息并发布
                message = Message(binary_frame, MessageType.IMAGE, metadata)
                encoded_message = Message.encode(message)
                self.redis_client.publish(self.channel, encoded_message)

                self.frame_counter += 1

                # 控制帧率
                elapsed = time.time() - start_time
                sleep_time = max(0, 1.0 / self.fps - elapsed)
                time.sleep(sleep_time)

        except Exception as e:
            print(f"视频发布错误: {e}")
        finally:
            # 确保资源被释放
            if self.cap and self.cap.isOpened():
                self.cap.release()
