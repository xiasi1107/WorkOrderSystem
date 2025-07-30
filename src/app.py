import yaml
import logging
from flask import Flask, render_template, redirect
from src.db_handler import DatabaseHandler

app = Flask(__name__)
# 加载应用配置
with open("config/app_config.yaml", "r", encoding="utf-8") as f:
    app_config = yaml.safe_load(f)

# 初始化数据库连接
db_handler = DatabaseHandler()

# 配置日志
def init_app_logger():
    logger = logging.getLogger("workorder_app")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("logs/app.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

init_app_logger()

@app.route("/")
def index():
    return redirect("/workorders")  # 访问根路径时自动跳转到工单页面

@app.route("/health")  # 用于企业微信后台验证服务器可用性
def health_check():
    return "OK", 200

@app.route("/workorders")
def show_workorders():
    workorders = db_handler.get_workorders_for_notify()
    # 打印数据，看看是不是期望的内容
    print("要传递给模板的数据：", workorders)
    return render_template("workorders.html", workorders=workorders)