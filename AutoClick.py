import pyautogui

from PIL import Image

from PIL import ImageGrab

import pytesseract

import cv2

import time

import numpy as nm

import configparser

import os

import keyboard

import threading



#SECOND THREAD FOR CLOSING PROGRAM
#function that uses the method "wait" from the keyboard-module which holds/stops the function untill a user presses esc, then the function will continue and close the whole porgram
def escPressed():
    keyboard.wait('esc')
    os._exit(1)

#defines a thread that runs the escPressed function
exitThread = threading.Thread(target=escPressed, daemon=True)

#starts the exitThread, so that the escPressed function runs as thread besides the main program. It handels the exit from the program.
exitThread.start()





#IMPORT OF SETTINGS AND DEFINING OF PATHS
#Defines the path of folder
pathOfFolder = os.path.dirname(os.path.abspath(__file__))

#Defines the path of the tesseract executable, so that it can be called when running OCR
pytesseract.pytesseract.tesseract_cmd = (pathOfFolder + r'\Tesseract\tesseract.exe')

#Opens in read mode the settings file SETTINGS.INI found in the folder Settings
config = configparser.ConfigParser()
config.read(pathOfFolder +'\Settings\SETTINGS.INI')

#Defines variables for the DEFAULT part of settings
timeBeforeRunning = int(config['DEFAULT']['timeBeforeRunning'])
clickSpeed = float(config['DEFAULT']['clickSpeed'])
amountOfPlayersInList = int(config['DEFAULT']['amountOfPlayersInList'])
scrollDownPause = float(config['DEFAULT']['scrollDownPause'])

#Defines variables for the PLAYER.VALUES part of settings
praiseNumber = float(config['PLAYER.VALUES']['praiseNumber'])
criticizePlayers = config.getboolean('PLAYER.VALUES','criticizePlayers')
criticizeNumber = float(config['PLAYER.VALUES']['criticizeNumber'])

#Defines variables for the PIXEL.VALUES part of settings
firstPlayerXValue = int(config['PIXEL.VALUES']['firstPlayerXValue'])
firstPlayerYValue = int(config['PIXEL.VALUES']['firstPlayerYValue'])
distanceInbetweenPlayers = int(config['PIXEL.VALUES']['distanceInbetweenPlayers'])

amountOfPlayersTopLeftXValue = int(config['PIXEL.VALUES']['amountOfPlayersTopLeftXValue'])
amountOfPlayersTopLeftYValue = int(config['PIXEL.VALUES']['amountOfPlayersTopLeftYValue'])
amountOfPlayersBottomRightXValue = int(config['PIXEL.VALUES']['amountOfPlayersBottomRightXValue'])
amountOfPlayersBottomRightYValue = int(config['PIXEL.VALUES']['amountOfPlayersBottomRightYValue'])

statNumberTopLeftXValue = int(config['PIXEL.VALUES']['statNumberTopLeftXValue'])
statNumberTopLeftYValue = int(config['PIXEL.VALUES']['statNumberTopLeftYValue'])
statNumberBottomRightXValue = int(config['PIXEL.VALUES']['statNumberBottomRightXValue'])
statNumberBottomRightYValue = int(config['PIXEL.VALUES']['statNumberBottomRightYValue'])

praiseXValue  = int(config['PIXEL.VALUES']['praiseXValue'])
praiseYValue = int(config['PIXEL.VALUES']['praiseYValue'])
putArmAroundXValue = int(config['PIXEL.VALUES']['putArmAroundXValue'])
putArmAroundYValue = int(config['PIXEL.VALUES']['putArmAroundYValue'])
praiseSentenceXValue = int(config['PIXEL.VALUES']['praiseSentenceXValue'])
praiseSentenceYValue = int(config['PIXEL.VALUES']['praiseSentenceYValue'])
endConversationXValue = int(config['PIXEL.VALUES']['endConversationXValue'])
endConversationYValue = int(config['PIXEL.VALUES']['endConversationYValue'])

criticizeXValue  = int(config['PIXEL.VALUES']['criticizeXValue'])
criticizeYValue = int(config['PIXEL.VALUES']['criticizeYValue'])
pointXValue = int(config['PIXEL.VALUES']['pointXValue'])
pointYValue = int(config['PIXEL.VALUES']['pointYValue'])
criticizeSentenceXValue = int(config['PIXEL.VALUES']['criticizeSentenceXValue'])
criticizeSentenceYValue = int(config['PIXEL.VALUES']['criticizeSentenceYValue'])

