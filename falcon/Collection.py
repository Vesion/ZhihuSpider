﻿#  ________      ______                   
#  ___  __/_____ ___  /__________________ 
#  __  /_ _  __ `/_  /_  ___/  __ \_  __ \
#  _  __/ / /_/ /_  / / /__ / /_/ /  / / /
#  /_/    \__,_/ /_/  \___/ \____//_/ /_/ 
#                              
# Author : Shine Xu
# License: The MIT License (MIT)

# -*- coding: utf-8 -*-

from .Utils import *
from .Entry import Entry

class Collection(Entry):
    """ Tool class for getting collection info. """

    def __init__(self, session, eid):
        Entry.__init__(self, session, eid)

    def get_title(self):
        """ Return title text. """
        return self.soup.find('h2', id = 'zh-fav-head-title')\
                        .get_text(strip = True).encode(CODE)

    def get_creator(self):
        """ Return creator eid. """
        return self.soup.find('h2', class_ = 'zm-list-content-title')\
                        .a['href']

    def get_questions(self):
        """ Return generator with question. """
        questions = self.soup.find_all('div', class_ = 'zm-item')
        if not questions:
            return
        i, question = 0, None
        for question in questions:
            i += 1
            yield question.h2.a['href']
        while True:
            params = {'page' : i / Page_Items_Num + 1}
            rsp = self.session.get(self.url, params = params)
            soup = self.getSoup(rsp.content)
            questions = soup.find_all('div', clas_ = 'zm-item')
            if questions:
                for question in questions:
                    i += 1
                    yield question.h2.a['href']
            else:
                return

    def get_answers(self):
        """ Return generator with answer. """
        answers = self.soup.find_all('div', class_ = 'zm-item')
        if not answers:
            return
        i, answer = 0, None
        for answer in answers:
            i += 1
            yield answer.find('a', class_ = 'answer-date-link')['href']
        while True:
            params = {'page' : i / Page_Items_Num + 1}
            rsp = self.session.get(self.url, params = params)
            soup = self.getSoup(rsp.content)
            answers = soup.find_all('div', clas_ = 'zm-item')
            if answers:
                for answer in answers:
                    i += 1
                    yield answer.find('a', class_ = 'answer-date-link')['href']
            else:
                return

    def get_all_questions(self):
        """ Return a [list] of question eids. """
        return get_all_(self.get_questions)

    def get_all_answers(self):
        """ Return a [list] of answer eids. """
        return get_all_(self.get_answers)

    def get_num_followers(self):
        """ Return number of followers int. """
        num = self.soup.find('a', href = self.eid + "/followers")\
                        .get_text(strip = True).encode(CODE)
        num = Number_RE.match(num).group(1)
        return int(num)

    def get_followers(self):
        """ A generator yields a user eid per next(). """
        rsp = self.session.get(self.url + "/followers")
        soup = self.getSoup(rsp.content)
        followers = soup.find_all('div', class_ = 'zm-profile-card zm-profile-section-item zg-clear no-hovercard')
        if not followers:
            return
        i, follower = 0, None
        for follower in followers:
            i += 1
            yield follower.a['href']
        while not i % Page_Items_Num:
            data = {
                    'offset' : i,
                    '_xsrf'  : self.session.getCookie()['_xsrf']
                }
            rsp = self.session.post(self.url + "/followers", data = data)
            if rsp.json()['r'] == 0:
                followers = self.getSoup(rsp.json()['msg'][1])\
                        .find_all('div', class_ = 'zm-profile-card zm-profile-section-item zg-clear no-hovercard')
                for follower in followers:
                    i += 1
                    yield follower.a['href']
            else:
                return

    def get_all_followers(self):
        """ Return a [list] of user eids. """
        return get_all_(self.get_followers)

    def follow_it(self):
        """ Follow this collection. Return status code. """
        favlist_id = self.soup.find('div', id = 'zh-list-side-head')\
                                .a['id'].split('-')[-1]
        data = {
            'favlist_id' : favlist_id,
            '_xsrf'      : self.session.getCookie()['_xsrf']
            }
        rsp = self.session.post(Follow_Collection_URL, data)
        if rsp.status_code == requests.codes.ok:
            print "Follow this collection successfully!"
            return SUCCESS
        else:
            print "Fail to follow this collection"
            return FAILURE
