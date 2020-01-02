#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import subprocess
#import telebot
import os
import datetime
import logging
import logging.handlers
import sys
import traceback

import virtualbox_api
import telegramAPI
import config

# Этот импорт нужен для смены identity у tor
#from stem import Signal
#from stem.control import Controller
#Проверить надо бы после пересоздания  ВМ


def log_init(logpath: str):
    """
    Функция инициализции системы логирования
    :param str logpath: Где хранить логи
    :return: logger logging.handlers.RotatingFileHandler(
    """
    print('Пробую создать логгер')
    try:
        logger = logging.getLogger()
        logger.setLevel(config.log_level)
    except Exception as e:
        # fixme добавить опцию изменения логов
        sys.exit('Что-то пошло не так при создании логгера')

    # create the logging file handler
    # fh = RotatingFileHandler('./export.log', maxBytes=10485760, backupCount=1)
    logpath = str(logpath)
    if  not logpath.endswith('/'):
        logpath = logpath + '/'
    print('Инициализирую лог по пути: ' + logpath + '/export.log')
    try:
        fh = logging.handlers.RotatingFileHandler(logpath + '/export.log', maxBytes=10485760, backupCount=1)
    except Exception as e:
        print('Произошел Exception при инициализации лога типа ' + str(type(e)))
        print('Аргументы Exception ' + str(e.args))
        print('Traceback: ')
        traceback.print_exc()
        sys.exit('Что-то с логгером не то')

    try:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
    except Exception as e:
        print('Произошел Exception при установке формата лога. Тип Exception: ' + str(type(e)))
        print('Аргументы Exception: ' + str(e.args))
        print('Traceback: ')
        traceback.print_exc()
        sys.exit('Что-то не так при установке форматтера логгера')

    # add handler to logger object
    try:
        logger.addHandler(fh)
    except Exception as e:
        print('Произошел Exception при добавлении хендлера логгера')
        print('Тип Exception: ' + str(type(e)))
        print('Аргументы Exception: ' + str(e.args))
        print('Traceback: ')
        traceback.print_exc()
        sys.exit('Что-то не так при добавлении хендлера логгера')
    print('Пробую создать первую запись в  логе')
    try:
        logger.info("Main started")
        logger.info('<<<<<------!!!!!!!!    Запуск произошел  ' + str((datetime.datetime.now().strftime('%d/%m/%y')))
                    + ' в ' + str(datetime.datetime.now().time().strftime('%X')) + '    !!!!!!!!------>>>>>>>\n')
    except Exception as e:
        print('Произошел Exception при создании первой записи в логе')
        print('Тип Exception: ' + str(type(e)))
        print('Аргументы Exception: ' + str(e.args))
        print('Traceback: ')
        traceback.print_exc()
        sys.exit('Что-то пошло не так при создании первой записи в  логе')
    print('Запись в  логе создана, лог-файл инициализирован.')
    return logger



def main():
    logger = log_init(config.dir_name)
    virtualbox_api.turn_off_vm(config.VM_NAME,logger)
    virtualbox_api.take_snapshot(config.VM_NAME,logger)
    virtualbox_api.export_vm(config.VM_NAME, logger, config.dir_name)
    virtualbox_api.start_vm(config.VM_NAME,logger)
    # archs = make_archives(dir_name, logger)
    archs = virtualbox_api.make_archives(logger,config.VM_NAME, config.dir_name)
    # send_files(archs,max_send_tryes,chat,token)
    # telegramAPI.send_message(config.msg,10,logger,config.token)
    logInf= 'Собираюсь отправить сообщение перед отправкой архивов'
    telegramAPI.send_message(config.msg, config.chat, config.max_send_tryes, logger, config.token, logInf)
    telegramAPI.send_files(archs,logger,config.max_send_tryes, config.chat, config.token)
    logInf = 'Собираюсь отправить сообщение с инструкциями по распаковке'
    telegramAPI.send_message(config.unpack_instruction, config.chat, config.max_send_tryes, logger, config.token, logInf)
    txt = 'Конец архива с  ' + config.VM_NAME + ' от ' + str((datetime.datetime.now().strftime('%d/%m/%y')))
    logInf = 'Собираюсь отправить сообщение о конце архива'
    telegramAPI.send_message(txt, config.chat, config.max_send_tryes, logger, config.token, logInf)
    telegramAPI.clear_folder(config.dir_name, logger)






    # send_files(archs, logger)
    logger.info('<<<<--------!!!!!!!    Закончили в ' + str(datetime.datetime.now().strftime('%X')) +
                '!!!!!!!-------->>>>>>>\n')
# Создание многотомного архива
#  tar -cvpj './expermental.ova'/ | split -d -b 1000m - a rchive.tar.bz2
# tar -cvpj 'directory/name'/ | split -d -b 4000m - /name/of/archive.tar.bz2.
# cat *.ova.tar.bz2*  > xbackup.tar.gz.joined
# type your code here

if __name__ == '__main__':
    main()
