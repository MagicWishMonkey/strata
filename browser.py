from selenium import webdriver
from selenium.webdriver.common.keys import Keys


driver = webdriver.Firefox()
driver.get("http://apply-dev.balancecredit.com/loan-application/")


def set(e, v):
    element = driver.find_element_by_id(e)
    tag_name = element.tag_name
    if tag_name == "select":
        v = v.strip().lower()
        all_options = element.find_elements_by_tag_name("option")
        for option in all_options:
            #print("Value is: %s" % option.get_attribute("value"))
            if option.get_attribute("value").strip().lower() == v:
                option.click()
                return
        return
    element.send_keys(v)


set("id_firstname", "RON")
set("id_lastname", "RODENBERG")
set("id_email1", "ron@whoat.net")
set("id_password1", "Dallas21")
set("id_password2", "Dallas21")
set("id_street_address", "3809 63rd Drive")
set("id_apt_number", "#128")
set("id_zip_code", "65603")
set("id_city", "ARCOLA")
set("id_state", "MO")
set("id_length_at_address", "five_plus_years")
set("id_home_phone", "(214) 659-1008")
set("id_cell_phone", "(469) 853-8716")

driver.find_elements_by_name("housing_type")[1].click()
driver.find_elements_by_name("military_duty")[1].click()
set("id_employer_name", "Google")
set("id_employer_phone", "(845) 664-1341")
set("id_length_at_employer", "five_plus_years")
set("id_take_home_amount", "2000.00")
set("id_income_frequency", "S") #semi-monthly
set("id_first_payday_of_month", "15")
set("id_second_payday_of_month", "32")
set("id_social_security_number", "666-55-1234")
set("id_dob_month", "4")
set("id_dob_day", "2")
set("id_dob_year", "1980")
set("id_drivers_license_or_id", "T140241998")
set("id_state_issued", "MO")
set("id_loan_reason", "major-purchase")
set("id_bank_name", "Bank Of America")
set("id_bank_phone", "(845) 664-1341")
set("id_account_usage_length", "five_plus_years")
set("id_routing_number", "021200339")
set("id_account_number", "0639259481")

driver.find_element_by_id("id_termsofservice_1").click()
driver.find_element_by_id("id_termsofservice_2").click()
driver.find_element_by_id("id_termsofservice_3").click()
driver.find_element_by_id("id_termsofservice_4").click()

driver.close()