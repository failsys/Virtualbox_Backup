#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import logging
import sys
# import copy
import traceback
import subprocess
import os
from time import sleep


def send_message(message: str, chat: str, max_tryes: int, logger, token: str, additional_log_info: str = None) -> int:
    """
    Функция отправляющая текстовое сообщение
    :param str message: текст отправляемого сообщения
    :param str chat: ChatID  куда отправлять
    :param int max_send_tryes: максимальное количество попыток на отправку
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :param str token: токен бота с  помощью которого будут отправляться сообщение
    :param str additional_log_info: дополнительная информация котрорая будет записана в лог перед выполнением функции
    :return int: результат выполнения. 0 - в случае успеха, 1 - неудача
    """
    # fixme Прикрутить условие - использовать тор прокси или нет
    result = 255
    msg_send_state = 2
    msg_send_tryes = 0
    # max_tryes = copy(max_send_tryes)
    while (msg_send_state != 0):
        try:
            c = 'curl --socks5 127.0.0.1:9050 --max-time 9000 --connect-timeout 900 -d chat_id=' + chat + ' -d text="' + message + '"  https://api.telegram.org/bot' + token + '/sendMessage'
            logger.debug('Собираюсь отправить информационное текстовое сообщение')
            if additional_log_info is not None:
                if type(additional_log_info) == str:
                    logger.debug(additional_log_info)
                else:
                    logger.debug('Дополнительная информация для логгера не является строкой и записана не будет')
            logger.debug('Команда которая будет выполнена: ' + str(c) + '\n')
            proc = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE)
            proc.wait()
            out = proc.communicate()
            logger.debug('Подробности отправки информационного текстового сообщения: ')
            logger.debug('Код отправки: ' + str(proc.returncode))
            logger.debug('stdout отправки: ' + str(out[0].decode('utf-8')))
            if out[1] is not None:
                logger.debug('stderr отправки: ' + str(out[1].decode('utf-8')))
            else:
                logger.debug('stderr был пуст')
            if proc.returncode == 0:
                msg_send_state = 0
                result = 0
                if msg_send_tryes == 0:
                    logger.info('информационное текстовое сообщение было успешно отправлено с первой попытки')
                else:
                    logger.info(
                        'информационное текстовое сообщение было отправлено с ' + str(msg_send_tryes + 1) + ' попытки')
                break
            else:
                msg_send_state = 1
            if msg_send_state == 1:
                msg_send_tryes = msg_send_tryes + 1
                logger.info('Попытки отправить информационное текстовое сообщение: ' + str(msg_send_tryes))
                max_tryes = max_tryes - 1
                if max_tryes == 0:
                    result = 1
                    logger.critical('Превышено максимальное количество попыток отправки, заданное '
                                    'в параметрах: ' + str(msg_send_tryes))
                    sys.exit('Превышено максимальное количество попыток отправки, заданное '
                             'в параметрах')
                sleep(10)
                continue
        except Exception as e:
            logger.error('Произошла ошибка отправки сообщения')
            logger.debug('Exception при отправке текстового сообщения, подробности ниже')
            logger.debug('Тип Exception: ' + str(type(e)))
            logger.debug('Аргументы исключения:' + str(e.args))
            # logger.debug('Стэк вызовов: \n' + str(e.with_traceback()))
            logger.debug('Команда использованная для отправки: ' + c)
            logger.debug('Стэк вызовов: ' + str(traceback.format_exc()))
            logger.debug('Код возврата: ' + str(proc.returncode))
            logger.debug('stdout: ' + str(proc.stdout.read().decode('utf-8')))
            if proc.stderr is not None:
                logger.debug('stderr: ' + str(proc.stderr.read().decode('utf-8')))
            sys.exit('Произошла ошибка при отправке сообщения')
        finally:
            proc.kill()
            return result


