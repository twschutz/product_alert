import requests 
from time import sleep 
import time 
import schedule 
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Set target URLs for websites to monitor for stock changes
bestbuyUrl = "https://www.bestbuy.com/site/sony-playstation-5-digital-edition-console/6430161.p?skuId=6430161"
targetUrl = "https://www.target.com/p/playstation-5-digital-edition-console/-/A-81114596"
walmartUrl = "https://www.walmart.com/ip/PlayStation5-Console/493824815"
gamestopUrl = "https://www.gamestop.com/video-games/playstation-5/consoles/products/playstation-5/11108140.html"

#Sends a text with content "bodyText" from the specified email to the specified phone number
def sendText(bodyText):
    email = "youremail@gmail.com"
    password = "yourpass"
    #Different carriers will have different extensions
    sms_gateway = 'yourphonenumber@txt.att.net'
    #Different email providers will have different extensions and ports
    smtp = "smtp.gmail.com"
    port = 587
    server = smtplib.SMTP(smtp, port)
    server.starttls()
    server.login(email, password)

    #Crafts the message to be sent 
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway
    msg['Subject'] = "PS5 Stock Info\n"
    body = bodyText + '\n'
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    #Sends the message to the specified phone number
    server.sendmail(email, sms_gateway, sms)

    server.quit()

#Gets the HTML text content from the specified URL page
def getHTML(url):
    #Headers included to make the automated system seem like a real user
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    page = requests.get(url, headers=headers)
    #print(page.status_code) #Testing code to print the status when loading the webpage. Expected to be 200
    return page.text

#Checks if the item is in stock at BestBuy
def checkInStockBB(pageHTML):
    #Utilizes BeautifulSoup to parse the HTML content
    text = BeautifulSoup(pageHTML, 'html.parser')
    #Find all instances of the "Sold Out" button
    outOfStockBB = text.findAll("button", {"class": "btn btn-disabled btn-lg btn-block add-to-cart-button"})
    if len(outOfStockBB) == 0:
        sendText("In Stock at BestBuy!")
    else:
        print("Out of Stock at BestBuy!")

#Checks if item is in stock at GameStop
def checkInStockGS(pageHTML):
    text = BeautifulSoup(pageHTML, 'html.parser')
    #Find all instances of unavailable banner for product
    outOfStockBB1 = text.findAll("span", {"class": "delivery-home-stock-msg hide"})
    outOfStockBB2 = text.findAll("span", {"class": "delivery-unavailable text-uppercase hide"})
    if (len(outOfStockBB1) + len(outOfStockBB2)) == 0 :
        sendText("In Stock at Gamestop!")
    else:
        print("Out of Stock at Gamestop!")

#Checks if item is in stock at Target, NEEDS FIX
def checkInStockTA(pageHTML):
    text = BeautifulSoup(pageHTML, 'html.parser')
    #Currently does not work
    outOfStockTA = text.findAll("div", text="Out of stock in stores near you")
    if len(outOfStockTA) == 0:
        sendText("In Stock at Target!")
    else:
        print("Out of Stock at Target!")

#Checks if item is in stock at Walmart
def checkInStockWM(pageHTML):
    text = BeautifulSoup(pageHTML, 'html.parser')
    #Find all instances of error page message
    outOfStockWM = text.findAll("div", {"class": "error-message-margin error-page-message"})
    if len(outOfStockWM) == 0:
        sendText("In Stock at Walmart!")    
    else:
        print("Out of Stock at Walmart")

#Queue a job to check all of the stores
def job(): 
    checkInStockBB(getHTML(bestbuyUrl))
    #checkInStockTA(getHTML(targetUrl))
    checkInStockWM(getHTML(walmartUrl))
    checkInStockGS(getHTML(gamestopUrl))

#Schedule the job to run every 2 minutes
schedule.every(2).minutes.do(job)

#Run the job as long as the user wants
while True:
    schedule.run_pending()
    time.sleep(1)