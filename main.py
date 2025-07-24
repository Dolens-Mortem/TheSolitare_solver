from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

url = "https://thesolitaire.com/ru/"

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 999999)
driver.get(url)

# Загрузка
time.sleep(5)

cards = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='card']")

print(f"Найдено карт: {len(cards)}")

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

# Вывод в консоли (масть, значение, открыта или закрыта)
for card in cards:
    suit = card.get_attribute("data-suit")
    value = card.get_attribute("data-value")
    is_open = "isOpen" in card.get_attribute("class")

    value_text = values.get(value, int(value) + 1)
    suit_text = suits.get(suit, f"Unknown({suit})")
    state = "Открыта" if is_open else "Закрыта"
    print(f"{value_text} {suit_text} | {state}")

time.sleep(99999)
