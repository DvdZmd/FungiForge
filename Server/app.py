from app_factory import create_app
from logs.sensor_logger import start_sensor_logger

app = create_app()
start_sensor_logger(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
