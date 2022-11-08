import requests as r
import json
import time
import io
import Levenshtein
import pandas as pd
import threading
from threading import Thread
import csv
from random import choice
import random
import colorama
from colorama import Fore, Back, Style

colorama.init()


def func_get(chat_id, usertoken):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    rg = s.get(f'https://discord.com/api/v8/channels/{chat_id}/messages', headers=header)
    jsn = json.loads(rg.text)
    return jsn


def func_get_userid(chat_id, usertoken, position):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    rg = s.get(f'https://discord.com/api/v8/channels/{chat_id}/messages', headers=header)
    jsn = json.loads(rg.text)
    return jsn[position]['author']['id']


def func_get_username(chat_id, usertoken, position):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    rg = s.get(f'https://discord.com/api/v8/channels/{chat_id}/messages', headers=header)
    jsn = json.loads(rg.text)
    return jsn[position]['author']['username']


def func_post(chat_id, message, usertoken, message_reference):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    _data = {'content': message, 'tts': False, 'message_reference': message_reference}
    s.post(f'https://discord.com/api/v9/channels/{chat_id}/messages', json=_data).json()


def func_post_withtyping(chat_id, message, usertoken, message_reference, typing_time):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    _data = {'content': message, 'tts': False, 'message_reference': message_reference}
    s.post(f'https://discord.com/api/v9/channels/{chat_id}/typing')
    time.sleep(typing_time)
    s.post(f'https://discord.com/api/v9/channels/{chat_id}/messages', json=_data).json()


def func_post_tome(user_name, chat_name, wnum, usertoken):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    message = f'Detect mention of bot user: "{user_name}" chat: "{chat_name}"'
    _data = {'content': message, 'tts': False}
    s.post(f'https://discord.com/api/v9/channels/{wnum}/messages', json=_data).json()


def func_delete(usertoken, chat_id, message_id, timing):
    header = {
        'authorization': usertoken
    }
    s = r.Session()
    s.headers = header
    time.sleep(timing)
    s.delete(f'https://discord.com/api/v9/channels/{chat_id}/messages/{message_id}')

