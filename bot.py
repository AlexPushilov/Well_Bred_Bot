import re

import telebot
from forismatic import *

# токен бота
from configure import config

bot = telebot.TeleBot(config["token"])

# Сорри, что прям все коментирую, а вдруг тебе непонтяно будет?~
# All default messages
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


# Make our KeyBoards
class Keyboards:

	# Main KeyBoard. There we take a conversation with our bot
	def make_reply_keyboard():
		reply_keyboard_login = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
		reply_keyboard = telebot.types.ReplyKeyboardMarkup()
		
		sign_up = telebot.types.KeyboardButton(text="🆕 Регистрация")
		help_com = telebot.types.KeyboardButton(text="❓ Помощь")
		my_commands = telebot.types.KeyboardButton(text="🗒 Мои команды")
		feature = telebot.types.KeyboardButton(text="🧐 Слово философа")
		homework = telebot.types.KeyboardButton(text="📕 Д/з")
		marks = telebot.types.KeyboardButton(text="📚 Отметки")
		total = telebot.types.KeyboardButton(text="👨‍🎓 Итоговые отметки")
		schedule = telebot.types.KeyboardButton(text="📝 Расписание")

		reply_keyboard_login.add(sign_up)

		reply_keyboard.add(my_commands)
		reply_keyboard.row(help_com, schedule)
		reply_keyboard.row(marks, total)
		reply_keyboard.row(homework, feature)

		# returning 2 bords: before login and after
		return reply_keyboard_login, reply_keyboard

	def make_schedule_keyboard():

		# Future board of schedule
		inline_keyboard = telebot.types.InlineKeyboardMarkup()
 
		now = telebot.types.InlineKeyboardButton(text="1️⃣", callback_data="next")
		day = telebot.types.InlineKeyboardButton(text="2️⃣", callback_data="day")
		week = telebot.types.InlineKeyboardButton(text="3️⃣", callback_data="week")

		inline_keyboard.row(now, day, week)

		return inline_keyboard

	def make_subjects_keyboard():

		# lessons
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


	# create board. Now we have an access to them through class "Keyboards"
	schedule_keyboard = make_schedule_keyboard()
	subject_keyboard = make_subjects_keyboard()
	signup_keyboard, reply_keyboard = make_reply_keyboard()


class Features_funcs:

	# variables we need to login
	sign_up = False
	sign_up_passed = False
	class_passed = False
	subject_selected = False

	first_time = True

	"""Just sugar: we need this variables cause 
	if we don't, user always (if login or pass isn't right)
	will see this message: "Неправильный..."""
	mistake_1 = False
	mistake_2 = False

	# Randow wise
	def make_quote():
		max_len = 150
		primary_quote = forismatic.ForismaticPy()

		quote, author = primary_quote.get_Quote('ru')
		while len(quote) > max_len:
			quote, author = primary_quote.get_Quote('ru')

		c = "©" if author else ""
		full_quote = f"{quote} {c}{author}"

		return full_quote

	# Check
	def check_class_correct(message):
		lengh = len(message.text)
		text = message.text

		if 2 <= lengh <= 3:
			return re.fullmatch(r"[\d^0][А-Га-г]", text) or re.fullmatch(r"1[01][А-Га-г]", text)
		return False
	
	# mail + pass validation
	def login_valid(login):
		return re.fullmatch(r".+@.+\..+", login)


