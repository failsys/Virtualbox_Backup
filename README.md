# Virtualbox_Backup

Let me know if someone will need english version. email: fail.sys@yandex.ru
No any depencies. No any pip install requered. just curl and tor as proxy

Система бэкапирования виртуальной машины ВиртуалБокс (VirtualBox) в telegram. 
Посредством создания образа и  многотомного архива.



НЕ СОВМЕСТИМ С Windows системами.
На текущий момент скрипт не использует никаких зависимостей не встроенных в питон.

Работоспосбоность проверялась с помощью Python3.6

Для корректной работы должен быть установлен curl и tor (как прокси). tor должен висеть на 9050 порту без авторизации

Возможно скоро добавлю работу без прокси (если понадобится)

Установка tor: подойдет обычный tor из репозитория

sudo apt-get install tor curl -y

Проверим что он существует на 9050 порту

sudo netstat -tunlp| grep 9050


Как пользоваться: 


Перед использованием нужно настроить указав правильные параметры в файле config.py
chat = ‘-123456789’ ID чата куда слать архивы. Для того чтобы узнать его можно воспользоваться специальным ботом @my_id_bot. !Обратите внимание на знак “-” перед номером. Он является ОБЯЗАТЕЛЬНЫМ для работы (присутствует только у ID группы) Если добавить указнного бота в группу - он сообщит адрес группы подробнее можно почитать где-то тут

token = ‘123456789:FuckThisWorld’ токен бота телеграмма который будет отправлять сообщения и архивы Можно создать с помощью специального бота @BotFather подробнее тут или тутОбратите внимание что ID указывается полностью, вместе с цифрами, двоеточием и буквами после двоеточия

dir_name = ‘/home/path/tempdir/temporary’ # временная директория для выполнения (! должна быть пустой и пользователь, от имени которого выполняется скрипт должен иметь право записи и чтения!) сюда будут складываться экспортиуемый образ и создаваемые архивы перед отправкой. Директория должна быть пустой. У пользователя от имени которого выполняется скрипт должны быть права на чтение и запись к директории. После выполнения программа сама удалит все созданные временные файлы.

VM_NAME = ‘vm_for_backup’ # название виртуальной машины которую будем бэкапировать. Можно посмотреть в виртуалбоксе или с помощью команды vboxmanage list vms

msg = (‘Резервная копия виртуальный машины с vm_my_backup по состоянию на ‘ + str(dt)) # Текст информационного сообщения, которое будет отправляться перед архивами

log_info = Информация которая будет записываться в кажой строке. По умолчанию “Backup script for Имя бэкапируемой виртуальной машины” Возможные варианты: log_level = уровень логгирования. По умолчанию стоит logging.DEBUG так как до сих пор на стадии отладки. Если хотите - можно поменять. Возможные варианты ниже:

**logging.DEBUG** - будут выводится сообщения об успешных и неудачных попытках отправки.  А так же много служебной, отладочной информации
**logging.INFO** - будут выводится инфо сообщения об успешных и неудачных попытках отправки.
**logging.CRITICAL** - будут выводится сообщения только о неудачных попытках
max_send_tryes = 10 # максимальное количество попыток отправки, действует и на сообщения,и на архивы.

vagrant = 0 # укажите тут 1, если виртуальная машина была создана с помощью vagrant и запускается с помощью него же. для корректного запуска с помощью vagrant следующий параметр обязателен

vagrant_working_Directory = ‘/my/virtual_machines/vagrant/vm_for_backup/’ # Директория где лежит Vagrantfile. Укажите полный путь до директории (не до файла! а именно до директории) где находится Vagrantfile

unpack_instruction =

                  'Для распаоквки нужно:' \
                 '1.поместить все файлы в  одну директорию' \
                 '2. объеденить их  с помощью команды cat *.ova.tar.bz2*  > backup.tar.bz2' \
                 '3. распаковать их с помощью tar -xvf backup.tar.bz2'
Последний параметр - инструкции для распаковки созданного архива. Будут отправлены после архива.
