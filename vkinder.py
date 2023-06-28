from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from config import my_token

#Получение необходимой информации о пользователе. Получение и обработка фотографий. 

class VkinderBot():
    def __init__(self, my_token):
        self.vkapi = vk_api.VkApi(token = my_token)

    def get_user_info(self, user_id):
        '''Получение информации о пользователе. (Семейное положение, Пол, возраст, город)'''

        try:
            user_info, = self.vkapi.method('users.get',
                                           {'user_id': user_id,
                                            'fields': 'sex, city, relation, bdate'
                                            }
            )
        except ApiError:
            user_info = {}
            #сообщение об ошибке.
        if len(user_info['bdate'].split('.')) == 3:
            user_bd = datetime.now().year - int(user_info['bdate'].split('.')[2])
        else: 
            user_bd = None

        result = {'name' : user_info['first_name'] if
            'first_name' in user_info else None,
            'sex' : user_info['sex'],
          'city' : user_info.get('city')['title'] if 
          user_info.get('city') is not None else None,
          'age' : user_bd
        }

        return result


    def get_result_search(self, search_params, offset):
        '''Метод выполняющий поиск пользователей по заданным параметрам. '''
        try:
            search_result = self.vkapi.method('users.search', 
                                              {'count' : 50,
                                               'offset' : offset,
                                               'hometown' : search_params['city'],
                                               'sex' : 1 if search_params['sex'] == 2 else 2,
                                               'age_from' : search_params['age'] - 5,
                                               'age_to' : search_params['age'] + 5,
                                               'has_photo' : True
                                               })
        except ApiError:
            search_result = []
            # сообщение об ошибке.
        found_users = []
        for item in search_result['items']:
            if item['is_closed'] is False:
                found_users.append(
                    {'name' : item['first_name'] + ' ' + item['last_name'],
                                'id' : item['id']}
                )
        return found_users

    def get_photo(self, user_id):
        try:
            photos = self.vkapi.method('photos.get', 
                                       {'owner_id' : user_id,
                                        'album_id' : 'profile',
                                        'extended' : '1'
                                        }
            )
            
        except ApiError:
            photos = {}
            #сообщение об ошибке.
        result = []
        for item in photos['items']:
            likes_count = item['likes']['count']
            comments_count = item['comments']['count']
            result.append(
                {'owner_id' : item['owner_id'],
                 'id_photos' : item['id'],
                 'popularity' : likes_count + comments_count
                 }
            )
        sorted_photos = sorted(result, key=lambda x: x['popularity'], reverse=True)
        return sorted_photos[:3]


    

bot = VkinderBot(my_token=my_token)

if __name__ == '__main__':
    bot.get_photo(137702708)