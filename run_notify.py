import logging
from pathlib import Path
from src.robot_notifier import RobotNotifier

# 初始化日志目录
Path("logs").mkdir(exist_ok=True)

if __name__ == "__main__":
    # 发送工单通知到所有群聊
    notifier = RobotNotifier()
    notifier.send_to_all_groups()