def main(j):

    i = int(j)
    global array_chats_first
    global array_users_first
    global array_chats_last
    global array_users_last

    global bot_exam
    global warningchat_num

    global msg_set
    global user_token_set
    global chat_set
    global user_chatid_set

    global total_sent
    global chat_name

    global delete_marker
    global delete_timing

    global spam_marker
    global spam_delete_marker
    global spam_delete_timing

    global typing_marker
    global typing_timing

    user_number = random.randint(array_users_first[i], array_users_last[i] - 1)
    user_token = user_token_set[user_number]

    for x in range(array_chats_first[i], array_chats_last[i]):
        chat_number = x
        current_chat_id = chat_set[chat_number]

        current_user_id = user_chatid_set[user_number]
        print(Fore.LIGHTBLUE_EX + f'Scanning {i + 1} project {chat_number + 1} chat from user {user_number + 1}')

        chat_new_message_jsn = func_get(current_chat_id, user_token)
        try:
            chat_new_message = chat_new_message_jsn[0]['content']
        except Exception:
            print(Fore.MAGENTA + '*** Some problems with get_message ***')
            continue
        new_user_id = chat_new_message_jsn[0]['author']['id']
        new_username = chat_new_message_jsn[0]['author']['username']

        database_trigger = 0
        if new_user_id != current_user_id:
            for i in range(0, 4):
                for value in bot_exam:
                    if value in chat_new_message:
                        with open('all_chats.csv') as csv_file:
                            file_chats = csv.reader(csv_file, delimiter='|')
                            for row in file_chats:
                                if row[0] == current_chat_id:
                                    chat_name = row[1]
                                    break
                        func_post_tome(new_username, chat_name, warningchat_num, user_token)
                        print(Fore.LIGHTRED_EX)
                        print('** ** ** ** ** ** ** ** ** ** ** ** ** ** **')
                        print('** ** ** ** ** ** ** ** ** ** ** ** ** ** **')
                        print('** ** ** ** ** ** ** ** ** ** ** ** ** ** **')
                        print('      									   ')
                        print('** ** ** ** ** ** ** ** ** ** ** ** ** ** **')

            print(Fore.LIGHTGREEN_EX)
            print(f'New message in "{chat_name}" chat: "{chat_new_message}"')

            with io.open('chatbot_dataset.csv', encoding='utf-8') as csv_file:
                file_reader = csv.reader(csv_file, delimiter="|", quoting=csv.QUOTE_NONE)
                ratio_list = []

                for row in file_reader:
                    if Levenshtein.ratio(chat_new_message, row[0]) >= 0.7:
                        ratio_list.append(str(row[1]))

                if ratio_list:
                    output_message = choice(ratio_list)
                    message_reference = {
                        'channel_id': chat_new_message_jsn[0]['channel_id'],
                        'message_id': chat_new_message_jsn[0]['id']
                    }
                    # reply_timeout = random.randint(2, 4)
                    # time.sleep(reply_timeout)
                    if typing_marker == 0:
                        try:
                            post_thread = threading.Thread(
                                target=func_post(current_chat_id, output_message, user_token, message_reference),
                                name='post_msg')
                            post_thread.start()
                        except Exception:
                            continue
                    elif typing_marker == 1:
                        try:
                            post2_thread = threading.Thread(
                                target=func_post_withtyping(current_chat_id, output_message, user_token,
                                                            message_reference, typing_timing), name='post2_msg')
                            post2_thread.start()
                        except Exception:
                            continue
                    print('*** I think I found the answer in the database and posted the answer: ***')
                    print(output_message)
                    print()
                    total_sent += 1
                    database_trigger = 1

                    if delete_marker == 1:
                        try:
                            chat_messages_fordel = func_get(current_chat_id, user_token)
                        except Exception:
                            continue
                        delete_find_marker = 0
                        for i in range(10):
                            if chat_messages_fordel[i]['author']['id'] == current_user_id:
                                message_id_delete = chat_messages_fordel[i]['id']
                                delete_find_marker = 1
                                break
                        if delete_find_marker == 1:
                            delete_thread = threading.Thread(target=func_delete, name='delete_msg', args=(
                            user_token, current_chat_id, message_id_delete, delete_timing))
                            delete_thread.start()

            if database_trigger == 0 and spam_marker == 1:
                msg = choice(msg_set)
                message_reference = {
                    'channel_id': chat_new_message_jsn[0]['channel_id'],
                    'message_id': chat_new_message_jsn[0]['id']
                }
                # reply_timeout = random.randint(2, 4)
                # time.sleep(reply_timeout)
                if typing_marker == 0:
                    try:
                        post_thread = threading.Thread(
                            target=func_post(current_chat_id, msg, user_token, message_reference), name='post_msg')
                        post_thread.start()
                    except Exception:
                        continue
                elif typing_marker == 1:
                    try:
                        post2_thread = threading.Thread(
                            target=func_post_withtyping(current_chat_id, msg, user_token, message_reference,
                                                        typing_timing), name='post2_msg')
                        post2_thread.start()
                    except Exception:
                        continue
                print('*** I dont found the answer in the database and posted the answer: ***')
                print(msg)
                print()
                total_sent += 1

                if spam_delete_marker == 1:
                    try:
                        spam_chat_messages_fordel = func_get(current_chat_id, user_token)
                    except Exception:
                        continue
                    spam_delete_find_marker = 0
                    for i in range(10):
                        if spam_chat_messages_fordel[i]['author']['id'] == current_user_id:
                            spam_message_id_delete = spam_chat_messages_fordel[i]['id']
                            spam_delete_find_marker = 1
                            break
                    if spam_delete_find_marker == 1:
                        spam_delete_thread = threading.Thread(target=func_delete, name='spam_delete_msg', args=(
                        user_token, current_chat_id, spam_message_id_delete, spam_delete_timing))
                        spam_delete_thread.start()


