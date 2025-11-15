# login_to.py
import os
import time
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException 
from webdriver_manager.chrome import ChromeDriverManager

# --- Настройки ---
URL = "https://uniportal.huawei.com/uniportal1/login-pc.html?redirect=https%3A%2F%2Fsupport.huawei.com%2Fenterprise%2Fen%2Findex.html#/passwordLogin"
# Получаем логин/пароль из переменных окружения или спрашиваем у пользователя
USERNAME = os.getenv("HUAWEI_USER") or input("Login (email/phone/ID): ").strip()
PASSWORD = os.getenv("HUAWEI_PASS") or getpass.getpass("Password: ")
part_number = '02355FRF' 

# Опции браузера
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # <-- раскомментируйте при необходимости (без GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117 Safari/537.36")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")

#chrome_options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

def try_select_and_send(selectors, value):
    """Попробуем несколько селекторов, вернём True если удачно."""
    for sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            el.clear()
            el.send_keys(value)
            return True
        except Exception:
            continue
    return False

def try_click(selectors):
    for sel in selectors:
        try:
            el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            el.click()
            return True
        except Exception:
            continue
    return False

try:
    driver.get(URL)

    # Иногда сайт автоматически редиректит на страницу логина /passport/ и т.п.
    # Подождём и попытаемся найти поля ввода на странице
    time.sleep(1)

    # Набор возможных селекторов для полей логина и пароля.
    login_selectors = [
        'input[name="username"]',
        'input[type="email"]',
        'input[type="text"]',
        'input[name="login"]',
        'input[name="account"]',
        'input[id*="user"]',
        'input[id*="login"]'
    ]
    password_selectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[id*="passwd"]',
        'input[id*="password"]'
    ]

    filled_login = try_select_and_send(login_selectors, USERNAME)
    filled_pass = try_select_and_send(password_selectors, PASSWORD)

    if not (filled_login and filled_pass):
        print("Не удалось найти/заполнить одно из полей автоматически. Попробуйте открыть браузер и войти вручную.")
        print("Оставляю браузер открытым для ручного завершения входа.")
        # Оставляем браузер открытым для ручного ввода; ожидание выхода
        input("После того как войдёте вручную — нажмите Enter здесь...")
    else:
        # Селекторы для кнопки входа
        login_btn_selectors = [
            'button[id="login-btn"]',    
            'button[type="submit"]',
            'button[id*="login"]',
            'button[class*="login"]',
            'input[type="submit"]'
        ]
        clicked = try_click(login_btn_selectors)
        if not clicked:
            driver.save_screenshot("huawei_failed_login.png")
            print("Кнопка 'Войти' не найдена — оставляю браузер открытым для ручного нажатия.")
            input("После того как войдёте вручную — нажмите Enter здесь...")
        else:
            # после клика — возможно появится капча/2FA или редирект
            # ждём либо завршения редиректа (изменение URL), либо появления элемента, указывающего, что мы в аккаунте
            # Попробуем дождаться появления какого-либо элемента личного кабинета (обычно там avatar, профиль и т.п.)
            try:
                # ждём до появления одного из индикаторов
                found = False
                try:
                    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "account-info")))
                    found = True
                except Exception as e:
                    print("exception ",type(e).__name__)
                
                if found:
                    print("Успешно вошли (по индикатору страницы).")
                else:
                    print("Вход возможно требует дополнительной проверки (CAPTCHA / 2FA).")
                    print("Оставляю браузер открытым для ручного завершения входа.")
                    input("После завершения входа вручную — нажмите Enter здесь...")
            except Exception as e:
                print("Во время ожидания произошла ошибка:", e)
                input("Нажмите Enter после ручного завершения входа...")
finally:
    pass

URL = "https://info.support.huawei.com/storageinfo/spareparts/#/home"
try:
    driver.get(URL)
    try:
        element = WebDriverWait(driver, 10).until(                           \
              EC.presence_of_element_located((By.ID, "ti_auto_id_16_input"))) 
        
        element.send_keys(part_number)
        element.send_keys(Keys.ENTER)

        element.clear()
        element = WebDriverWait(driver, 10).until(                           \
              EC.presence_of_element_located(                                \
                  (By.CLASS_NAME, "ant-descriptions-view")                   \
              )
        )         
        
    except Exception as e:
        print("Eception ",e)

except:
    pass

finally:
    pass

part = []
substs = []
try:
    elements = driver.find_elements(By.CLASS_NAME, "des-box")
    amount = len(elements)
    for sub in elements[:-2]:
        desc = sub.find_elements(By.CLASS_NAME, "ant-descriptions-row")
        for row in desc:
            elm = row.find_elements(By.TAG_NAME, 'td')
            if elm[0].text == 'BOM Number':
                substs.append(elm[1].text)

    rows = elements[-1].find_elements(By.CLASS_NAME, "ant-descriptions-row")
    for row in rows:
        elm = row.find_elements(By.TAG_NAME, 'td')
        if elm[0].text == 'BOM Number':
            part.append(elm[1].text)
        if elm[0].text == 'Description':
            part.append(elm[1].text)

except:
    pass
finally:
    driver.quit()

print(part[1])
print(substs)
