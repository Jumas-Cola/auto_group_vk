
import urllib.request
from urllib.parse import urlparse
from PIL import Image
import requests
import random
import vk_api
import time
import os

# загрузка изображения на сервер и получение объекта photo
def picture_send(image_to_send):
    a = vk.method('photos.getWallUploadServer')
    b = requests.post(a['upload_url'], files={'photo': open(image_to_send, 'rb')}).json()
    c = vk.method('photos.saveWallPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
    d = 'photo{}_{}'.format(c['owner_id'], c['id'])
    return d

# добавить в друзья все заявки
def add_all_to_friends(vk):
    for request_to_friends in vk.method('friends.getRequests', {'out': 0})['items']:
        vk.method('friends.add', {'user_id': request_to_friends})
        time.sleep(5)

# репост последнего поста из группы
def get_last_post(vk, last_id, owner_id):
    post = vk.method('wall.get', {'owner_id': owner_id, 'offset': 1, 'count': 1, 'filter': 'owner'})
    post_id = post['items'][0]['id']
    if post_id != last_id:
        vk.method('wall.repost', {'object': 'wall{}_{}'.format(owner_id, post_id)})
    return post_id

# добавление водяного знака
def add_watermark(img):
    picture = Image.open(img)
    watermark = Image.open('watermark.png').convert("RGBA")
    width, height = watermark.size
    picture.paste(watermark, (0, 0, width, height),  watermark)
    picture.save(img)



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


photo_sizes = ['photo_2560', 'photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75']
last_id = 0

while True:
    try:
        group_id = random.choice(groups)
        posts = vk.method('wall.get', {'owner_id': group_id, 'count': 100, 'filter': 'owner', 'v': '5.60'})
        count = random.randint(2,90)
        for i in range(count, count+1):
            photos = ''
            audios = ''
            playlists = ''
            videos = ''
            docs = ''
            text = posts['items'][i]['text']
            got_stop_words = False
            for word in stop_words:
                if word in text.lower():
                    got_stop_words = True
                    break
            if (posts['items'][i]['marked_as_ads'] == 0) and (not got_stop_words):
                for attachment in posts['items'][i]['attachments']:
                    if attachment['type'] == 'photo':
                        photo = attachment['photo']
                        for size in photo_sizes:
                            if size in photo:
                                url = photo[size]
                                file = urlparse(photo[size])[2].split('/')[-1]
                                urllib.request.urlretrieve(url, file)
                                break
                        if watermark:
                            add_watermark(file)
                        photos += picture_send(file) + ','
                        os.remove(file)
                    if attachment['type'] == 'audio':
                        audio = attachment['audio']
                        audios+='audio{}_{},'.format(audio['owner_id'], audio['id'])
                    if attachment['type'] == 'audio_playlist':
                        audio_playlist = attachment['audio_playlist']
                        playlists+='audio_playlist{}_{},'.format(audio_playlist['owner_id'], audio_playlist['id'])
                    if attachment['type'] == 'video':
                        video = attachment['video']
                        videos+='video{}_{},'.format(video['owner_id'], video['id'])
                    if attachment['type'] == 'doc':
                        doc = attachment['doc']
                        docs+='doc{}_{},'.format(doc['owner_id'], doc['id'])
            else:
                count += 1

        vk.method('account.setOnline') # посылаем онлайн перед созданием поста

        vk.method('wall.post', {'owner_id': owner_id, 'message': text+'\n\n\nИсточник: vk.com/club'+str(abs(group_id)), 'attachments': photos+audios+playlists+videos+docs, 'from_group': 1, 'signed': 0})

        if repost:
            try:
                last_id = get_last_post(vk, last_id, owner_id)
            except:
                pass
        if add_to_friends:
            try:
                add_all_to_friends(vk)
            except:
                pass

        time.sleep(delay)

    except:
        pass
