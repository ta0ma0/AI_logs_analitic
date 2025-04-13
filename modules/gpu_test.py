import logging
import datetime
import subprocess
from datetime import datetime



def check_gpu():
    """
    Модуль который проверят запущена ли на хосте VirtualBox машина.
    Если витуальная машина не запущена, то можно установить больше GPU ядер
    для ускорения анализа логов.

    Данные праметры справедливы для видеокарты NVIDIA GeForce GTX 1650 Mobile / Max-Q
    и подбираются эксперементально запуском llama.cpp с конкретной моделью и разными значениями

    n_gpu_layers

    Пример кода запуска с максимальным параметром:

    llm = Llama(
        model_path="/home/ruslan/.cache/lm-studio/models/bartowski/google_gemma-3-12b-it-GGUF/google_gemma-3-12b-it-Q4_K_S.gguf",
        n_gpu_layers=9, # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        n_ctx=14000, # Uncomment to increase the context window
        use_mmap=True,
        verbose=False, # Добавлено, чтобы уменьшить вывод от llama_cpp
    )
    """
    MAX = 8
    MIN = 4
    vmachine_marker = subprocess.run(['VBoxManage', 'list', 'runningvms'], capture_output=True, text=True, check=True)

    if len(vmachine_marker.stdout) == 0:
        return MAX
    else:
        return MIN


# print(check_gpu())