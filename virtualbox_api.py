#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import logging
import subprocess
import datetime
import traceback
import sys
import os
import glob


def turn_off_vm(VM_NAME: str, logger) -> int:
    """ Функция выключения виртуальной машины.
    :param str VM_NAME: Имя виртуальной машины которую будем выключать
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :return int:  результат выполнения. В случае успеха - 0, 3 - если ВМ была уже выключена, 2 в случае других ошибок
    """
    try:
        cmd = 'vboxmanage controlvm ' + VM_NAME + ' poweroff soft'
        # if not os.path.exists(dir_name):
        #     os.mkdir(dir_name)
        # os.chdir(dir_name)
        # cmd= 'vboxmanage list vms'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        if process.returncode == 0:
            logger.info('Выключение виртуальной машины прошло успешно')
            result = 0
        else:
            logger.critical('Что-то пошло не так при выключении ВМ')
        logger.debug('Выключение виртуальной машины завершилось с кодом: ' + str(process.returncode))
        logger.debug('Подробности выключения ВМ: \n')
        out = process.communicate()
        result = 1
        logger.debug('stdout операции выключения: ' + str(out[0].decode('utf-8')))
        if out[1] is not None:
            if ' is not currently running' in str(out[1].decode('utf-8')):
                logger.critical('ВМ была выключена на этот момент')
                result = 3
            logger.debug('stderr выключения: ' + str(out[1].decode('utf-8')))
        else:
            logger.debug('stderr выключения был None')
        process.kill()
    except Exception as e:
        logger.error('Произошла ошибка при выключении ВМ')
        logger.debug('Тип Exception: ' + str(type(e)))
        logger.debug('Аргументы Exception: ' + str(e.args))
        logger.debug(traceback.format_exc())
        result = 1
        pass
    return result


def take_snapshot(VM_NAME: str, logger) -> int:
    """
    Функция создающая снимок виртуальной машины
    :param str VM_NAME: Имя виртуальной машины с которой делаем снимок
    :param logging.handlers.RotatingFileHandler logger:  логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :return int: результат выполнения операции. 0 -  в случае успеха, 1 в случае ошибок
    """
    try:
        dt = str((datetime.datetime.now().date()).strftime('%d/%m/%Y'))
        cmd = 'vboxmanage snapshot ' + VM_NAME + ' take {snapshot_before_export_' + dt + '} --description \"' \
                                                                                         'Снимок виртуальной машины перед ее экспортом, сделанный ' + dt + ' в ' + \
              str(datetime.datetime.now().time().strftime('%X')) + '\"'
        logger.debug('Собираюсь создать снимок виртуальной машины с помощью команды: ' + cmd)
        # proccess = None
        proccess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proccess.wait()
        out = proccess.communicate()
        if proccess.returncode == 0:
            logger.info('Снимок виртуальной машины создан успешно')
            result = 0
        else:
            logger.critical('Снимок виртуальной машины не успешен!')
            result = 1

        if out[0] is not None:
            logger.debug('stdout для создания снимка виртуальной машины: ' + str(out[0].decode('utf-8')))
        if out[1] is not None:
            logger.debug('stderr для создания снимка виртуальной машины' + str(out[1].decode('utf-8')))
    except Exception as e:
        logger.error('Произошла ошибка при создании снимка виртуальной машины')
        logger.debug('тип Exception: ' + str(type(e)))
        logger.debug('Аргументы Exception: ' + str(e.args))
        logger.debug('Traceback: ' + str(traceback.format_exc()))
        result = 1
        pass
    finally:
        proccess.kill()
    return result


