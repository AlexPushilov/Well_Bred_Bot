import re
import time
import sqlite3

import telebot
from forismatic import *

from configure import config

bot = telebot.TeleBot(config["token"])

"""
week_days = {
    0: '1_Monday',
    1: '2_Tuesday',
    2: '3_Wednesday',
    3: '4_Thursday',
    4: '5_Friday',
    5: '6_Saturday',
    6: 'now_sunday'
}

lessons = {
    9: 'lesson_1',
    10: 'lesson_2',
    11: 'lesson_3',
    12: 'lesson_4',
    13: 'lesson_5',
    14: 'lesson_6',
    15: 'lesson_7',
    16: 'lesson_8'
}

timetable = {
    9: '9.0 9.45',
    10: '10.0 10.45',
    11: '11.05 11.50',
    12: '12.05 12.50',
    13: '13.10 13.55',
    14: '14.10 14.50',
    15: '15.05 15.10',
    16: '16.00 16.45'
}
"""

class Messages:
	start_message =\
"""
Привет👋, это бот Олег!

❗️Чтобы я функционировал тебе нужно пройти регистрацию.
‼️Пока Вы не пройдете регистрацию, все будет заблокировано!

Нажми на кнопку 🆕!
"""

	help_info=\
"""
Этот бот создан для того, чтобы помогать ученикам отслеживать свою успеваемость.

С помощью него можно узнать свои отметки по предметам, четвертям и полугодиям (а также и годовые), расписание уроков и домашние задания.

Чтобы узнать список команд бота и что они делают напишите в чат бота '🗒 Мои команды' или нажмите на соответствующую кнопку на клавиатуре телеграмма.

Если Вы заметили ошибки в работе бота, напишите:

• @principal_hero
• @SMeRtniK_OGniA
• @Krvan22
"""


	my_commands =\
"""
Список моих команд:
• 📚 Д/з - домашняя работа по определенному предмету.

• 📊 Отметки - оценки по определенному предмету.

• 🎓 Итоговые отметки - оценки за четверти, полугодия и год.

• 📝 Расписание - расписание уроков.

• ❓ Помощь - список команд бота.

• 🧐 Слово философа - Цитаты великих деятелей.
"""


	about_classformat =\
"""
Введите класс в формате xy, где x - номер класса, y - буква класса
• Раскладка клавиатуры - русская.
• Регистр не важен.
"""

	about_loginformat=\
"""
Введите данные в формате 'Login Password', где
• Login - Ваш логин (Эл. почта)
• Password - Ваш пароль
"""

	warning =\
"""
"Пока Вы не зарегистрируетесь, доступ к функциям закрыт."
"""

	schedule = \
"""
1️⃣ - Следующий урок

2️⃣ - Расписание на сегодня

3️⃣ - Расписание на неделю
"""


class Keyboards:

	# Main
	def make_reply_keyboard():
		reply_keyboard = telebot.types.ReplyKeyboardMarkup()
		
		help_com = telebot.types.KeyboardButton(text="❓ Помощь")
		my_commands = telebot.types.KeyboardButton(text="🗒 Мои команды")
		feature = telebot.types.KeyboardButton(text="🧐 Слово философа")
		homework = telebot.types.KeyboardButton(text="📕 Д/з")
		marks = telebot.types.KeyboardButton(text="📚 Отметки")
		total = telebot.types.KeyboardButton(text="👨‍🎓 Итоговые отметки")
		schedule = telebot.types.KeyboardButton(text="📝 Расписание")


		reply_keyboard.add(my_commands)
		reply_keyboard.row(help_com, schedule)
		reply_keyboard.row(marks, total)
		reply_keyboard.row(homework, feature)

		return reply_keyboard
	

	def make_start_keyboard():
		reply_keyboard = telebot.types.ReplyKeyboardMarkup()
		sign_up = telebot.types.KeyboardButton(text="🆕 Регистрация")

		reply_keyboard.add(sign_up)
		return reply_keyboard
	

	def make_schedule_keyboard():
		inline_keyboard = telebot.types.InlineKeyboardMarkup()
 
		now = telebot.types.InlineKeyboardButton(text="1️⃣", callback_data="next")
		day = telebot.types.InlineKeyboardButton(text="2️⃣", callback_data="day")
		week = telebot.types.InlineKeyboardButton(text="3️⃣", callback_data="week")

		inline_keyboard.row(now, day, week)

		return inline_keyboard

	def make_subjects_keyboard():
		reply_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

		phisics = telebot.types.KeyboardButton(text="💡 Физика")
		algebra = telebot.types.KeyboardButton(text="🧮 Алгебра")
		geometry = telebot.types.KeyboardButton(text="📐 Геометрия")
		computer = telebot.types.KeyboardButton(text="💻 Информ.")
		russian = telebot.types.KeyboardButton(text="🇷🇺 Русск. яз")
		literature = telebot.types.KeyboardButton(text="📖 Лит-ра")
		english = telebot.types.KeyboardButton(text="🇬🇧 Англ. яз")
		biology = telebot.types.KeyboardButton(text="🧬 Биология")
		chemistry = telebot.types.KeyboardButton(text="☣️ Химия")
		history = telebot.types.KeyboardButton(text="📽 История")
		social = telebot.types.KeyboardButton(text="👨‍👩‍👦 Общество")
		pe = telebot.types.KeyboardButton(text="🏐 Физ-ра")
		project = telebot.types.KeyboardButton(text="🧱 Проект")

		reply_keyboard.row(phisics, algebra, geometry)
		reply_keyboard.row(russian, literature, english)
		reply_keyboard.row(computer, biology, chemistry)
		reply_keyboard.row(history, social, pe)
		reply_keyboard.add(project)

		return reply_keyboard


	schedule_keyboard = make_schedule_keyboard()
	subject_keyboard = make_subjects_keyboard()
	start_keyboard = make_start_keyboard()
	reply_keyboard = make_reply_keyboard()


