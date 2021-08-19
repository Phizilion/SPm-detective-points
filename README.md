# SPm-detective-points
Бот подсчёта очков для детективов СПм.

## Создайте файл config.py для настройки:
```python
TOKEN = ""  # токен бота
command_prefix = ""  # префикс команд
db_path = ""  # путь к базе данных
admin_list = (,) id администраторов, которые могу выполнять большинство команд
report_reaction = ""  # реакция, которую бот ставит на отчёт
report_reward =  # награда за один отчёт (в очках)
report_money_reward =  # зарплата за один отчёт
detectives_guild_id =  # id сервера детективов
reports_channel_id =  # id канала для скринов
points_channel_id =  # id канала с сообщением, в котором выводятся очки
points_message_id =  # id сообщения, в котором выводятся очки
logs_channel_id =  # id канала для логов
user_for_report = # id пользователя для отправки отчётов
new_week_answer_message = ""  # это сообщение в ответ на команду new_week
update_answer_message = ""  # это сообщение в ответ на команду update
```
