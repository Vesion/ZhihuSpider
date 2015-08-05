﻿#  ________      ______                   
#  ___  __/_____ ___  /__________________ 
#  __  /_ _  __ `/_  /_  ___/  __ \_  __ \
#  _  __/ / /_/ /_  / / /__ / /_/ /  / / /
#  /_/    \__,_/ /_/  \___/ \____//_/ /_/ 
#                              
# Author : Shine Xu
# License: The MIT License (MIT)

# -*- coding: utf-8 -*-

import time
import ConfigParser

from .Utils import *

class Session():
    """ 
    Fundamental class instantiated to initiate and maintain an HTTP session.
    APIs: login, logout, get ,post
    Wrappers: set/get[Header], set/get[Cookie], set/get[Config]
    """

    def __init__(self):
        self.__session = requests.session()
        self.__config = self.getConfig()

    def setHeader(self, headers):
        for key, value in headers.items():
            self.__session.headers[key] = value

    def getHeader(self):
        return self.__session.headers

    def setCookie(self, cookies):
        for key, value in cookies.items():
            self.__session.cookies[key] = value

    def getCookie(self):
        return self.__session.cookies

    def setConfig(self, section, options):
        for key, value in options.items():
            self.__config.set(section, key, value)
        with open('config.ini', 'wb') as configfile:
            self.__config.write(configfile)

    def getConfig(self):
        cf = ConfigParser.ConfigParser()
        cf.read('config.ini')
        return cf
    
    def get(self, url, params = {}):
        return self.__session.get(url, params = params)

    def post(self, url, data = {}):
        return self.__session.post(url, data = data)
    

    def login(self):
        '''
        Login Zhihu, identify the user through email and pwd.
        Perhaps, the captcha need to be input.
        This method MUST be called before any other entry requests.
        '''

        # closure function for sending post
        def login_post(data):
            rsp = self.post(Login_URL, data = data)
            return rsp.json()['r'], rsp.json()['msg']
        
        # closure function for getting captcha image
        def get_captcha():
            params = {'r' : str(int(time.time() * 1000))}
            rsp = self.__session.get(Get_Captcha_URL, params = params, stream = True)
            if rsp.status_code == 200:
                with open('captcha.gif', 'wb') as f:
                    rsp.raw.decode_content = True
                    shutil.copyfileobj(rsp.raw, f)

        # prepare post header, cookie and data
        self.setHeader(dict(self.__config.items('header')))
        self.setCookie(dict(self.__config.items('cookie')))
        data = {
                'email'       : self.__config.get('info', 'email'),
                'password'    : self.__config.get('info', 'password'),
                'remember_me' : 'true'
            }
        
        # try to login with cookie
        code, msg = login_post(data)
        # if fail, input captcha
        while code == 1:
            print msg
            print "Getting captcha..."
            get_captcha()
            captcha = raw_input("Input captcha:\n")
            data['captcha'] = captcha
            code, msg = login_post(data)

        print "Login successfully."
        self.setConfig('cookie', self.__session.cookies)

    def logout(self):
        rsp = self.get(Logout_URL)
        if rsp.status_code == requests.codes.ok:
            print "Logout successfully."
            #self.setConfig('cookie', self.__session.cookies)
        else:
            print "Logout failed : {0}".format(rsp.status_code)



if __name__ == "__main__":
    s = Session()
    s.login()
    s.logout()
    
