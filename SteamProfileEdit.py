import steam.webauth as wa
import requests
import time
import configparser
import random
import os
import string
import uuid


class ProfileEdit():
    _acc_name = ''
    _acc_pas = ''
    _config_file_name = 'config.ini'
    _max_errors = 5
    _sleep_time = 5
    __errors = 0

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        default = config['DEFAULT']

        self._sleep_time = int(default.get('sleep_time'))
        self._max_errors = int(default.get('max_error'))

    def steam_login(self):
        try:
            user = wa.WebAuth(self._acc_name, self._acc_pas)
            session = user.login()
            self.__errors = 0
            return session, user

        except Exception as e:
            print(e, ' ', self._acc_name, ':', self._acc_pas)
            if self.__errors >= self._max_errors:
                print('Max erors')
                return False, False
            self.__errors = self.__errors + 1
            time.sleep(self._sleep_time)
            return self.steam_login()

    def get_data_from_config(self):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        default = config['DEFAULT']

        responce = {
            'name': self.__try_split_data(default.get('name')),
            'avatar_folder': self.__try_split_data(default.get('avatar_folder')),
            'realname': self.__try_split_data(default.get('realname')),
            'country': self.__try_split_data(default.get('country')),
            'state': self.__try_split_data(default.get('state')),
            'city': self.__try_split_data(default.get('city')),
            'summary0': self.__try_split_data(default.get('summary0')),
            'summary1': self.__try_split_data(default.get('summary1')),
            'summary2': self.__try_split_data(default.get('summary2')),
            'summary3': self.__try_split_data(default.get('summary3')),
            'summary4': self.__try_split_data(default.get('summary4')),
            'summary5': self.__try_split_data(default.get('summary5')),
            'summary6': self.__try_split_data(default.get('summary6')),
            'summary7': self.__try_split_data(default.get('summary7')),
            'summary8': self.__try_split_data(default.get('summary8')),
            'summary9': self.__try_split_data(default.get('summary9'))
        }
        return responce

    def __try_split_data(self, value):
        try:
            return value.split(',')
        except Exception:
            if value == None:
                return ''
            return value

    def __try_random_data(self, value):
        try:
            return random.choice(value)
        except Exception:
            if value == None:
                return ''
            return value

    def form_data_from_dict(self, row_data, user):
        summery = ''
        for x in range(10):
            summery = summery + \
                random.choice(row_data.get('summary'+str(x)))+' \n'
        data = {
            'sessionID': user.session_id,
            'type': 'profileSave',
            'weblink_1_title': '',
            'weblink_1_url': '',
            'weblink_2_title': '',
            'weblink_2_url': '',
            'weblink_3_title': '',
            'weblink_3_url': '',
            'personaName': self.__try_random_data(row_data.get('name')),
            'real_name': self.__try_random_data(row_data.get('realname')),
            'country': self.__try_random_data(row_data.get('country')),
            'state': self.__try_random_data(row_data.get('state')),
            'city': self.__try_random_data(row_data.get('city')),
            'customURL': '',
            'summary': summery,
            'favorite_badge_badgeid': '',
            'favorite_badge_communityitemid': '',
            'primary_group_steamid': 0,
        }
        return data

    def get_privacy_data_from_config(self, user):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        privacy = config['PRIVACY']

        data = (
            ("sessionid", (None, user.session_id)),
            ("Privacy", (None, ('{"PrivacyProfile":'+privacy.get('PrivacyProfile') +
                                ',"PrivacyInventory":'+privacy.get('PrivacyInventory') +
                                ',"PrivacyInventoryGifts":'+privacy.get('PrivacyInventoryGifts') +
                                ',"PrivacyOwnedGames":'+privacy.get('PrivacyOwnedGames') +
                                ',"PrivacyPlaytime":'+privacy.get('PrivacyPlaytime') +
                                ',"PrivacyFriendsList":'+privacy.get('PrivacyFriendsList')+'}'))),
            ("eCommentPermission", (None, privacy.get('eCommentPermission')))
        )
        return data

    def __get_avatars_path_list(self):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        default = config['DEFAULT']
        avatars = os.listdir(path=default.get('avatar_folder'))

        for x in range(len(avatars)):
            avatars[x] = default.get('avatar_folder') + '/' + avatars[x]

        return avatars

    def change_avatar(self, user, cookies):
        my_req = MyRequest()
        url = 'https://steamcommunity.com/actions/FileUploader'
        avatars = self.__get_avatars_path_list()
        avatar_data = {
            "MAX_FILE_SIZE": "1048576",
            "type": "player_avatar_image",
            "sId": user.steam_id,
            "sessionid": user.session_id,
            "doSub": "1",
        }
        avatar_params = {
            'type': 'player_avatar_image',
            'sId': user.steam_id
        }
        picture = open(random.choice(avatars), 'rb')
        avatar_files = {
            'avatar': picture,
        }
        req = my_req.post_with_params_files_data(
            url, avatar_params, avatar_files, avatar_data, cookies)
        if str(req) == '<Response [200]>':
            print('Avatar changed')
            return True
        else:
            print('Error changing avatar')
            return False

    def data_change(self, cookies, user):
        rand = Random_for_steam_edit()
        my_req = MyRequest()
        row_data = self.get_data_from_config()
        url = 'https://steamcommunity.com/profiles/'+str(user.steam_id)+'/edit'
        row_data = rand.add_random_symbol(row_data)
        data = self.form_data_from_dict(row_data, user)
        # print(data)

        req = my_req.post_with_cookie_and_data(url, cookies, data)
        if str(req) == '<Response [200]>':
            print('Data changed')
            return True
        else:
            print('Error changing data')
            return False

    def privacy_data_change(self, cookies, user):
        my_req = MyRequest()
        privacy_url = 'https://steamcommunity.com/profiles/' + \
            str(user.steam_id)+'/ajaxsetprivacy/'
        privacy_data = self.get_privacy_data_from_config(user)

        req = my_req.post_with_cookie_and_files(
            privacy_url, cookies, privacy_data)
        if str(req) == '<Response [200]>':
            print('Privacy data changed')
            return True
        else:
            print('Error changing privacy data')
            return False

    def data_edit(self, acc_name, acc_password):
        self._acc_name = acc_name
        self._acc_pas = acc_password
        my_req = MyRequest()
        session, user = self.steam_login()
        cookies = session.cookies

        if session != False:
            self.data_change(cookies, user)
            time.sleep(self._sleep_time)

            self.privacy_data_change(cookies, user)
            time.sleep(self._sleep_time)

            self.change_avatar(user, cookies)
            time.sleep(self._sleep_time)


