# makar72

Библиотека для экспорта файлов 3.txt, 4.txt, 5.txt в корень проекта по запросу.

## Установка

```
pip install makar72
```

## Использование

```python
import makar72
makar72.export_files()  # экспортирует файлы в текущую директорию
```

Можно указать путь:

```python
makar72.export_files('путь/к/директории')
```