#Defines variables for the IMAGE.PROCESSING part of settings
imageResizingPercent = int(config['IMAGE.PROCESSING']['imageResizingPercent'])
invertColours = config.getboolean('IMAGE.PROCESSING','invertColours')





#"MAIN THREAD"/PROGRAM

#Program is halted, so that users can alt-tab to correct window
time.sleep(timeBeforeRunning)

#Function that selects all players by clicking on the first player and pressing the ctrl+a shortcut. It pauses inbetween each press by the amout of time set by the variable clickSpeed.
def selectAllPlayers(clickSpeed, x, y):
    
    pyautogui.PAUSE = clickSpeed
    pyautogui.click(x, y)
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.keyUp('a')
    
#The function selectAllPlayers is called with parameters from the settings 
selectAllPlayers(clickSpeed, firstPlayerXValue, firstPlayerYValue)

#Function that grabs image from part of screen using imageGrab, bbox and pixel placement. To define the part of the screen that is captured two xy-coordinates is passed as the top left and bottom right of a box.
#it takes those xy-coordinates as arguments. It then converts the image to an array, so that cv2 can process it. It makes it greyscale, inverted and rezised for best ocr results. Inversion and rezise is based on variable.
#The image is then saved with the name argument and returned
def grabImageOfScreenAndProcess(topLeftX, topLeftY, bottomRightX, bottomRightY, nameOfSavedImage, invertColours, imageResizingPercent):
    
    imageOfScreen = ImageGrab.grab(bbox =(topLeftX, topLeftY, bottomRightX, bottomRightY))
    imageOfScreen = nm.asarray(imageOfScreen)
    imageOfScreen = cv2.cvtColor(imageOfScreen, cv2.COLOR_BGR2GRAY)
    
    if invertColours == True:
        imageOfScreen = cv2.bitwise_not(imageOfScreen)
    
    width = int(imageOfScreen.shape[1]*(imageResizingPercent/100))
    height = int(imageOfScreen.shape[0]*(imageResizingPercent/100))
    dim = (width, height)
    imageOfScreen = cv2.resize(imageOfScreen, dim, interpolation = cv2.INTER_CUBIC)
       
    saveableImageOfScreen = Image.fromarray(imageOfScreen)
    saveableImageOfScreen.save(pathOfFolder + "\Images/" + nameOfSavedImage + ".jpg")

    return(imageOfScreen)

#Grab image of all selected players
imageOfTotalAmountOfPlayers = grabImageOfScreenAndProcess(amountOfPlayersTopLeftXValue, amountOfPlayersTopLeftYValue, amountOfPlayersBottomRightXValue, amountOfPlayersBottomRightYValue, "totalAmountOfPlayers", invertColours, imageResizingPercent)

#Function that performs OCR on an image and filters the string from the image to either an int or a float. It contains two nested function that either filters based on floats or ints.
def performOCROnImageAndFilter(imageToProcess, intOrFloat):
    stringFromImage = pytesseract.image_to_string(imageToProcess, config='--psm 6')

    def filterFloats(stringToFilter):
        floatCharacters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
        return True if stringToFilter in floatCharacters else False
    
    def filterIntegers(stringToFilter):
        integerCharacters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return True if stringToFilter in integerCharacters else False
    
    if intOrFloat == "int":
        try:
            intFromString = (''.join(filter(filterIntegers, stringFromImage)))
            return(int(intFromString[:2]))
        except:
            os._exit(1)
    
    elif intOrFloat == "float":
        try:
            floatFromString = (''.join(filter(filterFloats, stringFromImage)))
            return(float(floatFromString[:4]))
        except:
            os._exit(1)
            
#Perform OCR of the image of total amount of players and returns number of players as int
totalAmountOfPlayers = performOCROnImageAndFilter(imageOfTotalAmountOfPlayers, "int")

#Two variables for the while-loop is set as conditions and x and y is set as the pixels for the first player
goodStat = True
n = 0
x = firstPlayerXValue
y = firstPlayerYValue

#Function that clicks through the chat options for praisining, and takes the xy cordinates as arguments
def praiseClicker(praiseX, praiseY, putArmAroundX, putArmAroundY, praiseSentenceX, praiseSentenceY, endConversationX, endConversationY):
    pyautogui.click(praiseX, praiseY)
    pyautogui.click(putArmAroundX, putArmAroundY)
    pyautogui.click(praiseSentenceX, praiseSentenceY)
    pyautogui.click(endConversationX, endConversationY)

