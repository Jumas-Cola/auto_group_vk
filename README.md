auto_group_vk ![Python 3.6](https://pp.userapi.com/c846523/v846523407/b716d/N3RXKWFcPS0.jpg)
======
**auto_group_vk** – скрипт на Python, который автоматически наполнаяет группу контентом из других групп, для социальной сети Вконтакте (vk.com)

```python
...
vk = vk_api.VkApi(login='login', password='password')
vk.auth()

# задержка между постами
delay = 60*random.randint(60,80)
# id Вашей группы
owner_id = -169696294
# список групп-доноров
groups = [-168416289, -168416289]
# слова для фильтрации
stop_words = ['конкурс','розыгрыш','приз','итоги','результаты','важн']
# добавление в друзья всех заявок каждый час
add_to_friends = True
# репост на стену
repost = True
# водяной знак
watermark = True
...

```
Watermark
------------
Для добавление водяного знака поместите файл **watermark.png** в одну директорию со скриптом. По умолчанию водяной знак добавляется в левый верхний угол изображения.
![example watermark](https://pp.userapi.com/c852232/v852232687/bea3/_3g3PlUisss.jpg)
![example watermark](https://pp.userapi.com/c852232/v852232687/beab/tiITEogFpXQ.jpg)
![example watermark](https://pp.userapi.com/c852232/v852232687/beb3/c7DjLQeYv_s.jpg)

Осторожно
------------
Вк действует система против копирования контента.
Подробнее здесь:
[https://vk.com/blog/nemesis](https://vk.com/blog/nemesis)