class Features_funcs:
	username = None
	userclass = None
	userlogin = None
	userpass = None

	sign_up = False
	sign_up_passed = False
	class_passed = False
	subject_selected = False

	first_time = True

	mistake_1 = False
	mistake_2 = False


	def make_quote():
		max_len = 150
		primary_quote = forismatic.ForismaticPy()

		quote, author = primary_quote.get_Quote('ru')
		while len(quote) > max_len:
			quote, author = primary_quote.get_Quote('ru')

		c = "©" if author else ""
		full_quote = f"{quote} {c}{author}"

		return full_quote


	def check_class_correct(message):
		lengh = len(message.text)
		text = message.text

		if 2 <= lengh <= 3:
			return re.fullmatch(r"[\d^0][А-Га-г]", text) or re.fullmatch(r"1[01][А-Га-г]", text)
		return False
	

	def login_valid(login):
		return re.fullmatch(r".+@.+\..+", login)

"""
	def now_schedule(userclass):
		clas = userclass
		con = sqlite3.connect('timetable.db')
		cur = con.cursor()

		full_time = time.localtime(time.time())
		hours = full_time.tm_hour
		date = week_days[full_time.tm_wday]
		minutes = full_time.tm_min

		if minutes < 10:
			minutes = '0' + str(minutes)
		print(float(str(hours) + '.' + str(minutes)))
		if date == 'now_sunday':
			print(''.join(cur.execute(f'''SELECT now_sunday FROM all_class''').fetchone()))
		elif hours in range(0, 9):
			print(''.join(cur.execute(f'''SELECT wait_day FROM all_class''').fetchone()))
		elif hours in range(17, 0):
			print(''.join(cur.execute(f'''SELECT lesson_8 FROM all_class''').fetchone()))
		elif float(str(hours) + '.' + str(minutes)) >= float(timetable[hours].split()[0]) and float(str(hours) + '.' + str(minutes)) <= float(timetable[hours].split()[1]):
			now_lesson = cur.execute(f'''SELECT {lessons[hours]} FROM all_class WHERE number_of_class = "{clas}" AND Day = "{date}"''').fetchall()
			next_lesson = cur.execute(f'''SELECT {lessons[hours + 1]} FROM all_class WHERE number_of_class = "{clas}" AND Day = "{date}"''').fetchall()
			
			message = f
Ваш класс: {clas}
Сейчас урок: {now_lesson[0][0].split()[0]}
Следующий урок:{next_lesson[0][0].split()[0]}
	
		else:
			message = ''.join(cur.execute(f'''SELECT wait_time FROM all_class''').fetchone())

		return message
"""

