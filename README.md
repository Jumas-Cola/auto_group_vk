auto_group_vk ![Python 3.6]
======
**auto_group_vk** – скрипт на Python, который автоматически наполнаяет группу контентом из других групп, для социальной сети Вконтакте (vk.com)

```python
...
vk = vk_api.VkApi(login='login', password='password')

vk.auth()

delay = 60*random.randint(60,80)

# id Вашей группы
owner_id = -169696294

# список групп-доноров
groups = [-168416289, -168416289]
...

```
Осторожно
------------
Вк действует система против копирования контента.
Подробнее здесь:
[https://vk.com/blog/nemesis](https://vk.com/blog/nemesis)
