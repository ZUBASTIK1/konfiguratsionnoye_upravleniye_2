import tomllib 
import sys
import os
import re
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


def main():
    config_path = "config.toml"
    try:
        settings = load_config(config_path)
    except ConfigError as e:
        print(f"[Ошибка конфигурации] {e}", file=sys.stderr)
        sys.exit(1)

    # Вывод параметров в формате ключ=значение
    for key, value in settings.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
