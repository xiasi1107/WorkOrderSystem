import requests
import yaml
from typing import List, Dict
from src.db_handler import DatabaseHandler

class RobotNotifier:
    def __init__(self, config_path: str = "config/wechat_robots.yaml"):
        # 加载机器人配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.robots = config.get("robots", {})  # 确保是字典：{群名: webhook}
        self.app_url = config.get("app_url", "")
        self.db_handler = DatabaseHandler()

    def _format_message(self, workorders: List[Dict]) -> str:
        """格式化待处理工单消息（纯中文+基础格式，避免乱码）"""
        if not workorders:
            return "⚠️ 当前暂无待处理工单"

        msg = "### 📢 最新待处理工单\n\n"
        for idx, order in enumerate(workorders, 1):
            # 只保留必要字段，避免特殊字符
            msg += f"{idx}. **{order['title']}**\n"
            msg += f"   - 状态：{order['status']}\n"
            msg += f"   - 创建时间：{order['create_time']}\n"
            msg += f"   - 处理人：{order['handler'] or '未分配'}\n\n"
        return msg

    def _send_markdown(self, webhook: str, content: str):
        """发送消息（与测试命令保持一致的格式）"""
        try:
            # 1. 构建与测试命令完全一致的 JSON 结构
            data = {
                "msgtype": "markdown",
                "markdown": {"content": content}
            }
            # 2. 头部与测试命令一致
            headers = {"Content-Type": "application/json; charset=utf-8"}
            # 3. 发送请求（用 json 参数自动序列化，确保 UTF-8 编码）
            response = requests.post(
                url=webhook,
                json=data,
                headers=headers,
                timeout=10
            )
            # 4. 打印响应（方便调试）
            print(f"发送响应：{response.text}")
            return response.json()
        except Exception as e:
            print(f"发送失败：{str(e)}")
            return None

    def send_to_all_groups(self):
        """向所有群聊发送工单通知"""
        print("当前配置的群聊机器人：", self.robots)  # 新增打印
        # 1. 获取待处理工单（与测试数据结构一致）
        workorders = self.db_handler.get_workorders_for_notify()
        print(f"待发送的工单数据：{workorders}")  # 确认有数据

        # 2. 格式化消息（与测试消息格式一致）
        message = self._format_message(workorders)
        print(f"待发送的消息内容：{message}")  # 确认内容无乱码

        # 3. 向所有群聊发送
        for group_name, webhook in self.robots.items():
            print(f"向 {group_name} 发送消息...")
            self._send_markdown(webhook, message)

if __name__ == "__main__":
    notifier = RobotNotifier()
    notifier.send_to_all_groups()