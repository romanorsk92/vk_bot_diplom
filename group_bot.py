import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from db import *
from config import my_token, token
from vkinder import VkinderBot
engine = create_engine(db_vkinder_connect)
Base.metadata.create_all(engine)
#диалог с пользователем. Отправка результатов поиска с фотографиями.

class GroupBot():
    def __init__(self, my_token, token):
        self.vk_group = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_group)
        self.vkinder = VkinderBot(my_token=my_token)
        self.offset = 0
        self.search_params = {}
        self.result_search = []

    def send_message(self, user_id, message, attachment=None):
        self.vk_group.method('messages.send',
        {'user_id' : user_id,
        'message' : message,
        'attachment' : attachment,
        'random_id' : get_random_id()}
        )

    def logics(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                if request =='привет' or request == 'начать':
                    self.search_params = self.vkinder.get_user_info(event.user_id)
                    self.send_message(event.user_id, f'''привет {self.search_params['name']} Можем попробовать поискать  тебе пару  для этого необходимо проверить все ли данные анкеты заполнены!''', attachment=None)
                    if self.search_params['sex'] == 0:
                        self.send_message(event.user_id, f'У тебя не указан пол. Введи 1 - если твой пол женский или 2 - если твой пол мужской!', attachment=None)
                        self.search_params['sex'] = request
                    if self.search_params['city'] == None:
                        self.send_message(event.user_id, f'У тебя не указан город! Введи его ...', attachment=None)
                        self.search_params['city'] = request
                    if self.search_params['age'] == None:
                        self.send_message(event.user_id, f'У вас не указан возраст. Для поиска он необходим. Введите его...', attachment=None)
                        self.search_params['age'] = request
                    
                    self.send_message(event.user_id, f'Начнём? Введи "поиск" для продолжения!', attachment=None)
                    self.send_message(
                        event.user_id, f'''Нашел подходящих для тебя людей. Напиши команду "да" для перехода к результатам поиска. Напиши команду "еще" для просмотра следующей анкеты.''', attachment=None)
                elif request == 'поиск' or request == 'да' or request == 'еще':
                    self.send_message(event.user_id, f'Начинаем поиск!', attachment=None)
                    if self.result_search:
                        while self.result_search:
                            user = self.result_search.pop()
                            if check_seen_users(engine, event.user_id, user['id']) == False:
                                photos = self.vkinder.get_photo(user['id'])
                                photo_attachment = ''
                                for photo in photos:
                                    photo_attachment += f'photo{photo["owner_id"]}_{photo["id_photos"]},'
                                self.offset += 50
                                self.send_message(
                                event.user_id, f'''{user['name']} Найти можно по ссылке vk.com/id{user['id']}''', attachment=photo_attachment)
                                add_user(engine, event.user_id, user['id'])
                                break
                            else:
                                self.offset += 50
                    else:
                        self.result_search = self.vkinder.get_result_search(self.search_params, self.offset)
                            
                else:
                    self.send_message(event.user_id, f'неизвестная команда!', attachment=None)








group_bot = GroupBot(my_token=my_token, token=token)