class ImportData():
    _acc_file_name = 'Accs.txt'
    _mail_file_name = 'Mail.txt'

    def import_acc(self):
        response = []
        with open(self._acc_file_name, 'r') as f:
            for line in f.readlines():
                line = line.replace(';', ':').replace('\n', '').split(':')
                response.append(line)
        return response


class Random_for_steam_edit():
    _config_file_name = 'config.ini'
    _random_symbol_amount = 2
    _random_symbol_after_name = False
    _random_symbol_after_real_name = False
    _random_symbol_after_summary0 = False
    _random_symbol_after_summary1 = False
    _random_symbol_after_summary2 = False
    _random_symbol_after_summary3 = False
    _random_symbol_after_summary4 = False
    _random_symbol_after_summary5 = False
    _random_symbol_after_summary6 = False
    _random_symbol_after_summary7 = False
    _random_symbol_after_summary8 = False
    _random_symbol_after_summary9 = False

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        rand = config['RANDOM']

        self._random_symbol_amount = int(rand.get('random_symbol_amount'))
        self._random_symbol_after_name = bool(
            int(rand.get('random_symbol_after_name')))
        self._random_symbol_after_real_name = bool(
            int(rand.get('random_symbol_after_real_name')))
        self._random_symbol_after_summary0 = bool(
            int(rand.get('random_symbol_after_summary0')))
        self._random_symbol_after_summary1 = bool(
            int(rand.get('random_symbol_after_summary1')))
        self._random_symbol_after_summary2 = bool(
            int(rand.get('random_symbol_after_summary2')))
        self._random_symbol_after_summary3 = bool(
            int(rand.get('random_symbol_after_summary3')))
        self._random_symbol_after_summary4 = bool(
            int(rand.get('random_symbol_after_summary4')))
        self._random_symbol_after_summary5 = bool(
            int(rand.get('random_symbol_after_summary5')))
        self._random_symbol_after_summary6 = bool(
            int(rand.get('random_symbol_after_summary6')))
        self._random_symbol_after_summary7 = bool(
            int(rand.get('random_symbol_after_summary7')))
        self._random_symbol_after_summary8 = bool(
            int(rand.get('random_symbol_after_summary8')))
        self._random_symbol_after_summary9 = bool(
            int(rand.get('random_symbol_after_summary9')))

    def add_random_symbol(self, data):
        pname = self.__add_random_symbol_to_list(
            data.get('name'), self._random_symbol_after_name)
        data.update({'name': pname})

        prealname = self.__add_random_symbol_to_list(
            data.get('realname'), self._random_symbol_after_real_name)
        data.update({'realname': prealname})

        psum0 = self.__add_random_symbol_to_list(
            data.get('summary0'), self._random_symbol_after_summary0)
        data.update({'summary0': psum0})

        psum1 = self.__add_random_symbol_to_list(
            data.get('summary1'), self._random_symbol_after_summary1)
        data.update({'summary1': psum1})

        psum2 = self.__add_random_symbol_to_list(
            data.get('summary2'), self._random_symbol_after_summary2)
        data.update({'summary2': psum2})

        psum3 = self.__add_random_symbol_to_list(
            data.get('summary3'), self._random_symbol_after_summary3)
        data.update({'summary3': psum3})

        psum4 = self.__add_random_symbol_to_list(
            data.get('summary4'), self._random_symbol_after_summary4)
        data.update({'summary4': psum4})

        psum5 = self.__add_random_symbol_to_list(
            data.get('summary5'), self._random_symbol_after_summary5)
        data.update({'summary5': psum5})

        psum6 = self.__add_random_symbol_to_list(
            data.get('summary6'), self._random_symbol_after_summary6)
        data.update({'summary6': psum6})

        psum7 = self.__add_random_symbol_to_list(
            data.get('summary7'), self._random_symbol_after_summary7)
        data.update({'summary7': psum7})

        psum8 = self.__add_random_symbol_to_list(
            data.get('summary8'), self._random_symbol_after_summary8)
        data.update({'summary8': psum8})

        psum9 = self.__add_random_symbol_to_list(
            data.get('summary9'), self._random_symbol_after_summary9)
        data.update({'summary9': psum9})
        return data

    def __add_random_symbol_to_list(self, list, value):

        for x in range(len(list)):
            list[x] = list[x] + ' ' + self.__random_symbol(value)

        return list

    def __random_symbol(self, value):
        if value:
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=self._random_symbol_amount))
        else:
            return ''


