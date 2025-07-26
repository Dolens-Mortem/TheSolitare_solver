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

# Словарь с картами
card_dict = {}
# Открытые карты
open_card_dict = {}
# Вышедшие карты из игры
out_card_dict = {
    "0": -1,    #"♥️ Червы"
    "1": -1,    #"♠️ Пики"
    "2": -1,    #"♦️ Бубны"
    "3": -1,    #"♣️ Крести"
}

# Масти
suits = {
    "0": "♥️ Червы",
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

time.sleep(3)

print("все")

# Функция для клика в нужном месте
def f_click_card_top(btn):
    size = btn.size
    offset_y = -size['height'] // 3  # клик в верхнюю треть
    actions = ActionChains(driver)
    actions.move_to_element(btn).move_by_offset(0, offset_y).click().perform()

def f_open_deck():
    try:
        deck_btn = driver.find_element(By.XPATH, '/html/body/main/div[1]/div[1]/div/div/div[1]')
        deck_btn.click()
        return True
    except Exception as e:
        print(e)
        return False

# Сканирует колоду и открытые карты
def f_opener(temp_dict = None):
    global open_card_dict, out_card_dict
    open_card_dict.clear()
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='card']")
    placeholders = driver.find_elements(By.CSS_SELECTOR, "div[class='styles_component__zVpk3 isOpen']")
    #print(f"Найдено карт: {len(cards)}")

    # Вывод в консоли (масть, значение, открыта или закрыта)
    for num, card in enumerate(cards):
        suit = card.get_attribute("data-suit")
        value = card.get_attribute("data-value")
        is_open = card.get_attribute("data-is-moveable")
        in_home = card.get_attribute("data-is-home")
        has_child = card.get_attribute("data-has-child")

        #value_text = values.get(value, int(value) + 1)
        value_num = int(value)
        #suit_text = suits.get(suit, f"Unknown({suit})")
        suit_num = int(suit)
        state = "Закрыта" if is_open == 'false' else "Открыта"
        data = "В игре" if in_home == 'false' else "Не в игре"
        child = "Без пары" if has_child == 'false' else "С парой"

        in_deck = "В колоде" if num > 27 else "Нет"
        card_dict[num] = [value_num, suit_num, state, in_deck, temp_dict[num][4] if temp_dict else data, child]
        '''if card_dict[num][4] == "Не в игре":
            print(card_dict[num])'''
        #print(f"{value_text} {suit_text} | {state} {in_deck}")

    #print(card_dict)
    #time.sleep(1)
    for k, v in card_dict.items():
        if card_dict[k][2] == "Открыта" and card_dict[k][4] == "В игре":
            open_card_dict[k] = v
            #print(open_card_dict)
            s = str(open_card_dict[k][1])
            print(s)
            # Чтобы карты могли 'выйти из игры'
            home_diff = (abs(out_card_dict[s] - open_card_dict[k][0]) == 1) and (open_card_dict[k][5] == "Без пары" and open_card_dict[k][4] == "В игре" and open_card_dict[k][2] == "Открыта")
            # Условие, убирающее короля на пустую клетку
            if (placeholders and open_card_dict[k][0] == 12) or home_diff:
                if home_diff:
                    out_card_dict[s] = open_card_dict[k][1]
                    print(f"КАРТА ВЫШЛА ИЗ ИГРЫ: {open_card_dict[k]}")
                card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{int(k) + 15}]')
                f_click_card_top(card_btn)
                card_dict[k][4] = "Не в игре"
                f_opener(card_dict)
                return
        '''if card_dict[k][0] == 0 and card_dict[k][2] == "Открыта" and card_dict[k][4] == "В игре":
            card_btn = driver.find_element(By.XPATH,f'/html/body/main/div[1]/div[1]/div/div/div[{int(k) + 15}]')
            f_click_card_top(card_btn)
            card_dict[k][4] = "Не в игре"
            f_opener(card_dict)
            return'''
    #time.sleep(0.3)
    #print(open_card_dict)

# Основная поисковая функция
def f_solver():
    f_opener(card_dict)
    for k_first, v_first in open_card_dict.items():
        for k_second, v_second in open_card_dict.items():
            if k_first == k_second:
                continue
            first = open_card_dict[k_first][0]
            second = open_card_dict[k_second][0]
            #print(f"first - {first} : second - {second}")
            formula = first - second == 1
            #print(formula)
            if formula and (open_card_dict[k_first][1] + open_card_dict[k_second][1]) % 2 != 0 and open_card_dict[k_second][4] == "В игре" and open_card_dict[k_first][5] == "Без пары" and open_card_dict[k_first][3] != "В колоде":
                if open_card_dict[k_second][3] == "В колоде":
                    open_card_dict[k_second][3] = "Нет"
                try:
                    #print(card_dict[k_second])
                    card_btn = driver.find_element(By.XPATH, f'/html/body/main/div[1]/div[1]/div/div/div[{k_second + 15}]')
                    #time.sleep(0.3)
                    f_click_card_top(card_btn)
                    card_dict[k_second][4] = "Не в игре"
                except Exception as e:
                    print(k_second)
                    print(e)
                print(f"first close - {card_dict[k_first]}")
                print(f"first open - {open_card_dict[k_first]}")
                print(f"second close - {card_dict[k_second]}")
                print(f"second open - {open_card_dict[k_second]}")
                print(open_card_dict)
                print('clicked')
                #print(f"СЛОВАРЬ - {open_card_dict}")
                f_solver()
                return
    print("Ходов не осталось. Открываю колоду.")

def main():
    f_opener()
    while True:
        f_solver()
        f_open_deck()
        if not f_open_deck():
            print('Остановка программы')
            time.sleep(999999)
            break
main()



















# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[36] - card 21
# /html/body/main/div[1]/div[1]/div/div/div[15] - card 0
# /html/body/main/div[1]/div[1]/div/div/div[42] - card 27

# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[39] - card 24
# /html/body/main/div[1]/div[1]/div/div/div[13]/div - пустое поле 2
# /html/body/main/div[1]/div[1]/div/div/div[14]/div - пустое поле 1