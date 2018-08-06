
import urllib.request
from urllib.parse import urlparse
import requests
import random
import vk_api
import time
import os


def picture_send(image_to_send):
    a = vk.method('photos.getWallUploadServer')
    b = requests.post(a['upload_url'], files={'photo': open(image_to_send, 'rb')}).json()
    c = vk.method('photos.saveWallPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
    d = 'photo{}_{}'.format(c['owner_id'], c['id'])
    return d


vk = vk_api.VkApi(login='login', password='password')

vk.auth()

delay = 60*random.randint(60,80)

# id Вашей группы
owner_id = -169696294

# список групп-доноров
groups = [-168416289, -168416289]

photo_sizes = ['photo_2560', 'photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75']

# слова для фильтрации
stop_words = ['конкурс','розыгрыш','приз','итоги','результаты','важн']


while True:
    try:
        group_id = random.choice(groups)
        posts = vk.method('wall.get', {'owner_id': group_id, 'count': 100, 'filter': 'owner'})

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

        vk.method('wall.post', {'owner_id': owner_id, 'message': text+'\n\n\nИсточник: vk.com/club'+str(abs(group_id)), 'attachments': photos+audios+playlists+videos+docs, 'from_group': 1, 'signed': 0})

        time.sleep(delay)

    except:
        pass
