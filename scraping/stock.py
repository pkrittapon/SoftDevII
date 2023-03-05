from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.set.or.th/th/market/index/set/overview")

set_price = driver.find_element(By.XPATH,'//*[@id="__layout"]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/h1').text
print(set_price)