import yaml
import logging
from typing import List, Dict
import mysql.connector

class DatabaseHandler:
    def __init__(self, config_path: str = "config/database.yaml"):
        # 加载配置
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.fields = self.config["fields"]  # 字段映射：{数据库字段: 显示名}
        self._init_logger()

    def _init_logger(self):
        self.logger = logging.getLogger("db_handler")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler("logs/db_operation.log")
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _get_db_connection(self):
        """创建数据库连接（根据类型适配）"""
        if self.config["db_type"] == "mysql":
            return mysql.connector.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=self.config["password"],
                database=self.config["database"]
            )
        else:
            raise ValueError(f"不支持的数据库类型：{self.config['db_type']}")

    def get_workorders_for_notify(self) -> List[Dict]:
        """获取需要推送到群的工单（如待处理工单）"""
        query = """
                SELECT id, title, content, status, create_time, handler 
                FROM workorders 
                WHERE status = '待处理'  -- 直接写条件，避免依赖配置
                ORDER BY create_time DESC
    """
        return self._query_data(query)


    def get_all_workorders(self) -> List[Dict]:
        """获取所有工单（供自建应用展示）"""
        query = """
                SELECT id, title, content, status, create_time, handler 
                FROM workorders 
                ORDER BY create_time DESC
        """
        return self._query_data(query)

    def _query_data(self, query: str) -> List[Dict]:
        """执行查询并返回格式化数据"""
        data = []
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)  # 以字典形式返回（含字段名）
            cursor.execute(query)
            data = cursor.fetchall()  # 原始数据：[{db_field: value}, ...]

            cursor.close()
            conn.close()
            self.logger.info(f"查询成功，返回{len(data)}条数据")
        except Exception as e:
            self.logger.error(f"数据库操作失败：{str(e)}")
        return data