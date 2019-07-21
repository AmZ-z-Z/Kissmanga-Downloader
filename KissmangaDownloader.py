# Global Variables
import sys, os

# Disable Console print
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore  Console print
def enablePrint():
    sys.stdout = sys.__stdout__

CWD = os.getcwd()
MangaName = ""

def ChaptersLinkGrabber( Manga_URL ):
	import cfscrape,re
	from bs4 import BeautifulSoup

	ChaptersList=list()
	
	# Returns a CloudflareScraper instance to bypass its DDOS protection
	web_scraper = cfscrape.create_scraper()  
	Result = web_scraper.get( Manga_URL )
	
	# Checks of Request succeeded(200) or not
	if str(Result) == '<Response [200]>':
		# Containts all the HTML data of the webpage.
		src = Result.content
	
		# BeautifulSop is an HTML parser that handles tags and find whatever you need.
		soup=BeautifulSoup( src , features = "html.parser" )
		# Find all link elements
		PageLinks = soup.find_all("a")
		
		# Extract all chapter links using Regex and append it to a list.
		for link in PageLinks:
			match = re.findall(r'(?<=\")(/Manga/.+\d)(?=\"\s)',str(link))
			# If Expression matchs insert it to the begining of the list.
			if match:
				ChaptersList.insert( 0 , "https://kissmanga.com"+str(match[0]) )

		return ChaptersList

def ImagesLinkExtractor( Chapter_Link ):
	import time,re,urllib.request,os
	from bs4 import BeautifulSoup
	from selenium import webdriver
	from selenium.webdriver.chrome.options import Options
	from webdriver_manager.chrome import ChromeDriverManager   
	
	# Change Directory to the Manga Folder
	global MangaName
	os.chdir(CWD+"\\"+MangaName)
	# Parse the Manga Chapter number.
	ChapterNumber = re.findall(r'(?<=Ch-)(\d+)(?=)',str(Chapter_Link))
	# If failed to parse using thise formula.
	if not ChapterNumber:
			ChapterNumber = re.findall(r'\d\d\d',str(Chapter_Link))
	# Create a folder with the current chapter number.
	if not os.path.exists(str(ChapterNumber[0])):
		os.mkdir(str(ChapterNumber[0]))
		FileVersion = str(ChapterNumber[0])
	elif not os.path.exists(str(ChapterNumber[0])+" V2 "):
		os.mkdir(str(ChapterNumber[0])+" V2 ")
		FileVersion = str(ChapterNumber[0])+" V2 "
	else: 
		os.mkdir(str(ChapterNumber[0])+" V3 ")
		FileVersion = str(ChapterNumber[0])+" V3 "
	# Change Directory to the new Chapter folder.
	os.chdir(os.getcwd()+"\\"+FileVersion)

	blockPrint()
	# Set a class of chrome options
	myChromeOptions = webdriver.ChromeOptions();
	# Make chrome Headless(No GUI) 
	myChromeOptions.add_argument("--headless");
	# Blink(doesn't load image) to save data.
	myChromeOptions.add_argument("--blink-settings=imagesEnabled=false");
	# Sets the minimum log level. Valid values are from 0 to 3: INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3.
	myChromeOptions.add_argument("log-level=3")
	# Disable Console Log Errors.	
	myChromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
	
	# Check if chrome is installed or not, and if not install it and enable its previous chosen options
	myWebDriver = webdriver.Chrome( ChromeDriverManager().install(), options = myChromeOptions )
	# Load Chapter link and wait 6 seconds till Cloudfire DDOS protection finishes loading
	myWebDriver.get(Chapter_Link)
	time.sleep(6)
	# Save HTML content after JavaScript finishes injecting the Images links.
	myChapterHtml = myWebDriver.page_source
	# Close WebDriver
	myWebDriver.quit()
	# Load HTML src to BeautifulSoup Parser.
	ImgsSoup = BeautifulSoup ( myChapterHtml , features="html.parser" )
	# Extract all Img Elements and parse the Chapter images.
	ImgLinks = ImgsSoup.find_all('img')
	ImgMatch=re.findall(r'(?<=\")(https://2\.bp.\S+)(?=\"/)',str(ImgLinks))
	enablePrint()
	ImgList = []
	ImageIndex = 0
	print("Downloading Chapter "+ str(ChapterNumber[0]) +" Images")
	for ImgLink in ImgMatch:
		if ImgLink:
			urllib.request.urlretrieve( str(ImgLink) , str(ImageIndex)+".png")
			ImgList.append( str(ImageIndex)+".png" )
			ImageIndex += 1;
	ImageVerticalConcatination(ImgList)
	os.chdir(CWD)

def ImageVerticalConcatination(ImgList):
	import numpy,PIL,time 
	from PIL import Image
	# Set up three empty lists for future use.
	Imgs=[] ; ImgSize=[] ; CombinedImgs=[]
	# Open all the Downloaded images using Pything Image Library in a list.
 	for OrigImg in ImgList:
		Imgs.append(PIL.Image.open(OrigImg))
	# Get the size of the image width and 
	for Img in Imgs:
		ImgSize.append((numpy.sum(Img.size),Img.size))
	ImgSize = sorted(ImgSize)

	for OrigImg in Imgs:
		NewImg = OrigImg.resize((ImgSize[0][1][0],OrigImg.size[1]), Image.ANTIALIAS)
		NewImg = NewImg.convert('RGB')
		CombinedImgs.append(numpy.asarray(NewImg))

	CombinedImgsNewV = numpy.vstack(CombinedImgs)
	CombinedImgsNewV = PIL.Image.fromarray(CombinedImgsNewV)
	CombinedImgsNewV.save("Vertical.png")

	# for IMG in ImgList:
		# os.remove(IMG)

def main():
	import re
	# URL ="https://kissmanga.com/Manga/Solo-Leveling"
	# Request URL from user.
	URL = input("Please Enter the Manga URL")
	print(URL)
	exit()
	# Extract Manga Name.
	NameMatch = re.findall( r'(?<=Manga\/)(.+)(?=)' , str(URL))
	global MangaName
	MangaName = NameMatch[0]

	if NameMatch:
		# Check if there's already a folder else make a new one.
		if not os.path.exists(NameMatch[0]):
			os.mkdir(NameMatch[0])
		# Extract Chapter Links.
		ExtractedLinks = ChaptersLinkGrabber(URL)
		for Chapter in ExtractedLinks:
			ImagesLinkExtractor(Chapter)
	else:
		print("Couldn't Extract Manga Name")

if __name__=="__main__":
	main()
                                                                                                                
