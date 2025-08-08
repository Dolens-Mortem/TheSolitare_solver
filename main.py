from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time

url = "https://thesolitaire.com/ru/"

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 999999)
driver.get(url)

# Загрузка
time.sleep(5)

# Карты, которыми нет смысла ходить
already_moved = {}
# Словарь с картами
card_dict = {}
# Открытые карты
open_card_dict = {}
# Вышедшие карты из игры
out_card_dict = {
    "0": -1,    #"♥️ Черви"
    "1": -1,    #"♠️ Пики"
    "2": -1,    #"♦️ Бубны"
    "3": -1,    #"♣️ Крести"
}

# Масти
suits = {
    "0": "♥️ Черви",
    "1": "♠️ Пики",
    "2": "♦️ Бубны",
    "3": "♣️ Крести"
}

# Высшие карты и туз
values = {
    "0": "A",
    "10": "J",
    "11": "Q",
    "12": "K"
}

strikes = 0
deck_len = 1
level_of_searching = 0

time.sleep(3)


# Функция для клика в нужном месте
def f_click_card_top(btn):
    size = btn.size
    offset_y = -size['height'] // 2.5  # клик в верхнюю треть 3
    actions = ActionChains(driver)
    actions.move_to_element(btn).move_by_offset(0, offset_y).click().perform()

def f_open_deck():
    global card_dict
    try:
        deck_btn = driver.find_element(By.XPATH, '/html/body/main/div[1]/div[1]/div/div/div[1]')
        deck_btn.click()
        return True
    except Exception as e:
        print(e)
        return False

# Сканирует колоду и открытые карты
def f_opener():
    global open_card_dict, out_card_dict, card_dict, already_moved, deck_len
    temp_card_dict = card_dict.copy()
    deck_len = 0
    while True:
        moved = False
        open_card_dict.clear()
        card_dict.clear()
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='card']")
        placeholders = driver.find_elements(By.CSS_SELECTOR, "div[class='styles_component__zVpk3 isOpen']")
        placeholders_len = len(placeholders)
        #print(f"Найдено карт: {len(cards)}")

        # Вывод в консоли (масть, значение, открыта или закрыта)
        for num, card in enumerate(cards):
            suit = card.get_attribute("data-suit")
            value = card.get_attribute("data-value")
            is_open = card.get_attribute("data-is-moveable")
            in_home = card.get_attribute("data-is-home")
            has_child = card.get_attribute("data-has-child")

            value_num = int(value)
            suit_num = int(suit)
            state = "Закрыта" if is_open == 'false' else "Открыта"
            data = "В игре" if in_home == 'false' else "Не в игре"
            child = "Без пары" if has_child == 'false' else "С парой"

            in_deck = "В колоде" if num > 27 else "Нет"
            deck_status = temp_card_dict[num][3] if temp_card_dict and num in temp_card_dict else in_deck
            card_dict[num] = [value_num, suit_num, state, deck_status, data, child]

            if deck_status == "В колоде":
                deck_len += 1

            if card_dict[num][2] == "Открыта" and card_dict[num][4] == "В игре":
                open_card_dict[num] = card_dict[num]
                print(open_card_dict)


        for k, v in open_card_dict.items():
            if open_card_dict[k][2] == "Открыта" and open_card_dict[k][4] == "В игре":
                s = str(open_card_dict[k][1])
                val_second, suit_second = v[0], v[1]
                pair_second = (val_second, suit_second)

                # Чтобы карты могли 'выйти из игры'
                home_diff = (abs(out_card_dict[s] - open_card_dict[k][0]) == 1) and (open_card_dict[k][5] == "Без пары" and open_card_dict[k][4] == "В игре" and open_card_dict[k][2] == "Открыта")
                if home_diff:
                    out_card_dict[s] = open_card_dict[k][0]
                    card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{int(k) + 15}]')
                    f_click_card_top(card_btn)
                    already_moved[k] = False
                    moved = True

                # Условие, убирающее короля на пустую клетку
                if placeholders_len != 0 and open_card_dict[k][0] == 12:
                    if already_moved.get(pair_second) is False:
                        continue
                    card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{int(k) + 15}]')
                    f_click_card_top(card_btn)
                    already_moved[pair_second] = False
                    moved = True
                    placeholders_len -= 1
                    if card_dict[k][3] == "В колоде" or open_card_dict[k][3] == "В колоде":
                        card_dict[k][3] = open_card_dict[k][3] = "Нет"
                        temp_card_dict = card_dict.copy()
        if not moved:
            break