def send_files(files: tuple, logger, max_tryes: int, chat: str, token: str) -> int:
    """
    Функция отправляющая указанные файлы в чат
    :param tuple files: массив файлов, тип каждого элемента str
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :param int max_tryes: максимальное количество попыток на отправку
    :param str chat: ID чата куда отправлять
    :param str token: token бота с помощью которого отправлять
    :return int: результат выполнения. В случае успеха 0, в случае неудачи  1
    """
    result = 255
    not_uploaded = []
    logger.info('Всего файлов к отправке: ' + str(len(files)))
    logger.info('Начинаю отправку файлов....')
    # fixme Добавить уведомление в случае облома
    total = len(files)
    sent = 0
    for file in files:
        # На случай если понадобится менять identity у  tor
        # with Controller.from_port(port=9050) as controller:
        #     controller.signal(Signal.NEWNYM)

        file_send_state = 2
        file_send_tryes = 0
        while (file_send_state != 0):
            if not os.path.isfile(file):
                logger.critical('Файл ' + file + ' не найден, но числится  в массиве')
                logger.debug('Поиск производился: ' + str(os.getcwd()) + '\n')
            logger.debug('\n\n\nСобираюсь отправить файл ' + file)
            cmd = 'curl --socks5 127.0.0.1:9050 --max-time 9000 --connect-timeout 900 ' \
                  '-F document=@"' + file + '" https://api.telegram.org/bot' + token + '/sendDocument?chat_id=' + chat
            # #cmd = 'curl --socks5 127.0.0.1:9050 --max-time 9000 --connect-timeout 900 ' \
            #       '-F document=@"' + file + '" https://api.telegram.org/bot888746107:AAGNg4KGik97AkmHnbDQeGUrlG57Qjb7B1c/' \
            #                                 'sendDocument?chat_id=-341753010'
            logger.debug('Команда на выполнение для отправки файлов: ' + cmd + '\n')
            logger.debug('Значение в file: ' + file + '\n')
            if os.path.exists(file):
                logger.debug('Файл существует ' + file + '\n')
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.wait()
                # logger.info('Собираюсь отправить файл: ' + file + '\n')
                # logger.debug('С помощью команды: \n' + cmd + '\n')
                out = proc.communicate()
                if out[0] is not None:
                    logger.debug('stdout для отправки: ' + str(out[0].decode('utf-8')))
                if out[1] is not None:
                    logger.debug('stderr для отправки: ' + str(out[1].decode('utf-8')))
                if proc.returncode == 0:
                    file_send_state = 0
                    sent = sent + 1
                    logger.info('Файлов успешно отправлено на текущий момент: ' + str(sent))
                    logger.info('Осталось отправить файлов: ' + str(total - sent))
                    if file_send_tryes > 0:
                        logger.info(
                            'Файл ' + file + 'был  успешно отправлен  с ' + str(file_send_tryes + 1) + ' попытки')
                    else:
                        logger.info(' Файл ' + file + ' был успешно отправлен с первой попытки')
                        proc.kill()
                    break
                else:
                    not_uploaded.append(file)
                    logger.critical('Файл ' + file + ' не удалось отправить, curl вернул ' + str(proc.returncode))
                    # logger.critical('Файлов неудачно отправлено на текущий момент: ' + str(len(not_uploaded)))
                    file_send_state = 1
                    file_send_tryes = file_send_tryes + 1
                    max_tryes = max_tryes - 1
                    if max_tryes == 0:
                        logger.critical(
                            'Превышено максимальное количество попыток отправки, указанное в конфигурации:' +
                            str(max_tryes))
                        result = 1
                        sys.exit(1)
                    logger.info('Попыток отправки для этого файла: ' + str(file_send_tryes))
                    logger.debug('Этот текст читаем ?')
                    logger.debug('Код отправки файла: ' + str(proc.returncode))
                    logger.debug('stdout отправки файла: ' + file + '\n' + str(out[0].decode('utf-8')))
                    if out[1] is not None:
                        logger.debug('stderr отправки файла: ' + file + '\n' + str(out[1].decode('utf-8')))
                    sleep(10)
                    proc.kill()
                    continue
            except Exception as e:
                logger.debug('Случился Exception, ниже инфа о нем:' + '\n')
                logger.debug('тип случившегося исключения: ' + str(type(e)) + '\n')
                logger.debug('Аргументы исключения: ' + str(e.args) + '\n')
                logger.critical('Произошла неизведанная хуйня(' + str(type(e)) + '), чтобы узнать подробности нужно '
                                                                                 'включить уровень DEBUG для логгирования \n')
                pass
    return result


def clear_folder(dir_name: str, logger, force=False) -> int:
    """ функция удаляющая созданный образ ova из указанной папки и архивы из нее же
    :param str dir_name: Директория откуда нужно удалить файлы
    :param logging.handlers.RotatingFileHandler logger: logger куда записывать о результатах
    :param bool force: если укзать True будет использован параметр -f  для rm, по умолчанию False
    :return: В случае успеха - 0,  в случае если не удалось удалить образ ova, но удалось удалить архивы - 1, в
    случае если не удалось удалить ничего - 2
    """
    result = 255
    if os.path.isdir(dir_name):
        logger.info('Директория для удаления файлов обнаружена, перехожу в директорию для зачистки')
        os.chdir(dir_name)
    else:
        logger.error('Не удалось удалить файлы, так как была указана некорректная директоррия')
        sys.exit('Указана некорректная директория для удаления файлов')
    if not force:
        cmd = 'rm -r  ./*.ova'
    else:
        cmd = 'rm -rf ./*.ova'
    logger.info('Приступаю к удалению файла образа в директории: ' + str (os.getcwd()))
    logger.debug('C помощью команды: ' + cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out = proc.communicate()
    if proc.returncode == 0:
        logger.info('Файл образа был успешно удален')
        result = 254
    logger.debug('Код возврата для операции удаления образа: ' + str(proc.returncode) + '\n')
    logger.debug('stdout операции удаления образа: ' + str(out[0].decode('utf-8')))
    if out[1] is not None:
        logger.debug('stderr операции удаления образа' + str(out[1].decode('utf-8')))
    else:
        logger.debug('stderr операции удаления образа был пустым')
    proc.kill()
    logger.debug('Собираюсь удалить файлы ./*.tar.bz* в директории ' + dir_name + '\n')
    logger.info('Проверяю наличие директории')
    if os.path.isdir(dir_name):
        logger.info('Директория обнаружена')
        os.chdir(dir_name)

    if not force:
        cmd = 'rm -r  ./*.tar.bz*'
    else:
        cmd = 'rm -rf ./*.tar.bz*'
    logger.debug('Команда которая будет использована для удаления: ' + cmd)
    logger.info('Приступаю к удалению...')
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    proc.wait()
    out = proc.communicate()
    if proc.returncode == 0:
        logger.info('Удаление архивов прошло успешно')
        if result == 254:
            result = 0
        if result == 255:
            result = 1
    else:
        result = 2
    logger.debug('Код возврата для операции удаления: ' + str(proc.returncode) + '\n')
    logger.debug('stdout операции удаления архивов' + str(out[0].decode('utf-8')))
    if out[1] is not None:
        logger.debug('stderr операции удаления архивов; \n' + str(out[1].decode('utf-8')))
    else:
        logger.debug('stderr операции удаления архивов был пустым')
    proc.kill()
    return result


def main(*args, **kwargs):
    print('Этот файл не предназначен для самостоятельного запуска')
    print('Используйте import telegramAPI...')


if __name__ == '__main__':
    main()
    sys.exit('Неправильное использование модуля')
