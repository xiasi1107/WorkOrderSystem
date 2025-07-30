from src.app import app, app_config

if __name__ == "__main__":
    # 启动Flask服务（生产环境建议用Gunicorn等部署）
    app.run(
        host="0.0.0.0",  # 允许外部访问
        port=app_config["server_port"],
        debug=False  # 生产环境设为False
    )