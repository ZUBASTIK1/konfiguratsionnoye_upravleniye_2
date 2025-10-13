# Минимальный прототип CLI-приложения (Этап 1)

## 1. Общее описание
Цель данного этапа — создать минимальное CLI-приложение на Python, которое настраивается через конфигурационный файл формата **TOML**.  
Приложение загружает параметры из файла `config.toml`, проверяет их корректность и выводит в формате `ключ=значение`.  
Реализована обработка ошибок для всех параметров.

---

## 2. Описание функций и настроек

### Настраиваемые параметры (секция `[settings]` в `config.toml`)
- **package_name** *(str)* — имя анализируемого пакета.  
- **repository_url** *(str)* — URL-адрес репозитория или путь к локальному тестовому репозиторию.  
- **repo_mode** *(str)* — режим работы с репозиторием: `local` или `remote`.  
- **version** *(str)* — версия пакета в формате `X.Y.Z`.  
- **filter_substring** *(str)* — подстрока для фильтрации пакетов.  

Пример `config.toml`:
```toml
[settings]
package_name = "mypackage"
repository_url = "https://github.com/example/repo"
repo_mode = "remote"
version = "1.0.0"
filter_substring = "test"
```
## 3. Команды для сборки проекта и запуска тестов

### Запуск приложения 

```bash
python main.py
```

### Примеры вывода при корректной конфигурации

```bash
package_name=mypackage
repository_url=https://github.com/example/repo
repo_mode=remote
version=1.0.0
filter_substring=test
```


## 4. Примеры **использования**

<img width="857" height="272" alt="image" src="https://github.com/user-attachments/assets/f246e2f0-1fc7-4029-963b-32ff78e820d2" />
