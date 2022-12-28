# pylint: skip-file
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome("D:\Apps\Windows\Web Browsers\Chrome Setup\chromedriver.exe")
driver.get("http://127.0.0.1:8000/")


def page_down():
    body = driver.find_element_by_css_selector("body")
    body.click()
    body.send_keys(Keys.PAGE_DOWN)


def page_up():
    body = driver.find_element_by_css_selector("body")
    body.click()
    body.send_keys(Keys.PAGE_UP)


# Drive Code

# Home Page
time.sleep(5)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)
page_up()
time.sleep(2)

# See Records
see_data = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[2]/a')
see_data.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)

next_btn = driver.find_element_by_xpath("/html/body/div[3]/div/div/ul/li[4]/a")
next_btn.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)
page_up()
time.sleep(2)

# Home Page
home = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[1]/a')
home.click()
time.sleep(2)
page_down()
time.sleep(2)

# Satyam Detailed
satyam_detailed = driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/a")
satyam_detailed.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)
driver.back()
time.sleep(2)

# Ankit Detailed
ankit_detailed = driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/div/a")
ankit_detailed.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)
driver.back()
time.sleep(2)

# Ganga Detailed
ganga_detailed = driver.find_element_by_xpath("/html/body/div[4]/div/div[3]/div/a")
ganga_detailed.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)
driver.back()
time.sleep(2)

# Prashant Detailed
prashant_detailed = driver.find_element_by_xpath("/html/body/div[4]/div/div[4]/div/a")
prashant_detailed.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)

# Water Record
home = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[1]/a')
home.click()
time.sleep(2)
page_down()
time.sleep(2)
page_down()
time.sleep(2)
page_down()
time.sleep(2)

water_detailed = driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div/a")
water_detailed.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_up()
time.sleep(2)
page_up()
time.sleep(2)

# Progress Report
progress_report = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/ul/li[3]/a'
)
progress_report.click()
time.sleep(5)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_down()
time.sleep(5)

# Login
login = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[6]/a')
login.click()
time.sleep(2)
login_btn = driver.find_element_by_xpath(
    "/html/body/div[2]/div/div/div[2]/form/div[3]/input"
)
login_btn.click()

time.sleep(2)
username = driver.find_element_by_xpath('//*[@id="id_username"]')
username.send_keys("user123")
time.sleep(0.5)
password = driver.find_element_by_xpath('//*[@id="id_password"]')
password.send_keys("root@123")
time.sleep(0.5)
login_btn = driver.find_element_by_xpath(
    "/html/body/div[2]/div/div/div[2]/form/div[3]/input"
)
login_btn.click()

time.sleep(2)
username = driver.find_element_by_xpath('//*[@id="id_username"]')
username.clear()
username.send_keys("root")
time.sleep(0.5)
password = driver.find_element_by_xpath('//*[@id="id_password"]')
password.send_keys("root@123")
login_btn = driver.find_element_by_xpath(
    "/html/body/div[2]/div/div/div[2]/form/div[3]/input"
)
time.sleep(0.5)
login_btn.click()
time.sleep(2)
notification = driver.find_element_by_xpath("/html/body/div[3]/div/button/span")
notification.click()
time.sleep(2)

# Add Data
add_data = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[2]/a')
add_data.click()
time.sleep(2)
page_down()
time.sleep(5)

item = driver.find_element_by_xpath('//*[@id="id_item"]')
item.send_keys("Egg (1 Tray)")
time.sleep(1)
price = driver.find_element_by_xpath('//*[@id="id_price"]')
price.send_keys("120")
time.sleep(1)
add_item = driver.find_element_by_xpath("/html/body/div[4]/form/button[2]")
add_item.click()
time.sleep(2)

notification = driver.find_element_by_xpath("/html/body/div[3]/div/button/span")
notification.click()
time.sleep(2)
page_down()
time.sleep(5)

add_water = driver.find_element_by_xpath("/html/body/div[5]/form/button[2]")
add_water.click()
time.sleep(2)
notification = driver.find_element_by_xpath("/html/body/div[3]/div/button/span")
notification.click()
time.sleep(2)

# Logout
logout = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[7]/a')
logout.click()
time.sleep(2)
notification = driver.find_element_by_xpath("/html/body/div[3]/div/button/span")
notification.click()
time.sleep(2)

# Search Item
search_bar = driver.find_element_by_name("query")
search_bar.send_keys("Egg")
time.sleep(2)
search_btn = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/form/button'
)
search_btn.click()
time.sleep(2)
page_down()
time.sleep(5)
page_down()
time.sleep(5)
page_down()

search_bar = driver.find_element_by_name("query")
search_bar.send_keys("Apple")
time.sleep(2)
search_btn = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/form/button'
)
search_btn.click()
time.sleep(2)
page_down()
time.sleep(5)

# More: Download
more = driver.find_element_by_xpath('//*[@id="navbarDropdown"]')
more.click()
time.sleep(2)
download = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/ul/li[5]/div/a[1]'
)
download.click()
time.sleep(2)
page_down()
time.sleep(5)

for i in range(1, 6):
    download_btn = driver.find_element_by_xpath(
        f"/html/body/div[3]/div/table/tbody/tr[{i}]/td/a"
    )
    download_btn.click()
    time.sleep(5)

# More: Feedback
more = driver.find_element_by_xpath('//*[@id="navbarDropdown"]')
more.click()
time.sleep(2)
download = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/ul/li[5]/div/a[2]'
)
download.click()
time.sleep(2)
page_down()
time.sleep(5)

name = driver.find_element_by_xpath('//*[@id="id_name"]')
name.send_keys("Ganga Sagar Bharti")
time.sleep(0.5)
problem = driver.find_element_by_xpath('//*[@id="id_problem"]')
problem.send_keys("Business Idea")
time.sleep(0.5)
message = driver.find_element_by_xpath('//*[@id="id_message"]')
message.send_keys("Make it a general product.")
time.sleep(0.5)
submit = driver.find_element_by_xpath("/html/body/div[3]/form/div[3]/button")
submit.click()
time.sleep(2)
notification = driver.find_element_by_xpath("/html/body/div[3]/div/button/span")
notification.click()
time.sleep(5)

# Admin Panel
more = driver.find_element_by_xpath('//*[@id="navbarDropdown"]')
more.click()
time.sleep(2)
admin = driver.find_element_by_xpath(
    '//*[@id="navbarSupportedContent"]/ul/li[5]/div/a[3]'
)
admin.click()

# Login Password Forget
time.sleep(10)
login = driver.find_element_by_xpath('//*[@id="navbarSupportedContent"]/ul/li[6]/a')
login.click()
time.sleep(5)
forget_btn = driver.find_element_by_xpath(
    "/html/body/div[2]/div/div/div[2]/form/div[3]/a"
)
forget_btn.click()
