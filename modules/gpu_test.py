import logging
import subprocess

def check_gpu():
    MAX = 8
    MIN = 4
    try:
        vmachine_marker = subprocess.run(['VBoxManage', 'list', 'runningvms'], capture_output=True, text=True, check=True)
        logging.info(f"VBoxManage stdout: '{vmachine_marker.stdout}'")
        logging.info(f"VBoxManage stderr: '{vmachine_marker.stderr}'")
        logging.info(f"VBoxManage returncode: {vmachine_marker.returncode}")
        if len(vmachine_marker.stdout) == 0:
            return MAX
        else:
            return MIN
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка выполнения VBoxManage: {e}")
        logging.error(f"stderr: {e.stderr}")
        return MIN
    except FileNotFoundError:
        logging.error("Команда VBoxManage не найдена.")
        return MAX
