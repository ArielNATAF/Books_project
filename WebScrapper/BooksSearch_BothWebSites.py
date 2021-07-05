import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P
import BooksSearch_GoodReads as GR
import BooksSearch_Google as G
    
import pandas as pd
import requests
from urllib.request import urlopen
import bs4
import re
import warnings

def GoodReadsPartialSearchFunction(isbn =  None):
    
    awardsSearched = ''
    authorGenreSearched = ''
    goodreadsLinksSeriesList = []
    avgRating = ""

    ISBNfound = False
    
    try:
        urlIdBookGoodReads_start = "https://www.goodreads.com/search?q={0:0>10s}".format(isbn)
        urlIdBookGoodReads_end = '&qid='
        bookUrlForSearch = urlIdBookGoodReads_start + urlIdBookGoodReads_end
#            print(bookUrlForSearch)
        
        source = urlopen(bookUrlForSearch)
        soup = bs4.BeautifulSoup(source, 'html.parser')
        ISBNfound = (soup.find("h1", id="bookTitle") != None)


        #Now we are on the specific book's web page
        if ISBNfound:
            if soup.find("span", itemprop="ratingValue"):
                avgRating = soup.find("span", itemprop="ratingValue").text.strip()

            searchForISBN_Lang_Awards_Series = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")
            for i in range(len(searchForISBN_Lang_Awards_Series)):
                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Literary Awards':
                    awardsSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text.strip()

                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Edition Language':
                    languageSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text
                    #In order to be compliant with GoogleBooks names
                    if (languageSearched == 'English'):
                        languageSearched = 'en'
    
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
            sourceAuthor = urlopen(soup.find("a", class_="authorName")["href"])
            soupAuthor = bs4.BeautifulSoup(sourceAuthor, 'html.parser')
            
            #On the author web site page, we search for the author genre
            searchForAuthorGenre = soupAuthor.find_all("div", class_="dataTitle")
            for i in range(len(searchForAuthorGenre)):
                if (searchForAuthorGenre[i].text == "Genre"):
                    authorGenreSearched = searchForAuthorGenre[i].find_next("div", class_="dataItem").text.split(',')[0]
                    authorGenreSearched = authorGenreSearched.replace('\n', '').strip()
    
    
        return (ISBNfound, [awardsSearched, authorGenreSearched, goodreadsLinksSeriesList, avgRating])
    
    except:
        return (False, [awardsSearched, authorGenreSearched, goodreadsLinksSeriesList, avgRating])    
    


def internetSearch(f, SaveFileName, theColumns, ind_start, ind_end, Re = False):

    NotFoundBooks_ind = 0   
    NotFoundBooks_bool = True
    
    pdT = pd.DataFrame(columns = theColumns)

    for i in range(0, ind_start-1): 
        f.readline()
        
    csvLineParsed = P.ParserCsvInputBookCrossing(f.readline(), Re)
    ret, refBookGoogle = G.GoogleSearchFunction(isbn = csvLineParsed[0])
    pdT.loc[0] = refBookGoogle 
    #print(pdT.loc[0].ISBN_13, type(pdT.loc[0].ISBN_13))
    pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'w')
    
    #it doesn't start at 0 so that the trigger index 'len(pdT) - savingRate:len(pdT)+1' of save is correct
    for i in range(ind_start+1, ind_end):    
        retGoogle = False
        retGoodReads = False
        retPartial = False

        lili = f.readline()
        #print(lili)
        csvLineParsed = P.ParserCsvInputBookCrossing(lili, Re)
        #print(csvLineParsed)
        
        #First we use Google Books web site: search fastest
        retGoogle, refBookGoogle = G.GoogleSearchFunction(isbn = csvLineParsed[0])
        
        if (retGoogle == False):

            #if ISBN not found on Google Books, we try on Google Reads
            retGoodReads, refBookGoodReads = GR.GoodReadsSearchFunction(isbn = csvLineParsed[0])
            
            if (retGoodReads == False):
                #if ISBN not found (on Google Books and on Good Reads), 
                #we try search on GoodReads only a search with title and author 
                retGoodReads, refBookGoodReads = GR.GoodReadsSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
                if (retGoodReads == True):
                    refBook = refBookGoodReads
                    NotFoundBooks_bool = False
                else:
                    NotFoundBooks_ind += 1
            else:
                refBook = refBookGoodReads
                NotFoundBooks_bool = False
                
        else:
            refBook = refBookGoogle
            NotFoundBooks_bool = False
            
            #If ISBN found on Google Books, we complete some columns with GoodReads search
            retPartial, refBookPartial = GoodReadsPartialSearchFunction(isbn = csvLineParsed[0])
            if (retPartial == True):
                refBook[-4:] = refBookPartial

        if NotFoundBooks_bool != True:
            pdT.loc[0] = refBook
            pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)
            NotFoundBooks_bool = True

        
    return NotFoundBooks_ind



    
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.warn("Let this be your last warning")
        warnings.simplefilter("ignore")
        
        cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees\GoodBooks\goodbooks-10k-master\goodbooks-10k-master/'
        cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
    
        cheminCommon = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees/'
        cheminCommon = cheminCommon.replace('\\', '/')
        SaveFileName = cheminCommon + 'bothWebSites_InternetSearch_25_01_2021.csv'
        
        theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                            'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                            'Image', 'Pages', 'Awards', "Author's genre", 'Same serie', 'average_rating']
    
        #List of books to search on Google
        f = open(cheminBookCrossing + 'books.csv', encoding="utf8", errors="replace")
        f.readline()
        
        #Google search function
        NotFoundBooks = internetSearch(f, SaveFileName, theColumns, 0, 10, Re = True) 
    
        print("Not found books: %d" % NotFoundBooks)
        f.close()   
    
    
 
