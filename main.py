import telebot
import time
from itertools import product

token = "5787809042:AAHL2a4FYKaBavQJNBjQEp54Iro-jjYWtgo"
bot = telebot.TeleBot(token=token)


class Team:
    def __init__(self, pin_code, name):
        self.name = name
        self.pin_code = pin_code
        self.time_start = 0
        self.time_end = 0
        self.current_task = 0
        self.current_chain = 0
        self.chain_count = 0
        self.penalty_points = 0
        self.participants = []


teams_list = []

task_list = [
    ['задание11', 'задание12'],
    ['задание21', 'задание22'],
    ['задание31', 'задание32']
]
answer_list = [
    ['ответ11', 'ответ12'],
    ['ответ21', 'ответ22'],
    ['ответ31', 'ответ32']
]

teams_result_times = []
pin_codes_list = [110101, 123456]


def bot_help(user_id):
    bot.send_message(user_id, 'Если вы хотите узнать текущее задание - введите \'Задание\';\n'
                              'Если вы хотите ввести ответ в формате \'Ответ:<ваш ответ>\';\n')


def get_task(user_id, team):
    bot.send_message(user_id, f'Текущее задание вашей комады: {task_list[team.current_chain][team.current_task]}')


def choosing_a_new_chain(msg, team, user_id):
    team.current_chain = int(msg.text)
    team.current_task = 0
    get_task(user_id, team)


def check_answer(answer, team, user_id):
    try:
        answer = answer.split('Ответ:')[1]
        if answer == answer_list[team.current_chain][team.current_task]:
            bot.send_message(user_id, "Верно")
            if team.current_task < len(answer_list[team.current_chain]):
                team.current_task += 1
            else:
                if team.chain_count < len(answer_list):
                    team.chain_count += 1
                    msg = bot.reply_to(answer, "Выберите новую цепочку для прохождения")
                    bot.register_next_step_handler(msg, choosing_a_new_chain, team, user_id)
                else:
                    # counting the results taking into account penalty points
                    team.time_end = time.time()
                    teams_result_times.append(int(team.time_end - team.time_start) + team.penalty_points * 300)
                    teams_result_times.sort()
                    ranking_place = teams_result_times.index(team.time_end) + 1
                    bot.send_message(user_id, f'Молодец! Ты решил все задания за {team.end_time} секунды')
                    bot.send_message(user_id, f'Твое место в рейтинге: {ranking_place}')
        else:
            team.penalty_points += 1
            bot.send_message(user_id, "Не, попробуй еще разок")

    except Exception as e:
        ranking_place = teams_result_times.index(team.time_end) + 1
        bot.send_message(user_id, f'Хорош, игра окончена:) Твое место в рейтинге: {ranking_place}')


def new_team(name_msg, pin_code, user_id):
    new_user_team = Team(pin_code=pin_code, name=name_msg.text)
    new_user_team.participants.append(user_id)
    teams_list.append(new_user_team)


def get_pin(pin_code_msg, user_id):
    pin_code = int(pin_code_msg.text)
    if pin_code in pin_codes_list:
        team = [el for el in teams_list if el.pin_code == pin_code]
        if team:
            team[0].participants.append(user_id)
        else:
            msg = bot.reply_to(pin_code_msg, "Задайте имя вашей команде")
            bot.register_next_step_handler(msg, new_team, pin_code, user_id)
    else:
        bot.send_message(user_id, "Этого пин-кода нет в списке...Может, ты неправильно ввел?")


@bot.message_handler(content_types=['text'])
def remember(message):
    user_id = message.chat.id
    # looking for a user among existing players
    new_user = True
    users_team = None
    for team in teams_list:
        for participant in team.participants:
            if user_id == participant:
                new_user = False
                users_team = team
    # if the user is new, he must enter a pin to join some team
    if new_user:
        msg = bot.reply_to(message, "Введите пин-код:")
        bot.register_next_step_handler(msg, get_pin, user_id)
        # get_pin(user_id, message.text)
    else:
        if 'Ответ:' in message.text:
            check_answer(message.text, users_team, user_id)
        elif 'Задание' in message.text:
            get_task(user_id, users_team)
        else:
            bot_help(user_id)


bot.polling(none_stop=True)

# TODO
# 1.выбор цепочки
# 2.только один штрафной бал за одно задание
# 3.подсказки для заданий
# 4.мб bot_help для разных этапов будет выглядеть по-разному, потому формат ответа может меняться
