from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import re

counterRefreshed = 0
counterSkipped = 0
username = "YOUR USERNAME"
password = "YOUR PASSWORD"

def elem(id):
    # Wait for the element to be present
    return WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, id)))

def findallByClassName(className, regex):
    # Wait for the element to be present
    rawElem = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, className)))
    rawText = str(rawElem.get_attribute("innerHTML"))
    return re.findall(regex, rawText)

def setTextForId(id, text):
    element = elem(id)
    element.clear()
    element.send_keys(text)

def login():
    print("Entering credentials")
    setTextForId("username", username)
    setTextForId("password", password)
    print("Logging in")
    elem("password").send_keys(Keys.ENTER)
    if "Free" in driver.title:
        login()

def getRoutes():
    print("Getting Routes:")
    routes = findallByClassName("priceTable", "/\w{9}/\w{7}/[0-9]{3,10}")
    print(len(routes))
    return routes

def refreshPrice(route):
    global counterSkipped
    global counterRefreshed

    print("Working on Route: " + route.split("/")[3])
    while driver.current_url != "https://www.airlines-manager.com" + route:
        driver.get("https://www.airlines-manager.com" + route)

    # ensure page is loaded
    try:
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#priceSimulation")))
    except:
        pass

    # check if price can be changed
    try:
        # wait for loading
        wait = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".amcountdown"))).get_attribute("data-timeremaining")
        
        print(f"Timer is still running!\n{int(wait)} seconds left!\nNothing to do here")
        counterSkipped += 1
        return
    except:
        pass

    # perform audit
    driver.get("https://www.airlines-manager.com/marketing/internalaudit/line/" + route.split("/")[3] + "?fromPricing=1")

    # extract prices
    ideals = []
    for ideal in findallByClassName("box1", "\$[0-9]{1,},?[0-9]{1,3}"):
        if "," in ideal:
            ideals.append(int(ideal.replace("$","").replace(",","")))
        else:
            ideals.append(int(ideal.replace("$","")))
    print(ideals)

    currents = []
    for current in findallByClassName("box2", "\$[0-9]{1,},?[0-9]{1,3}"):
        if "," in current:
            currents.append(int(current.replace("$","").replace(",","")))
        else:
            currents.append(int(current.replace("$","")))
    print(currents)

    if currents == ideals:
        print("Prices are already ideal!")
        counterSkipped += 1
        return

    setTextForId("line_priceEco", ideals[0])
    setTextForId("line_priceBus", ideals[1])
    setTextForId("line_priceFirst", ideals[2])
    setTextForId("line_priceCargo", ideals[3])
    
    while 1:
        try:
            # wait for timer to show
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".amcountdown")))
            counterRefreshed += 1
            return
        except:
            try:
                elem("line_priceEco").send_keys(Keys.ENTER)
            except:
                pass
    
    print("Something went wrong!")

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://www.airlines-manager.com/marketing/pricing/?airport=0")

    login()
    
    # wait while loading
    #while "Airlines Manager 2" in driver.title:
    #    sleep(1)
    #print("Logged in!")

    tot = 0
    page = 1
    while 1:
        # retrive routes
        print()
        routes = getRoutes()

        if len(routes) == 0:
            print()
            print("No more routes to refresh!")
            break

        tot += len(routes)
        # refresh prices
        for i in range(0, len(routes)):
            print()
            refreshPrice(routes[i])
            print(f"Refreshed {counterRefreshed} line(s)")
            print(f"Skipped {counterSkipped} line(s)")
            print(f"Scanned {counterRefreshed + counterSkipped} out of {tot} so far!")    

        page += 1
        driver.get("https://www.airlines-manager.com/marketing/pricing/?airport=0&page=" + str(page))