print(Fore.LIGHTGREEN_EX)
print('''
                               ....
                                    %
                            L
                            "F3  $r
                           $$$$.e$"  .
                           "$$$$$"   "
   (FovTextBot)              $$$$c  /
        .                   $$$$$$$P
       ."c                      $$$
      .$c3b                  ..J$$$$$e
      4$$$$             .$$$$$$$$$$$$$$c
       $$$$b           .$$$$$$$$$$$$$$$$r
          $$$.        .$$$$$$$$$$$$$$$$$$
           $$$c      .$$$$$$$  "$$$$$$$$$r

    
*** Hello, I'm FovTextBot, for my work fill the files:
 	user_tokens.txt, chat_to_sent.txt, user_chat_id.txt, 
 	all_chats.csv, give me the dictionary of questions/answers 
 	as chatbot_dataset.csv and pool of random messages 
 	as bot_messages.txt (you can change it by add strings in
 	file) ***
''')
print(Fore.LIGHTWHITE_EX)

array_chats_first = []
array_users_first = []
array_chats_last = []
array_users_last = []

bot_exam = ['bot', 'Bot', 'BOT', 'b0t', 'auto', 'aut0', 'spam', 'SPAM']

project_num = int(input('Enter the number of threads: '))
for i in range(0, project_num):
    u1 = int(input(f'Enter the number of first user in {i+1} project: '))
    u1 -= 1
    array_users_first.append(u1)
    u2 = int(input(f'Enter the number of last user in {i+1} project: '))
    array_users_last.append(u2)
    c1 = int(input(f'Enter the number of first chat in {i+1} project: '))
    c1 -= 1
    array_chats_first.append(c1)
    c2 = int(input(f'Enter the number of last chat in {i+1} project: '))
    array_chats_last.append(c2)
warningchat_num = int(input('Enter the id of warning chat: '))

msg_set: list = open('bot_messages.txt', 'r', encoding='utf-8').read().splitlines()
user_token_set: list = open('user_tokens.txt', 'r', encoding='utf-8').read().splitlines()
chat_set: list = open('chat_to_sent.txt', 'r', encoding='utf-8').read().splitlines()
user_chatid_set: list = open('user_chat_id.txt', 'r', encoding='utf-8').read().splitlines()

delay = int(input('Enter a delay for sending messages: '))
total_sent = 0
chat_name = 0

delete_marker = int(input('Delete messages from database after sending? (1/0): '))
if delete_marker == 1:
    delete_timing = int(input('Set timing for delete database messages in secs: '))

spam_marker = int(input('Sent spam messages if there no answer in database (1/0): '))
if spam_marker == 1:
    spam_delete_marker = int(input('Delete spam messages after sending? (1/0): '))
    if spam_delete_marker == 1:
        spam_delete_timing = int(input('Set timing for delete spam messages in secs: '))

typing_marker = int(input('Imitate typing before sending message? (1/0): '))
if typing_marker == 1:
    typing_timing = int(input('Set typing time in secs (1-10): '))



print()
print('*** Successful scanning of chats ***')
print()

print('*** I start checking out the changes. ***')
print()

main_thread = []

while True:

    for i in range(0, project_num):
        j = f'{i}'
        main_thread.append(threading.Thread(target=main, name=f'thread{i}', args=(j)))
        main_thread[i].start()
        #print()
        #print(Fore.LIGHTRED_EX + f'поток {i} проснулся')
    for i in range(0, project_num):
        main_thread[i].join()
        #print()
        #print(Fore.LIGHTRED_EX + f'поток {i} схлопнулся')
    main_thread = []
    print(Fore.LIGHTWHITE_EX + f'*** Total sent {total_sent} messages ***')
    print()
    time.sleep(delay)