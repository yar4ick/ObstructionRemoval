import config
from imgprocessing import image_converting
import os
import subprocess
import shutil
import PIL
from PIL import Image
import telebot
from telebot import types

bot = telebot.TeleBot(config.token)
users = []
usersPhotos = {}
usersResults = {}

### Welcome Message
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    welcome_gif = open('example.gif', 'rb')
    if user_id not in users:
        users.append(user_id)
        bot.send_message(user_id, "Привіт! Я бот, що допоможе тобі прибрати зайве з твоїх фото.\
            Зараз я вмію прибирати лише сітку.\
 Пришли мені 5 фото зробленних як на гіфці нижче (у послідовному русі вправо або вліво), а решта за мною!")
        bot.send_document(user_id, welcome_gif)
    else:
        bot.send_message(user_id, "Хочешь ще допомоги з фото? Я готовий!\
 Пришли мені 5 фото зробленних як на гіфці нижче (у послідовному русі вправо або вліво), а решта за мною!")
        bot.send_document(user_id, welcome_gif)

### Handling text messages
@bot.message_handler(content_types=["text"])
def text_warning(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Чекаю твої фото \U0001F60A!\
 З текстом не працюю \U0001F609")

### Handling documents
@bot.message_handler(content_types=["document"])
def document_warning(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Я не працюю з іншими файлами, окрім зображень \U0001F61E.\
 Не треба присилати зображення як файл,\
 використовуй стандартний спосіб надсилання зображень у Telegram! \U0000261D")

### Bot downloads 5 photos, run a subprocess and sends a final image back to the user
@bot.message_handler(content_types=["photo"])
def user_sending_photo(message):
    user_id = message.chat.id
    msg_id = message.message_id
    ### Creating a directory for each user
    prnt_dir = "source_images"
    user_dir = str(user_id)
    user_path = os.path.join(prnt_dir, user_dir)
    ### Making a directory for each user
    try:
        os.makedirs(user_path)
    ### Error handler if a directory already exists
    except OSError as error:
        print (error)
    ### Creating a variable for each user based on user ID using dictionary usersPhotos
    if usersPhotos.get(user_id, 1) <= 5:   
        ### Saving photo as a source file to a user folder
        photo_id = bot.get_file(message.photo[-1].file_id)
        dwnl_photo = bot.download_file(photo_id.file_path)
        im_src = user_path + message.photo[-1].file_id
        with open(im_src, 'wb') as new_file:
            new_file.write(dwnl_photo)
        ### Creating a path to a photo
        im_name = user_path + '/' + str(msg_id) + '.png'
        ### Using image_converting function from imgprocessing.py to resize image
        image_converting(Image.open(im_src)).save(im_name)
        ### Removing initial source image file
        os.remove(im_src)
        ### Counter for 5 images received
        if usersPhotos.get(user_id, 1) < 5:
            usersPhotos[user_id] = usersPhotos.get(user_id, 1) + 1
        else:
            ### The main process starts when bot receives 5 photos
            usersPhotos[user_id] += 1
            bot.send_message(user_id, "Отримав 5 фото. Починаю працювати \U0001F913. Я повідомлю тобі, як буде готово.")
            ### Loop to rename photos to the format needed for the obstruction removal ANN
            for count, filename in enumerate(os.listdir(user_path)):
                os.rename(os.path.join(user_path, filename), user_path + "/00001_I" + str(count) + ".png")
            ### Starting ANN as a subprocess
            usersResults[user_id] = subprocess.run("python3.7 test_fence.py --output_dir " + user_path + "/" + " --test_dataset_name " + user_path + "/00001", shell=True)
            ### Check the subprocess result: if it is 0 than subprocess was executed succesfuly
            if usersResults[user_id].returncode == 0:
                bot.send_message(user_id, "Твоє фото готове!")
                bot.send_photo(user_id, open(user_path+"/00001_final.png", 'rb'))
                bot.send_message(user_id, "Якщо ти не задоволений результатом, то спробуй ще раз з новими фото. Радимо використовувати HDR режим.\U0001F64B")
                ### Deleting all items in the users folder since they are no more needed
                shutil.rmtree(user_path)
                ### Deleting user key from the dictionary in order to allow to run a subprocess again
                del usersPhotos[user_id]
            else:
                bot.send_message(user_id, "Щось пішло не так \U0001F635. Зроби нові фото та спробуй ще.")
                ### Deleting all items in the users folder since they are no more needed
                shutil.rmtree(user_path)
                ### Deleting user key from the dictionary in order to allow to run a subprocess again  
                del usersPhotos[user_id]
    else:
        bot.send_message(user_id, "Я вже маю 5  фото та працюю над ними. Більше не потрібно. Почекай \U0001F609")

if __name__ == '__main__':
    bot.infinity_polling()