#Function that clicks through the chat options for criticizing, and takes the xy cordinates as arguments
def criticizeClicker(criticizeX, criticizeY, pointX, pointY, criticizeSentenceX, criticizeSentenceY, endConversationX, endConversationY):
    pyautogui.click(criticizeX, criticizeY)
    pyautogui.click(pointX, pointY)
    pyautogui.click(criticizeSentenceX, criticizeSentenceY)
    pyautogui.click(endConversationX, endConversationY)

#Function that scrolls down through player list
def scrollDown(x, y, amountOfPlayersInList, distanceInbetweenPlayers, scrollDownPause):
    pyautogui.press("left")
    pyautogui.press("right")
    pyautogui.click(x, y)
    pyautogui.press("down", presses=(amountOfPlayersInList*2)-1)
    amountOfPlayersLeft = amountOfPlayersInList-(totalAmountOfPlayers-amountOfPlayersInList)
    y = y + (amountOfPlayersLeft * distanceInbetweenPlayers)
    time.sleep(scrollDownPause)

    return(y)

#Function that increase number of players clicked and the y-cordinate to go down the list of players.
def increaseNAndY(n, y, distanceInbetweenPlayers):
    n = n+1
    y = y+distanceInbetweenPlayers
    return(n, y)

#While-loop that checks each player and prasies, does nothing or criticizes each player. Exits when all have been checked or (if criticize is set to false) exit the script when all positives have been praised.
while totalAmountOfPlayers != n and goodStat == True:

    pyautogui.click(x, y)
    
    #Grab image of selected player's training stat
    imageOfStatNum = grabImageOfScreenAndProcess(statNumberTopLeftXValue, statNumberTopLeftYValue, statNumberBottomRightXValue, statNumberBottomRightYValue, "statNum", invertColours, imageResizingPercent)

    #Perform OCR of the image of statnumber
    statNum = performOCROnImageAndFilter(imageOfStatNum, "float")

#If his trainning stat is higher or equal to PraiseNumber he will be praised
#and the y varialbe is increased to pick the next player and n is increased to keep track of how many players have been praised
    if statNum >= praiseNumber:
        praiseClicker(praiseXValue, praiseYValue, putArmAroundXValue, putArmAroundYValue, praiseSentenceXValue, praiseSentenceYValue, endConversationXValue, endConversationYValue)

        n, y = increaseNAndY(n, y, distanceInbetweenPlayers)

        #Checks to see if the maximum of players on the list (amountOfPlayersInList) has been reached and then scrolls down
        if n == amountOfPlayersInList or n == amountOfPlayersInList*2 or n == amountOfPlayersInList*3 or n == amountOfPlayersInList*4:
            y = scrollDown(firstPlayerXValue, firstPlayerYValue, amountOfPlayersInList, distanceInbetweenPlayers, scrollDownPause)            

    elif criticizePlayers == False:
       #exit while loop and therefore program if criticizePlayers is False
        goodStat = False

    elif statNum < praiseNumber and statNum > criticizeNumber:
        
        n, y = increaseNAndY(n, y, distanceInbetweenPlayers)

        #Checks to see if the maximum of players on the list (amountOfPlayersInList) has been reached and then scrolls down
        if n == amountOfPlayersInList or n == amountOfPlayersInList*2:
            y = scrollDown(firstPlayerXValue, firstPlayerYValue, amountOfPlayersInList, distanceInbetweenPlayers, scrollDownPause)   

    elif statNum <= criticizeNumber:
        
        criticizeClicker(criticizeXValue, criticizeYValue, pointXValue, pointYValue, criticizeSentenceXValue, criticizeSentenceYValue, endConversationXValue, endConversationYValue)

        n, y = increaseNAndY(n, y, distanceInbetweenPlayers)

        #Checks to see if the maximum of players on the list (amountOfPlayersInList) has been reached and then scrolls down
        if n == amountOfPlayersInList or n == amountOfPlayersInList*2:
            
            y = scrollDown(firstPlayerXValue, firstPlayerYValue, amountOfPlayersInList, distanceInbetweenPlayers, scrollDownPause)  

    else:
        #exit while loop and therefore program 
        goodStat = False