class Handlers:
	filters = [
	"audio", "document", "photo", "sticker", "video", "video_note", "voice", 
	"location", "contact", "new_chat_members", "left_chat_member", "new_chat_title",
	"new_chat_photo", "delete_chat_photo", "group_chat_created", "supergroup_chat_created", 
	"channel_chat_created", "migrate_to_chat_id", "migrate_from_chat_id", 
	"pinned_message", "web_app_data", "sticker"
	]

	@bot.message_handler(commands=["start"])
	def start(message):
		Features_funcs.first_time = True
		Features_funcs.sign_up_passed = False
		bot.send_message(message.chat.id, Messages.start_message, reply_markup=Keyboards.start_keyboard)


	@bot.callback_query_handler(func=lambda call: True)
	def process_callback_schedule(call):

		if call == "next":
			bot.send_message(call.message.chat.id, Features_funcs.now_schedule(Features_funcs.userclass))
		elif call == "day":
			bot.send_message(call.message.chat.id, "Расписание на сегодня:")
		elif call == "week":
			bot.send_message(call.message.chat.id, "Расписание на неделю:")
		
		bot.answer_callback_query(call.id, text="Дорогой пользователь, бот Олег находится на стадии разработки!", show_alert=True)


	@bot.message_handler(content_types=["text"])
	def class_number(message):
		if Features_funcs.sign_up_passed:
			if message.text == "📝 Расписание":
				bot.send_message(message.chat.id, f"Доступные варианты:\n{Messages.schedule}", reply_markup=Keyboards.schedule_keyboard)

			elif message.text == "📕 Д/з":
				bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)

			elif message.text == "📚 Отметки":
				bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)

			elif message.text == "👨‍🎓 Итоговые отметки":
				bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)


			elif message.text == "🧐 Слово философа":
				bot.send_message(message.chat.id, f"👴 Мудрость:\n\n{Features_funcs.make_quote()}")

			elif message.text == "🗒 Мои команды":
				bot.send_message(message.chat.id, Messages.my_commands)

			elif message.text == "❓ Помощь":
				bot.send_message(message.chat.id, Messages.help_info)


			elif message.text == "💡 Физика":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🧮 Алгебра":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "📐 Геометрия":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "💻 Информ.":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🇷🇺 Русск. яз":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "📖 Лит-ра":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🇬🇧 Англ. яз":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🧬 Биология":
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "☣️ Химия":
					bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "📽 История":
					bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "👨‍👩‍👦 Общество":
					bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🏐 Физ-ра":
					bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

			elif message.text == "🧱 Проект":
					bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.reply_keyboard)

		else:
			if message.chat.type == "private":
				if message.text == "🆕 Регистрация":
					if Features_funcs.first_time: # will: if user not in database
						Features_funcs.sign_up = True
						Features_funcs.sign_up_passed = False
						Features_funcs.class_passed = False
						Features_funcs.first_time = False

						bot.send_message(message.chat.id, Messages.about_classformat, reply_markup=telebot.types.ReplyKeyboardRemove())
					
					else:
						bot.delete_message(message.chat.id, message.message_id)

				elif not Features_funcs.class_passed and Features_funcs.sign_up:
					if Features_funcs.check_class_correct(message):
						Features_funcs.userсlass = message.text

						Features_funcs.class_passed = True
						bot.send_message(message.chat.id, Messages.about_loginformat)
		
					else:
						bot.delete_message(message.chat.id, message.message_id)

				elif Features_funcs.class_passed and not Features_funcs.sign_up_passed:
					if len(message.text.split()) == 2:
						login, password = message.text.split()

						if Features_funcs.login_valid(login):
							Features_funcs.userlogin = login
							Features_funcs.userpass = password

							Features_funcs.sign_up_passed = True
							bot.send_message(message.chat.id, "Регистрация завершена!", reply_markup=Keyboards.reply_keyboard)
						
						else:
							if not Features_funcs.mistake_2:
								bot.send_message(message.chat.id, "Логин введен неверно!")
								Features_funcs.mistake_2 = True
							else:
								bot.delete_message(message.chat.id, message.message_id)
					
					else:
						bot.delete_message(message.chat.id, message.message_id)
				
				else:
					if not Features_funcs.mistake_2:
						bot.send_message(message.chat.id, "Неправильный формат!")
						Features_funcs.mistake_2 = True
					else:
						bot.delete_message(message.chat.id, message.message_id)
	
	@bot.message_handler(content_types=filters)
	def del_messages(message):
		bot.delete_message(message.chat.id, message.message_id)

if __name__ == "__main__":
	bot.infinity_polling()