class MyRequest():
    _config_file_name = 'config.ini'
    _request_timeout = 10
    _retry = 5
    _sleep_time = 5
    _max_errors = 5
    __errors = 0

    def __init__(self):
        config = configparser.ConfigParser()
        config.read(self._config_file_name)
        default = config['DEFAULT']

        self._sleep_time = int(default.get('sleep_time'))
        self._max_errors = int(default.get('max_error'))
        self._retry = int(default.get('retry'))

    def get_with_cookie(self):
        pass

    def post_with_cookie_and_data(self, url, cookies, data):
        try:
            req = requests.post(url=url, cookies=cookies,
                                data=data, timeout=self._request_timeout)
            self.__errors = 0
            return req
        except Exception as e:
            print(e, ' ', url)
            if self.__errors >= self._max_errors:
                print('Max Error')
                return False
            self.__errors = self.__errors + 1
            time.sleep(self._sleep_time)
            return self.post_with_cookie_and_data(url, cookies, data)

    def post_with_cookie_and_files(self, url, cookies, files):
        try:
            req = requests.post(url=url, cookies=cookies,
                                files=files, timeout=self._request_timeout)
            self.__errors = 0
            return req
        except Exception as e:
            print(e, ' ', url)
            if self.__errors >= self._max_errors:
                print('Max Error')
                return False
            self.__errors = self.__errors + 1
            time.sleep(self._sleep_time)
            return self.post_with_cookie_data_and_headers(url, cookies, files)

    def post_with_params_files_data(self, url, params, files, data, cookies):
        try:
            req = requests.post(url=url, params=params, files=files,
                                data=data, cookies=cookies, timeout=self._request_timeout)
            self.__errors = 0
            return req
        except Exception as e:
            print(e, ' ', url)
            if self.__errors >= self._max_errors:
                print('Max Error')
                return False
            self.__errors = self.__errors + 1
            time.sleep(self._sleep_time)
            return self.post_with_params_files_data(url, params, files, data, cookies)


def Ceaser(text, shag):
    alf = 'xyz12qrstuvwghij90klmn34abcdefop5678'
    sh = ''
    probel = ' '
    for i in range(0, len(text)):
        for n in range(0, len(alf)):

            if text[i].find(alf[n]) == 0:
                if n + shag > len(alf):

                    while n + shag - len(alf) >= len(alf):
                        shag -= len(alf)
                    sh += alf[n+shag-len(alf)]

                elif n + shag < 0:
                    while n + shag - len(alf) <= 0:
                        shag += len(alf)
                    sh += alf[n+shag-len(alf)]
                else:
                    sh += alf[n+shag]

        if text[i].find(' ') == 0:
            sh += ' '
    return sh


if __name__ == '__main__':
    key = hex(uuid.getnode())

    if Ceaser(key, len(key)) == 'oh0orvvufvz1f':

        ImpData = ImportData()
        PrfEdit = ProfileEdit()
        SteamAccs = ImpData.import_acc()

        for x in SteamAccs:
            print('\nAcc', x[0]+':'+x[1])
            PrfEdit.data_edit(x[0], x[1])
    else:
        print('Invalid API key ' + 'oh0orvvufvz1f')
        input('Press any key')
