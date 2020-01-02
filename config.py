#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import logging
from sys import exit as sys_exit
from datetime import datetime


chat = '-1234567890' # чат куда отправлять
token = '123456789:FuckThisWorld' # токен бота телеграма с помощью которого отправлять
dir_name = '/path/temp/dir/temporary' # временная директория для выполнения (! должна быть пустой
VM_NAME = 'VM_FOR_BACKUP' # название виртуальной машины которую копируем
msg = 'Резервная копия тестовой виртуальный машины по состоянию на ' + str((datetime.now().date()).strftime('%d/%m/%Y')) # Текст информационного сообщения
max_send_tryes = 10 # максимальное количество на попыток отправки
# fixme на текущий момент в логе вместо ожидамого BACKUP_VM_NAME появляется root
log_info = 'BACKUP_' + VM_NAME # Если хотите формат не по умолчанию укажите тут свой.
log_level = logging.DEBUG # Уровень логгирования
vagrant = 0 # 1 если поднимать с vagrant, 0 -  если без  вагранта. Следующий параметр обязателен если с вагрантом
vagrant_working_Directory = '/path/to/vagrant/dir/VagrnatVM/' # Директория где лежит Vagrantfile
unpack_instruction = 'Для распаоквки нужно:' \
                     '1.поместить все файлы в  одну директорию' \
                     '2. объеденить их  с помощью команды cat *.ova.tar.bz2*  > backup.tar.bz2' \
                     '3. распаковать их с помощью tar -xvf backup.tar.bz2'



def main(*args, **kwargs):
    print('Этот модуль не предназначен для самостоятельного запуска')
    print('Используйте import config')

if __name__ == '__main__':
    main()
    sys_exit('Неправильное использование модуля')