# All Handlers here/
class Handlers:

	# bot deleting messages of these types
	filters = [
	"audio", "document",
	"video", "video_note", "voice", "location",
	"contact", "new_chat_members", "left_chat_member",
	"new_chat_title", "new_chat_photo", "delete_chat_photo",
	"group_chat_created", "supergroup_chat_created", "channel_chat_created",
	"migrate_to_chat_id", "migrate_from_chat_id",
	"pinned_message", "web_app_data",
	]

	# start command
	@bot.message_handler(commands=["start"])
	def start(message):
		Features_funcs.first_time = True
		Features_funcs.sign_up_passed = False
		bot.send_message(message.chat.id, Messages.start_message, reply_markup=Keyboards.signup_keyboard)

	# Bot's buttons
	@bot.callback_query_handler(func=lambda call: True)
	def process_callback_schedule(call):

		# Пока что сдедано в виде alert (всплывающее окно)
		if call == "next":
			bot.send_message(call.message.chat.id, "Текущий урок:\nСледующий урок:")
		elif call == "day":
			bot.send_message(call.message.chat.id, "Расписание на сегодня:")
		elif call == "week":
			bot.send_message(call.message.chat.id, "Расписание на неделю:")
		
		bot.answer_callback_query(call.id, text="Дорогой пользователь, бот Олег находится на стадии разработки!", show_alert=True)

	# text handlers
	@bot.message_handler(content_types=["text"])
	def class_number(message):

		# if chat id is private, we can use stickers
		if message.chat.id == "private":
			Handlers.filters.append("sticker")

		# Below so many handlers
		# There is reaction if we passed reg
		if message.text == "📝 Расписание":

			# if passed reg
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, f"Доступные варианты:\n{Messages.schedule}", reply_markup=Keyboards.schedule_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "📕 Д/з":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "📚 Отметки":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "👨‍🎓 Итоговые отметки":
			if Features_funcs.sign_up_passed:
					bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=Keyboards.subject_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🧐 Слово философа":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, f"👴 Мудрость:\n\n{Features_funcs.make_quote()}")
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🗒 Мои команды":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, Messages.my_commands)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "❓ Помощь":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, Messages.help_info)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "💡 Физика":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🧮 Алгебра":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "📐 Геометрия":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "💻 Информ.":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🇷🇺 Русск. яз":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "📖 Лит-ра":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🇬🇧 Англ. яз":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🧬 Биология":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "☣️ Химия":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "📽 История":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "👨‍👩‍👦 Общество":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🏐 Физ-ра":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		elif message.text == "🧱 Проект":
			if Features_funcs.sign_up_passed:
				bot.send_message(message.chat.id, "Скоро!", reply_markup=Keyboards.signup_keyboard)
			else:
				bot.delete_message(message.chat.id, message.message_id)


		# reg process
		# remove this?
		elif message.chat.type == "private":
			if message.text == "🆕 Регистрация":

				# flags
				if Features_funcs.first_time:
					
					# Прошли первый этап
					Features_funcs.sign_up = True

					# Прошли всю регистрацию
					Features_funcs.sign_up_passed = False

					# Прошли второй этап (класс)
					Features_funcs.class_passed = False

					# Проходим регитсрацию впервые
					Features_funcs.first_time = False

					# send class info
					bot.send_message(message.chat.id, Messages.about_classformat, reply_markup=telebot.types.ReplyKeyboardRemove())
				else:
					# delete user message
					bot.delete_message(message.chat.id, message.message_id)

			# Если прошли не прошли второй этап (класс) и прошли первый этап (нажалли кнопку)
			elif not Features_funcs.class_passed and Features_funcs.sign_up:

				# Если ввели все правильно
				if Features_funcs.check_class_correct(message):
					Features_funcs.class_passed = True

					bot.send_message(message.chat.id, Messages.about_loginformat)
				else:
					bot.delete_message(message.chat.id, message.message_id)

			# Если прошли второй этап и не прошли всю регистрацию
			elif Features_funcs.class_passed and not Features_funcs.sign_up_passed:
				# Если сообщение соотвествует формату "login Pass"
				if len(message.text.split()) == 2:

					# запишем в бд?
					login, password = message.text.split()

					# если формат правильный
					if Features_funcs.login_valid(login):
						Features_funcs.sign_up_passed = True
						bot.send_message(message.chat.id, "Регистрация завершена!", reply_markup=Keyboards.signup_keyboard)
					else:
						# если пользователь впервые ввел что-то неправильно
						# то бот отвечает. Если не впервые, то просто удаляет сообщение и ничего не пишет
						if not Features_funcs.mistake_2:
							bot.send_message(message.chat.id, "Логин введен неверно!")
							Features_funcs.mistake_2 = True
						else:
							bot.delete_message(message.chat.id, message.message_id)
				else:
					bot.delete_message(message.chat.id, message.message_id)
			else:
				# то же самое, что и mistake_1, только на втором этапе регистрации
				if not Features_funcs.mistake_2:
					bot.send_message(message.chat.id, "Неправильный формат!")
					Features_funcs.mistake_2 = True
				else:
					bot.delete_message(message.chat.id, message.message_id)
	
	# удаляем сообщения, попавшие в фильтры
	@bot.message_handler(content_types=filters)
	def delete_message(message):
		bot.delete_message(message.chat.id, message.message_id)

# запускаем бота
if __name__ == "__main__":
	bot.infinity_polling()