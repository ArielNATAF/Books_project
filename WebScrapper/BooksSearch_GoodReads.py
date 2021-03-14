import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P

import pandas as pd
import re
import time
import requests
from urllib.request import urlopen
import bs4

   

def GoodReadsSearchFunction(isbn = None, title = None, author = None):
    ''' Find information on internet about the book entered in function's arguments 
        Either isbn = ..., Or title = ..., author = ... '''
    
    #3 kinds of books identifiers
    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
    #all is reset
    ISBNdict["ISBN_10"] = 0.0
    ISBNdict["ISBN_13"] = 0.0   
    ISBNdict["OtherID"] = 0.0
    autGoodReads = ''
    titleSearched = ''
    autSearched = ''
    pubSearched = ''
    pubData = ''
    catSearched = ''
    descSearched = ''
    awardsSearched = ''
    languageSearched = ''
    pagesSearched = 0
    authorGenreSearched = ''
    goodreadsLinksSeriesList = []

    AUTHORfound = False
    ISBNfound = False
    
    try:
        if(isbn is not None):
            #https://www.goodreads.com/search?q=195153448&qid=
            ISBNdict["ISBN_10"] = isbn
    
            urlIdBookGoodReads_start = "https://www.goodreads.com/search?q={0:0>10s}".format(ISBNdict["ISBN_10"])
            urlIdBookGoodReads_end = '&qid='
            bookUrlForSearch = urlIdBookGoodReads_start + urlIdBookGoodReads_end
#            print(bookUrlForSearch)
            
            source = urlopen(bookUrlForSearch)
            soup = bs4.BeautifulSoup(source, 'html.parser')
            ISBNfound = (soup.find("h1", id="bookTitle") != None)

        else:    
            if ((title != None) and (author != None)):
                urlIdBookGoodReads_start = 'https://www.goodreads.com/search?utf8=%E2%9C%93&q='
                urlIdBookGoodReads_end = '&search_type=books'
                
                titleSearched = title.encode('ascii', 'ignore').decode('ascii')
                autSearched = author.encode('ascii', 'ignore').decode('ascii')
                #We keep only the author familly name
                autSearchedInternal = autSearched.lower().split()[-1]
                
                #First we have to find the book page: we need GoodReads identifier of the book 
                bookUrlForSearch = urlIdBookGoodReads_start + titleSearched.replace(' ', '+') + '+' + autSearchedInternal.replace(' ', '+') + urlIdBookGoodReads_end
#                print(bookUrlForSearch)
                sourceIdBookGoodReads = urlopen(bookUrlForSearch)
                soupIdBookGoodReads = bs4.BeautifulSoup(sourceIdBookGoodReads, 'html.parser')
                
                #Search of the reference compliant with title and author provided, among all proposed books references
                booksReference = soupIdBookGoodReads.find_all("a", class_="bookTitle")
                j = 0
                while ((j < len(booksReference)) and (AUTHORfound == False)):
                    autGoodReads = booksReference[j].find_next("a", class_="authorName").text
                    
                    if (autSearchedInternal in autGoodReads.lower()):
                        AUTHORfound = True
                    j += 1    
                
                #Now we go to the selected book's page
                if (AUTHORfound == True):
                    source = urlopen('https://www.goodreads.com' + booksReference[j-1]["href"]) 
                    soup = bs4.BeautifulSoup(source, 'html.parser')
                    ISBNfound = True

        #Now we are on the specific book's web page
        #=> Common analysis begins
        if ISBNfound:
            titleSearched = soup.find("h1", id="bookTitle").text
            titleSearched = titleSearched.replace('\n', '').strip()
            
            #Search of ISBN (10 and / or 13), language and awards
            searchForISBN_Lang_Awards_Series = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")

            for i in range(len(searchForISBN_Lang_Awards_Series)):
                
                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'ISBN':
                    isbnFull = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem")
                    
                    #ISBN_10 and ISBN_13 are provided
                    if isbnFull.find("span", class_="greyText"):
                        ISBNdict["ISBN_10"] = isbnFull.text.split(isbnFull.find("span", class_="greyText").text)
                        ISBNdict["ISBN_10"] = ISBNdict["ISBN_10"][0].replace('\n', '').strip()
                        ISBNdict["ISBN_13"] = isbnFull.find("span", class_="greyText").text
                        ISBNdict["ISBN_13"] = ISBNdict["ISBN_13"].split('(ISBN13: ')[1].replace(")", '')
                    #Only ISBN_10 is provided
                    else:
                        ISBNdict["ISBN_10"] = isbnFull.text

                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Edition Language':
                    languageSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text
                    #In order to be compliant with GoogleBooks names
                    if (languageSearched == 'English'):
                        languageSearched = 'en'
            
                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Literary Awards':
                    awardsSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text
                    awardsSearched = awardsSearched.strip()

            
            #Search of published date and publisher       
            searchForPublished = soup.find("div", id="details").find_all("div", class_="row")
            for i in range(len(searchForPublished)):
                if 'Published' in searchForPublished[i].text:
                    #Current published date and additional information on first publication date is also provided
                    if (searchForPublished[i].find("nobr", class_="greyText")):
                        infoFirstPublished = searchForPublished[i].find("nobr", class_="greyText")
                        tempPublished = searchForPublished[i].text.split(infoFirstPublished.text)
                        tempPublished = tempPublished[0].strip().replace('\n', '').replace('Published', '').split('by')
                        pubData = tempPublished[0].strip()
                        pubData = re.search("[0-9]{4,4}", pubData)[0]
                        pubSearched = tempPublished[1].strip()
                    #Only current published date is provided
                    else:
                        tempPublished = searchForPublished[i].text.strip().replace('\n', '').replace('Published', '').split('by')
                        pubData = tempPublished[0].strip()
                        pubData = re.search("[0-9]{4,4}", pubData)[0]
                        pubSearched = tempPublished[1].strip()

            #Search of the pages number
            searchForPages = soup.find("div", id="details").find_all("div", class_="row")
            for i in range(len(searchForPages)):
                if 'pages' in searchForPages[i].text:
                    pagesSearched = searchForPublished[i].text
                    pagesSearched = pagesSearched.split(',')[-1].split('pages')[0].strip()
        
            #Search for the book's genre
            if (soup.find("a", class_="actionLinkLite bookPageGenreLink")):
                catSearched = soup.find_all("a", class_="actionLinkLite bookPageGenreLink")[0].text
            
            #Search for knowing if book is part of a serie
            #=> If yes, we keep the URL of the other mentionned books of the serie
            if soup.find("div", class_="seriesList"):
                if (soup.find("div", class_="seriesList").find_next("h2").text == 'Other books in the series'):
                    #We go to this specific book serie web page
                    linkTowardSeries = soup.find("div", class_="seriesList").find_next("h2").find_next("a")["href"]
                    r = requests.get('https://www.goodreads.com' + linkTowardSeries)
                    
                    #We keep all the other books reference of this serie
                    seriesList = re.findall('href="/book/show/[0-9]+', str(r.content))
                    goodreadsLinksSeriesList = [seriesList[i].replace('href="', 'https://www.goodreads.com') for i in range(len(seriesList)) if i%2 == 0]
        
            #search of the author genre: we need to finf the URL of author page first
            autSearched = soup.find("a", class_="authorName").text
            sourceAuthor = urlopen(soup.find("a", class_="authorName")["href"])
            soupAuthor = bs4.BeautifulSoup(sourceAuthor, 'html.parser')
            
            #On the author web site page, we search for the author genre
            searchForAuthorGenre = soupAuthor.find_all("div", class_="dataTitle")
            for i in range(len(searchForAuthorGenre)):
                if (searchForAuthorGenre[i].text == "Genre"):
                    authorGenreSearched = searchForAuthorGenre[i].find_next("div", class_="dataItem").text.split(',')[0]
                    authorGenreSearched = authorGenreSearched.replace('\n', '').strip()
    
        return (ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                pubData, pubSearched, catSearched, descSearched, languageSearched, '', pagesSearched, awardsSearched, \
                authorGenreSearched, goodreadsLinksSeriesList])
    
    except:
        return (False, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                pubData, pubSearched, catSearched, descSearched, languageSearched, '', pagesSearched, awardsSearched, \
                authorGenreSearched, goodreadsLinksSeriesList])    


