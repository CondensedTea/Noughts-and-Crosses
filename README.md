## Консольная игра крестики-нолики на основе `curses`

Для запуска приложения необходимо поставить библиотеку `click`: 
```bash
pip install click
```

После этого можно запустить приложение:
```bash
python3 noughts_and_crosess
```

Игра запустится с игровым полем 3х3, игрок будет играть за случайную сторону.
Все параметры можно задать через аргументы:
- `--width, -w`: Ширина поля.
- `--height, -h`: Высота поля.
- `--side, -s`: Сторона, за которую вы будете играть. 
  Нолики: noughts, n или o, крестики: crosses, c, или x.
- `--load, -l`: Путь до файла сохранения игры. Если этот параметр задан, то все другие параметры будут проигнорированы.   
