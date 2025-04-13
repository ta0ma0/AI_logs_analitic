import os
import time
import datetime
from pathlib import Path
import logging
from settings.logger_config import setup_logging

def delete_old_files(directory: str, days_old: int):
    """
    Deletes files older than a specified number of days within a directory.

    Args:
        directory (str): The path to the directory to clean.
        days_old (int): The minimum age in days for files to be deleted.
                         Files modified more than this many days ago will be removed.
    """
    # setup_logging()
    logging.info('start log cleaner')
    dir_path = Path(directory)

    # 1. Check if the directory exists
    if not dir_path.is_dir():
        print(f"Ошибка: Директория '{directory}' не найдена.")
        return # Exit the function if directory doesn't exist

    print(f"Поиск и удаление файлов старше {days_old} дней в директории '{directory}'...")

    # 2. Calculate the cutoff time
    # time.time() gives seconds since the epoch
    # days_old * 24 * 60 * 60 converts days to seconds
    now = time.time()
    cutoff_seconds = days_old * 24 * 60 * 60
    cutoff_time = now - cutoff_seconds # Files modified before this time are old

    deleted_count = 0
    error_count = 0

    # 3. Iterate through items in the directory
    try:
        for item in dir_path.iterdir():
            # 4. Check if it's a file (not a directory or link)
            if item.is_file():
                try:
                    # 5. Get the file's last modification time
                    file_mtime = item.stat().st_mtime

                    # 6. Compare modification time with the cutoff
                    if file_mtime < cutoff_time:
                        file_age = (now - file_mtime) / (24 * 60 * 60)
                        print(f"  Удаление файла: {item.name} (возраст: {file_age:.1f} дней)")
                        item.unlink() # Delete the file
                        deleted_count += 1
                except OSError as e:
                    print(f"  Ошибка при обработке файла {item.name}: {e}")
                    error_count += 1
                except Exception as e: # Catch other potential errors
                     print(f"  Неожиданная ошибка при обработке файла {item.name}: {e}")
                     error_count += 1

    except Exception as e:
        print(f"Ошибка при доступе к директории '{directory}': {e}")
        return # Exit if we can't even list the directory contents

    # 7. Report results
    print("-" * 20)
    if deleted_count > 0:
        logging.info(f'Deleted {deleted_count} files')
    else:
        logging.info('No files to delete')
        
    if error_count > 0:
        logging.info(f"Errors occured: {error_count}")
    else:
        logging.info('No errors occured')
    