def export_vm(VM_NAME: str, logger, dir_name: str, timeout=2400) -> str:
    """
    функция экспортирующая виртуальную машину
    :param str VM_NAME: Имя виртуальной машины которую экспортируем
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :param int timeout: таймаут ожидания экспорта, по умолчанию 2400 секунд
    :return str: имя файла созданного образа
    """
    # fixme добавить возможность изменения пути для экспортируемого образа
    try:
        cmd = 'vboxmanage export ' + VM_NAME + ' -o ' + VM_NAME +  '.ova'
        os.chdir(dir_name)
        logger.info('Собираюсь произвести экспорт виртуальной машины: ' + VM_NAME + ' в файл: ' + VM_NAME + '.ova')
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait(timeout=timeout)
        if process.returncode == 0:
            logger.info('Экспорт ВМ прошел успешно')
            result = 0
        else:
            logger.critical('При экспорте ВМ произошли ошибки')
            result = 1
        logger.debug('Проверяю существует ли файл: ' + VM_NAME + '.ova')
        if os.path.isfile(VM_NAME + '.ova'):
            logger.info('Файл ' + VM_NAME + '.ova обнаружен')
        logger.debug('Экспорт виртуальной машины завершилось с  кодом: ' + str(process.returncode))
        logger.debug('подробности экспорта ВМ ниже: \n')
        out = process.communicate()
        logger.debug('stdout  экспорта ниже: \n' + str(out[0].decode('utf-8')))
        if out[1] is not None:
            logger.debug('stderr экспорта ниже: \n' + str(out[1].decode('utf-8')))
            if 'VERR_ALREADY_EXISTS' in str(out[1].decode('utf-8')):
                logger.critical('При экспорте виртуальной машины произошла ошибка, файл с таким именем уже существует')
                # fixme удалить созданный ранее образ и пересоздать его

        logger.debug('Проверяю существование файла с образом')
        if os.path.isfile(VM_NAME + '.ova'):
            logger.info('Файл ' + VM_NAME + '.ova обнаружен после функции экспорта')
        process.kill()
    except Exception as e:
        logger.error('Произошел Exception при экспорте виртуальной машины')
        logger.debug('Тип произошедшего Exception: ' + str(type(e)))
        logger.debug('Аргументы произошедшего Exception: ' + str(e.args))
        logger.debug('стэк вызовов: ' + traceback.format_exc())
        sys.exit('Произошла ошибка при экспорте виртуальной машины')
    return VM_NAME +  '.ova'


def get_state_vm(VM_NAME: str, logger) -> int:
    """Функция проверки включена ли виртуальная машина
    :param str VM_NAME: Имя проверяемой виртуальной машины
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :return int: результат выполнения. 0 - в случае если с вм включена, 1 - вм не включена
    """
    try:
        result = 255
        cmd = 'vboxmanage showvminfo ' + VM_NAME +' | grep State'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        out = process.communicate()
        if 'running' in str(out[0].decode('utf-8')):
            logger.info('Виртуальная машина работает')
            result = 0
        else:
            logger.critical(' виртуальная машина не работает')
            result = 1
        logger.debug('stdout запуска: ' + str(out[0].decode('utf-8')))
        if out[1] is not None:
            logger.debug('stderr запуска: ' + str(out[1].decode('utf-8')))
            # logger.info('Состояние виртуальной машины после экспорта: ' + str(process.stdout.read().decode('utf-8')))
        process.kill()
    except Exception as e:
        logger.error('Произошла ошибка при проверке состояния ВМ')
        logger.debug('Тип Exception: ' + str(type(e)))
        logger.debug('Аргументы Exception: ' + str(e.args))
        logger.debug('Traceback: ' + traceback.format_exc())
        result = 1
        pass
        return result
    # elif vagrant == 1:


def start_vm(VM_NAME: str, logger, vagrant=0, vagrant_Working_directory = None) -> int:
    """
    Функция запускающуая виртуальную  машину
    :param str VM_NAME: имя виртуальной машины
    :param logging.handlers.RotatingFileHandler logger: логгер, фиксирующий события в процессе запуска
    :param int vagrant: использовать ли вагрант для запуска, 0 - нет, 1 - да
    :param str vagrant_Working_directory: Директория где будет находится файл Vagrantfile
    :return int: результат выполнения, 0 - если все успешно
    """
    result = 255
    if vagrant == 0:
        cmd = 'vboxmanage startvm ' + VM_NAME + ' --type headless'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        if process.returncode == 0:
            logger.info('Запуск виртуальной машины прошел успешно')
            result = 0
        else:
            logger.critical('При запуске виртуальной машины возникли какие-то проблемы')
        logger.debug('Запуск виртуальной машины завершился с  кодом: ' + str(process.returncode))
        logger.debug('Подробности запуска ВМ ниже: \n')
        out = process.communicate()
        logger.debug('stdout запуска: ' + str(out[0].decode('utf-8')))
        if out[1] is not None:
            logger.debug('stderr запуска:' + str(out[1].decode('utf-8')))
        process.kill()
    elif vagrant == 1 and vagrant_Working_directory is not None:
        readytowork = 1
        if vagrant_Working_directory.endswith('/') and os.path.isfile(vagrant_Working_directory + 'Vagrantfile'):
            readytowork = 0
        elif os.path.isfile(vagrant_Working_directory + '/Vagrantfile'):
            readytowork = 0
        if readytowork == 1:
            logger.critical('В указанной директории не найден Vagrantfile')
            logger.critical('Завершаю работу...')
            sys.exit('Vagrantfile не найден в укзанной дериктории')
        else:
            os.chdir(vagrant_Working_directory)
            proc = subprocess.Popen('vagrant up', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            out = proc.communicate()
            if proc.returncode == 0:
                logger.info('ВМ успешно запустилась с помощью Vagrant')
                result = 0
                if out[0] is not None:
                    logger.debug('stdout для запуска ВМ через Vagrant: \n ' + str(out[0].decode('utf-8')))
                if out[1] is not None:
                    logger.debug('stderr для запуска ВМ через Vagrant: \n' + str(out[1].decode('utf-8')))
            elif proc.returncode != 0:
                logger.critical('ВМ не запустилась с помощью Vagrant')
                result = 1
                if out[0] is not None:
                    logger.debug('stdout для запуска ВМ через Vagrant: \n ' + str(out[0].decode('utf-8')))
                if out[1] is not None:
                    logger.debug('stderr для запуска ВМ через Vagrant: \n' + str(out[1].decode('utf-8')))
    return result


def make_archives(logger, VM_NAME: str, dir_name: str) -> tuple:
    '''
    Функция создающая многотомный архив из образа .ova ВМ
    :param logging.handlers.RotatingFileHandler logger: логгер куда писать о событиях в процессе,  рекомендуемый тип: logging.handlers.RotatingFileHandler
    :param str VM_NAME: Имя виртуальной машины для которой создается архив
    :param str dir_name: путь куда будут сохранены части архива
    :return tuple: массив строк с  файлами
    '''
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    os.chdir(dir_name)
    files = glob.glob(dir_name + '/*.tar.bz2*')
    # debug в целях отладки чтобы не пересоздавать архивы каждый раз
    if len(files) > 0:
        return files
    # debugend
    exported = VM_NAME + '.ova'
    logger.debug('Проверяю существует ли файл ' + exported + '.ova перед архивацией')
    if os.path.isfile(exported):
        logger.info('Проверка существования файла ' + exported + ' перед архивацией прошла успешно')
    cmd = 'tar -cvpj '  + exported +  '/ | split -d -b 25m - ' + exported + '.tar.bz2'
    logger.debug('Собираюсь создать архивы с  помощью команды: ' + cmd + '\n')
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out = proc.communicate()
    # logger.info('Создание архивов завершилось с кодом: ' + str(proc.returncode))
    if proc.returncode == 0:
        logger.info('Создание архива завершилось успешно')
    logger.debug('Подробности создания архивов (stdout и stderr ниже')
    logger.debug('stdout: ' + str(out[0].decode('utf-8')))
    if out[1] is not None:
        logger.debug('stderr: ' + str(out[1].decode('utf-8')))
    else:
        logger.debug('stderr был пуст')
    proc.kill()
    files = glob.glob(dir_name + '/*.tar.bz2*')
    logger.info('Количество получившихся архивов: ' + str(len(files)))
    #logger.debug('архивы созданы: \n' + str(files))
    logger.debug('Список созданных файлов: \n' + ' , '.join(files))
    return files


#
# def send_file(file):
#     try:
#         bot.send_document(chat, file)
#     except:
#         send_file(file)


logger = logging.FileHandler


def main(*args, **kwargs):
    print('Этот файл не предназначен для самостоятельного запуска, и является модулем (библиотекой)')
    print('Используйте import virtualbox_api....')


if __name__ == '__main__':
    main()