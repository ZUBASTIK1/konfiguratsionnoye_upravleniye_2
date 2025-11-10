import tomllib
import sys
import os
import re
import urllib.request
from urllib.parse import urlparse

CONFIG_KEYS = {
    "package_name": str,
    "repository_url": str,
    "repo_mode": str,
    "version": str,
    "filter_substring": str,
}

VALID_REPO_MODES = {"local", "remote"}


class ConfigError(Exception):
    pass


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"Файл конфигурации '{path}' не найден")

    with open(path, "rb") as f:
        try:
            data = tomllib.load(f)
        except Exception as e:
            raise ConfigError(f"Ошибка разбора TOML: {e}")

    if "settings" not in data:
        raise ConfigError("Секция [settings] отсутствует в конфигурации")

    settings = data["settings"]

    # Проверка обязательных ключей
    for key, expected_type in CONFIG_KEYS.items():
        if key not in settings:
            raise ConfigError(f"Отсутствует обязательный параметр: {key}")
        if not isinstance(settings[key], expected_type):
            raise ConfigError(f"Неверный тип для '{key}': ожидался {expected_type.__name__}")

    # Дополнительные проверки
    url = settings["repository_url"]
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc) and not os.path.exists(url):
        raise ConfigError(f"Некорректный путь или URL: {url}")

    if settings["repo_mode"] not in VALID_REPO_MODES:
        raise ConfigError(f"Недопустимый режим repo_mode: {settings['repo_mode']} "
                          f"(ожидалось одно из {VALID_REPO_MODES})")

    version_pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(version_pattern, settings["version"]):
        raise ConfigError(f"Некорректный формат версии: {settings['version']} "
                          f"(ожидалось X.Y.Z)")

    return settings




def read_file(path_or_url: str, mode: str) -> bytes:
    """Чтение файла локально или по URL"""
    if mode == "local":
        if not os.path.exists(path_or_url):
            raise ConfigError(f"Файл {path_or_url} не найден")
        with open(path_or_url, "rb") as f:
            return f.read()
    elif mode == "remote":
        try:
            with urllib.request.urlopen(path_or_url) as resp:
                return resp.read()
        except Exception as e:
            raise ConfigError(f"Ошибка загрузки по URL {path_or_url}: {e}")
    else:
        raise ConfigError(f"Неизвестный режим: {mode}")


def extract_dependencies_from_pyproject(data: bytes) -> list[str]:
    """Извлечение зависимостей из pyproject.toml"""
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except Exception as e:
        raise ConfigError(f"Ошибка разбора pyproject.toml: {e}")

    if "project" not in parsed or "dependencies" not in parsed["project"]:
        return []

    return parsed["project"]["dependencies"]


def extract_dependencies_from_setup(data: bytes) -> list[str]:
    """Простейший парсинг setup.py (ищем install_requires)"""
    text = data.decode("utf-8")
    match = re.search(r"install_requires\s*=\s*\[(.*?)\]", text, re.S)
    if not match:
        return []
    deps_raw = match.group(1)
    deps = re.findall(r"'([^']+)'|\"([^\"]+)\"", deps_raw)
    return [d[0] or d[1] for d in deps]


def collect_dependencies(settings: dict) -> list[str]:
    repo_url = settings["repository_url"]
    repo_mode = settings["repo_mode"]
    version = settings["version"]

    # Формируем путь/URL для конкретной версии
    pyproject_path = os.path.join(repo_url, version, "pyproject.toml")
    setup_path = os.path.join(repo_url, version, "setup.py")

    # pyproject.toml
    try:
        data = read_file(pyproject_path, repo_mode)
        deps = extract_dependencies_from_pyproject(data)
        if deps:
            return deps
    except Exception:
        pass

    # setup.py
    try:
        data = read_file(setup_path, repo_mode)
        deps = extract_dependencies_from_setup(data)
        if deps:
            return deps
    except Exception:
        pass

    return []


def main():
    config_path = "config.toml"
    try:
        settings = load_config(config_path)
    except ConfigError as e:
        print(f"[Ошибка конфигурации] {e}", file=sys.stderr)
        sys.exit(1)

    # Этап 1: вывод параметров
    print("Параметры конфигурации:")
    for key, value in settings.items():
        print(f"{key}={value}")

    # Этап 2: вывод зависимостей
    print("\nПрямые зависимости пакета:")
    deps = collect_dependencies(settings)
    if deps:
        for dep in deps:
            print(f"- {dep}")
    else:
        print("Зависимости не найдены")


if __name__ == "__main__":
    main()