def GoodReadsSearch(f, SaveFileName, theColumns, ind_start, ind_end):

    NotFoundBooks = 0    
    pdT = pd.DataFrame(columns = theColumns)

    for i in range(0, ind_start-1): 
        f.readline()
    
    csvLineParsed = P.ParserCsvInputBookCrossing(f.readline())
    ret, refBook = GoodReadsSearchFunction(isbn = csvLineParsed[0])
    pdT.loc[0] = refBook
    pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'w')


    #i doesn't start at 0 so that the trigger index 'len(pdT) - savingRate:len(pdT)+1' of save is correct
    for i in range(ind_start+1, ind_end):  
        
        csvLineParsed = P.ParserCsvInputBookCrossing(f.readline())
        
        ret = False
        ret, refBook = GoodReadsSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            ret, refBook = GoodReadsSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
            
        if (ret == False):
            NotFoundBooks += 1

        pdT.loc[0] = refBook
        pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)
        #Google doesn't like when too much requests are performed...
        #time.sleep(10.0)
    
    return NotFoundBooks


    
if __name__ == "__main__":
    
#Example of GoodReads Requests:
############################
    #Direct search on the GoodReads web site with title 'Jane Doe' and author name 'Kaiser'
    #=> the URL used it then: 'https://www.goodreads.com/search?utf8=%E2%9C%93&q=jane+doe+kaiser&search_type=books'

    #On the html code of the previous direct search, there are: <div id="1730953" and <div id="9675352" 
    #=> It's GoodReads book's identifiers 

    #=> Then with the following request, we are on the book web page : 'https://www.goodreads.com/book/show/1730953'
    
    #Example of book with 'Literary Awards': The Millionaire Next Door: The Surprising Secrets of America's Wealthy 
    #=> 'https://www.goodreads.com/book/show/998'

    #Example of book inside a serie: Asterix the Gaul
    #=> direct search: https://www.goodreads.com/search?utf8=%E2%9C%93&search%5Bquery%5D=asterix+the+gaulois&commit=Search&search_type=books
    #=> URL of GoodReads book's page: 'https://www.goodreads.com/book/show/71292'
    
#Search result
############################
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
    
    cheminGoodReads = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\GoodReads/'
    cheminGoodReads = cheminGoodReads.replace('\\', '/')

    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                        'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                        'Image', 'Pages', 'Awards', "Author's genre", 'Same serie']
    
    SaveFileName = cheminGoodReads + 'GoodreadsBooks_InternetSearch_14_03_2021.csv'

    #List of books to search on Google
    f = open(cheminBookCrossing + 'Extrait1000_BX-Books_et1awards.csv', encoding="utf8", errors="replace")
    f.readline()
    
    #Google search function
    NotFoubndBooks = GoodReadsSearch(f, SaveFileName, theColumns, 0, 2) 


    print("Not found books: %d" % NotFoubndBooks)
    f.close()   



