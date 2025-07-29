from datetime import datetime
import json
import os


def clear_terminal_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_project_root(root_dir_name='RsLogMod', fallback_root=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if root_dir_name in os.listdir(current_dir):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    if fallback_root:
        return fallback_root
    raise FileNotFoundError(f"Root directory '{root_dir_name}' not found.")


def locate(target):
    root = get_project_root()
    for path, folders, files in os.walk(root):
        if target in folders + files:
            return os.path.join(path, target)
    raise FileNotFoundError(f"'{target}' not found in '{root}'.")


def load_default_log_folder():
    default_log_folder = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(default_log_folder):
        os.makedirs(default_log_folder)
    return default_log_folder


def load_default_archive_folder():
    default_archive_folder = os.path.join(os.getcwd(), 'logs', 'archive')
    if not os.path.exists(default_archive_folder):
        os.makedirs(default_archive_folder)
    return default_archive_folder


def load_config_from_file(target_config=None):
    config_path = locate('configs.json')

    with open(config_path, 'r') as file:
        config = json.load(file)

    if target_config == 'log_folder' and not config.get('log_folder'):
        return load_default_log_folder()

    if target_config == 'archive_folder' and not config.get('archive_folder'):
        return load_default_archive_folder()

    return config.get(target_config) if target_config else config


def update_config_file(key: str, value: any):
    file_path = locate('configs.json')
    with open(file_path, 'r+') as file:
        file_content = json.load(file)
        file_content[key] = value
        file.seek(0)
        file.truncate()
        json.dump(file_content, file, indent=4)


def format_out_path(log_name):
    log_folder = load_config_from_file('log_folder')
    if log_folder:
        if not os.path.exists(log_folder):
            os.makedirs(log_folder, exist_ok=True)
        if not log_name:
            log_name = 'log'
        return os.path.join(log_folder, f"{log_name}.log")


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


def get_current_time_safe():
    return datetime.now().strftime("%H-%M-%S")


def rotate_logs():
    def rotate(path):
        archive_folder = load_config_from_file('archive_folder')
        log_folder = load_config_from_file('log_folder')
        if not archive_folder:
            archive_folder = os.path.join(log_folder, 'archived')
            update_config_file('archive_folder', archive_folder)
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
        new_file_path = os.path.join(archive_folder, f'archived_{get_current_date()}_{get_current_time_safe()}.log')
        try:
            with open(path, 'r') as old_file:
                with open(new_file_path, 'w') as new_file:
                    content = old_file.read()
                    new_file.write(content)
            with open(path, 'w') as old_file:
                old_file.truncate(0)
        except IOError as e:
            print(f"Error during log rotation: {e}")

    max_size = load_config_from_file('max_size_in_mega_bytes') * 1024 * 1024
    log_folder = load_config_from_file('log_folder')
    if log_folder:
        for root, _, files in os.walk(log_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if os.path.getsize(file_path) > max_size:
                    rotate(file_path)
