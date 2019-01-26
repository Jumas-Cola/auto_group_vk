import unicodedata
import urllib.request
from PIL import Image
import random
import sqlite3
import json
import requests
import vk_api
import os


class User:
    """
        docstring forUser.

        Чтение конфигурации из файла
    """

    def __init__(self, file='config.json'):
        with open(file) as f:
            data = json.load(f)
        self.group_id = data['group_id']
        self.post_text = data['post_text']
        self.donors = data['donors']
        self.stop_words = data['stop_words']
        self.add_friends = data['add_friends']
        self.del_requests = data['del_requests']
        self.repost = data['repost']
        self.watermark = data['watermark']
        self.watermark_img = data['watermark_img']
        self.sqlog = data['sqlog']
        self.vk = vk_api.VkApi(token=data['access_token'])
        self.v = data['v']

    """
        Добавить в друзья все заявки
    """

    def add_all_to_friends(self):
        for request_to_friends in self.vk.method('friends.getRequests', {'out': 0, 'v': self.v})['items']:
            self.vk.method('friends.add', {
                           'user_id': request_to_friends, 'v': self.v})

    """
        Отписаться от всех заявок
    """

    def friends_deny_request(self):
        for request_to_friends in self.vk.method('friends.getRequests', {'out': 1, 'v': self.v})['items']:
            self.vk.method('friends.delete', {
                           'user_id': request_to_friends, 'v': self.v})

    """
        Загрузка изображения на сервер и получение объекта photo
    """

    def picture_send(self, image_to_send):
        a = self.vk.method('photos.getWallUploadServer', {'v': self.v})
        b = requests.post(a['upload_url'], files={
                          'photo': open(image_to_send, 'rb')}).json()
        c = self.vk.method('photos.saveWallPhoto', {
            'photo': b['photo'], 'server': b['server'], 'hash': b['hash'], 'v': self.v})[0]
        d = f'photo{c["owner_id"]}_{c["id"]}'
        return d

    """
        Репост последнего поста из группы
        (если есть закреп - то предпоследнего)
    """

    def repost_last_post(self):
        post = self.vk.method(
            'wall.get', {'owner_id': -self.group_id, 'count': 1, 'filter': 'owner', 'v': self.v})['items'][0]
        if 'is_pinned' in post:
            post = self.vk.method('wall.get', {
                                  'owner_id': -self.group_id, 'offset': 1, 'count': 1, 'filter': 'owner', 'v': self.v})['items'][0]
        owner_id = post['owner_id']
        post_id = post['id']
        self.vk.method('wall.repost', {
                       'object': f'wall{owner_id}_{post_id}', 'v': self.v})
        return post_id

    """
        Проверка наличия идентификатора поста в базе данных
    """

    def check_in_db(self, id):
        conn = sqlite3.connect("posts.db")
        cursor = conn.cursor()
        try:
            cursor.execute('CREATE TABLE posts (id text)')
        except:
            pass
        sql = "SELECT * FROM posts WHERE id=?"
        cursor.execute(sql, [(id)])
        res = cursor.fetchall()
        if res:
            return 1
        else:
            return 0

    """
        Добавление идентификатора поста в базу данных
    """

    def add_in_db(self, id):
        conn = sqlite3.connect("posts.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""CREATE TABLE posts (id text)""")
        except:
            pass
        cursor.execute("""INSERT INTO posts (id) VALUES (?)""", (id,))
        conn.commit()
        return 0

    """
        Добавление водяного знака
    """

    def add_watermark(self, img):
        picture = Image.open(img)
        watermark = Image.open(self.watermark_img).convert("RGBA")
        width, height = watermark.size
        picture.paste(watermark, (0, 0, width, height),  watermark)
        picture.save(img)

    """
        Получает случайный пост со стены группы из списка
    """

    def get_random_post(self):
        while True:
            donor_id = random.choice(self.donors)
            count = self.vk.method(
                'wall.get', {'owner_id': donor_id, 'v': self.v})['count']
            post = self.vk.method('wall.get', {'owner_id': donor_id, 'offset': random.randint(
                2, count - 1), 'count': 1, 'filter': 'owner', 'v': self.v})['items'][0]
            donor_post_id = post['id']
            text = post['text'].lower()
            if any(word in text for word in self.stop_words):
                continue
            if post['marked_as_ads']:
                continue
            if self.sqlog:
                if self.check_in_db(f'{donor_id}_{donor_post_id}'):
                    continue
            attachments = ''
            for attachment in post['attachments']:
                if attachment['type'] == 'photo':
                    photo = attachment['photo']
                    url = photo['sizes'][-1]['url']
                    file = url.split('/')[-1]
                    urllib.request.urlretrieve(url, file)
                    if self.watermark:
                        self.add_watermark(file)
                    attachments += self.picture_send(file) + ','
                    os.remove(file)
                if attachment['type'] == 'audio':
                    audio = attachment['audio']
                    attachments += f'audio{audio["owner_id"]}_{audio["id"]},'
                if attachment['type'] == 'audio_playlist':
                    audio_playlist = attachment['audio_playlist']
                    attachments += f'audio_playlist{audio_playlist["owner_id"]}_{audio_playlist["id"]},'
                if attachment['type'] == 'video':
                    video = attachment['video']
                    attachments += f'video{video["owner_id"]}_{video["id"]},'
                if attachment['type'] == 'doc':
                    doc = attachment['doc']
                    attachments += f'doc{doc["owner_id"]}_{doc["id"]},'
            if not attachments:
                continue
            break
        return {'donor_id': donor_id, 'donor_post_id': donor_post_id, 'attachments': attachments, 'text': text}

    """
        Пост в группу
    """

    def make_post(self, attachments, donor_id):
        try:
            donor = self.vk.method(
                'groups.getById', {'group_ids': -donor_id, 'v': self.v})[0]['name']
            donor = unicodedata.normalize(
                'NFKD', donor).encode('ascii', 'ignore')
            donor = donor.decode('utf8').replace(')', '').replace('(', '')
        except:
            donor = 'club' + str(abs(donor_id))
        self.vk.method('account.setOnline', {'v': self.v})
        self.vk.method('wall.post', {'owner_id': -self.group_id, 'message': self.post_text +
                                     f'\n\n\nИсточник: @club{abs(donor_id)}({donor})', 'attachments': attachments, 'from_group': 1, 'signed': 0, 'v': self.v})
