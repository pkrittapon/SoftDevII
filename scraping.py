from selenium import webdriver
from selenium.webdriver.common.by import By
crypto = webdriver.Chrome()
crypto.get("https://www.investing.com/crypto/bitcoin")
crypto_price = crypto.find_element(By.XPATH,'//*[@id="last_last"]').text
print(crypto_price)