def intelligent_analysis(card_key, card_value):
    for k, v in open_card_dict.items():
        if card_key == k:
            continue
        if card_value[0] == 1:
            break
        if level_of_searching == 1:
            return True
        if out_card_dict[str(card_value[1])] == -1:
            break
        intel_formula = (card_value[0] - v[0] == 1) and (open_card_dict[card_key][1] + open_card_dict[k][1]) % 2 != 0 and open_card_dict[k][4] == "В игре"
        if intel_formula:
            return True
    return False


# Основная поисковая функция
def f_solver():
    while True:
        moved = False
        global card_dict, open_card_dict, strikes
        f_opener()
        for k_first, v_first in open_card_dict.items():
            val_first, suit_first = v_first[0], v_first[1]
            for k_second, v_second in open_card_dict.items():
                if k_first == k_second:
                    continue

                val_second, suit_second = v_second[0], v_second[1]
                pair_second = (val_second, suit_second)

                formula = (val_first - val_second == 1) and (open_card_dict[k_first][1] + open_card_dict[k_second][1]) % 2 != 0 and open_card_dict[k_second][4] == "В игре" and open_card_dict[k_first][5] == "Без пары" and open_card_dict[k_first][3] != "В колоде"
                if formula:
                    if already_moved.get(pair_second) is False:
                        continue
                    if card_dict[k_second][3] == "В колоде" or open_card_dict[k_second][3] == "В колоде":
                        if not intelligent_analysis(k_second, open_card_dict[k_second]):
                            print('no')
                            continue
                        card_dict[k_second][3] = open_card_dict[k_second][3] = "Нет"
                    try:
                        card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{k_second + 15}]')
                        f_click_card_top(card_btn)
                        already_moved[pair_second] = False
                        card_dict[k_second][4] = "Не в игре"
                        open_card_dict[k_first][5] = "С парой"
                    except Exception as e:
                        print(k_second)
                        print(e)
                    moved = True
                    strikes = 0
        if not moved:
            strikes += 1
            print("Ходов не осталось. Открываю колоду.")
            break

def f_solver_endgame():
    global card_dict, open_card_dict, out_card_dict, already_moved

    for suit, last_out_val in out_card_dict.items():
        target_val = last_out_val + 1
        if target_val > 12:
            continue

        for key, value_open in card_dict.items():
            val, s, state, *_ = value_open
            if val == target_val and str(s) == suit and value_open[4] == "В игре":
                if value_open[2] == "Открыта":
                    if value_open[5] == "С парой":
                        print(f"{values.get(str(val), val)} {suits[suit]} заблокирована картой снизу")
                        for key2, value_open2 in open_card_dict.items():
                            if value_open2[0] == val + 1 and value_open2[1] % 2 != s % 2:
                                try:
                                    card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{key2 + 15}]')
                                    f_click_card_top(card_btn)
                                    already_moved[(value_open2[0], value_open2[1])] = False
                                    time.sleep(1)
                                except Exception as e:
                                    print("Ошибка при клике на карту:", e)
                else:
                    print(f"{values.get(str(val), val)} {suits[suit]} закрыта — нельзя освободить")



def main():
    global strikes, level_of_searching
    f_opener()
    while True:
        '''if strikes >= deck_len * 2:
            f_solver_endgame()
            strikes = 0
        else:'''
        for i in range(deck_len):
            f_solver()
            bool_deck = f_open_deck()
            if not bool_deck:
                print('Остановка программы')
                time.sleep(999999)
                break
        if strikes >= deck_len:
            level_of_searching = 1
        else:
            level_of_searching = 0
main()



















# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[36] - card 21
# /html/body/main/div[1]/div[1]/div/div/div[15] - card 0
# /html/body/main/div[1]/div[1]/div/div/div[42] - card 27

# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[13]/div - пустое поле 2
# /html/body/main/div[1]/div[1]/div/div/div[14]/div - пустое поле 1