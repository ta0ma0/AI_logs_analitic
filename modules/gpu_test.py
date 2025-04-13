import logging
import datetime
import subprocess
from datetime import datetime

def check_gpu():
    MAX = 8
    MIN = 4
    try:
        vmachine_marker = subprocess.run(['VBoxManage', 'list', 'runningvms'], capture_output=True, text=True, check=True)
        logging.info(f"Вывод VBoxManage: '{vmachine_marker.stdout}'")
        logging.info(f"Длина вывода VBoxManage: {len(vmachine_marker.stdout)}")
        if len(vmachine_marker.stdout) == 0:
            return MAX
        else:
            return MIN
    except FileNotFoundError:
        logging.error("Команда VBoxManage не найдена. Убедитесь, что она установлена и добавлена в PATH.")
        return MAX  # Или другое значение по умолчанию
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка выполнения VBoxManage: {e}")
        logging.error(f"stderr: {e.stderr}")
        return MIN  # Или другое значение по умолчанию

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logging.info("Logging was setup")
n_gpu_layers = check_gpu()
logging.info(f"Setup n_gpu_layers = {n_gpu_layers}")