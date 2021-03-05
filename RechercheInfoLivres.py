import sys
import pandas as pd
import re
import time
import requests
from urllib.request import urlopen
import bs4

cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
sys.path.append(cheminBookCrossing)

cheminGoogleBooks = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\GoogleBooks/'
cheminGoogleBooks = cheminGoogleBooks.replace('\\', '/')
sys.path.append(cheminGoogleBooks)

cheminGoodReads = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\GoodReads/'
cheminGoodReads = cheminGoodReads.replace('\\', '/')
sys.path.append(cheminGoodReads)
    
def ParserCsvInputBookCrossing(currentLine):

    L = currentLine.split(';')
    
    if len(L) == 8:
        return L
        
    else:
        g = re.search('([0-9X]+);(.+);([0-9]{4,4})(.+)(;http.+.jpg)+(;http.+.jpg)+(;http.+.jpg)+', currentLine)

        g_2 = g[2].split('"')
        if len(g_2) == 1:
            g_2_12 = g[2].split(';')
        else:
            g_2_12 = [g_2[i] for i in range(len(g_2)) if not (g_2[i] == '' or g_2[i] == ';')]
     
        return [x.strip(';') for x in [g[1], g_2_12[0], g_2_12[1], g[3], g[4], g[5], g[6], g[7]]]



def GoogleSearchFunction(isbn = None, title = None, author = None):
    ''' Find information on internet about the book entered in function's arguments 
        Either isbn = ..., Or title = ..., author = ... '''
    
    #3 kinds of books identifiers
    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
    #all is reset
    ISBNdict["ISBN_10"] = 0.0
    ISBNdict["ISBN_13"] = 0.0   
    ISBNdict["OtherID"] = 0.0
    autGoogle = []
    titleSearched = ''
    autSearched = ''
    pubSearched = ''
    pubData = ''
    catSearched = ''
    descSearched = ''

    ISBNfound = False
    AUTHORfound = False
    repTitleGoogle = ''
    repIsbnGoogle = ''
    
    try:
        #book is searched on internet thanks to its ISBN_10 identifier
        if (isbn is not None):
            
            ISBNdict["ISBN_10"] = isbn

            #Request format for a search on Google Book web site
            #=> We have to format the ISBN so that it is written on 10 digits => {0:0>10s}
            requeteIsbnGoogle = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0:0>10s}".format(ISBNdict["ISBN_10"])
#            print('\n\n', requeteIsbnGoogle)
    
            try:
                #In case where a book reference has been found
                repIsbnGoogle = pd.read_json(requeteIsbnGoogle)
                ISBNfound = True
            except:
                #In case where a book reference has NOT been found                
                repIsbnGoogle = pd.read_json(requeteIsbnGoogle, typ = 'series')
                ISBNfound = False
            
            #ISBN has been recognized on Google Books
            if (ISBNfound == True):
                titleSearched = repIsbnGoogle['items'][0]['volumeInfo']['title']
                
                if 'subtitle' in repIsbnGoogle['items'][0]['volumeInfo']:
                    titleSearched = titleSearched + ' : ' + repIsbnGoogle['items'][0]['volumeInfo']['subtitle']
        
                #'industryIdentifiers' stands for ISBN_10, ISBN_13 or OtherID
                if ('industryIdentifiers' in repIsbnGoogle['items'][0]['volumeInfo']):
                    
                    #Among all identifiers type proposed by Google, we search "ISBN_10", "ISBN_13" or "OtherID"
                    for k in range(len(repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'])):
                        
                        if repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_10":
                            assert (repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier'] == str(ISBNdict["ISBN_10"]).zfill(10))
                            
                        elif repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_13":
                            ISBNdict["ISBN_13"] = repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                            
                        else:
                            ISBNdict["OtherID"] = repIsbnGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                    
                    
                if ('authors' in repIsbnGoogle['items'][0]['volumeInfo']):
                    autSearched = repIsbnGoogle['items'][0]['volumeInfo']['authors'][0]
                    
                if ('publisher' in repIsbnGoogle['items'][0]['volumeInfo']):
                    pubSearched = repIsbnGoogle['items'][0]['volumeInfo']['publisher']
                                        
                if ('publishedDate' in repIsbnGoogle['items'][0]['volumeInfo']):
                    pubData = repIsbnGoogle['items'][0]['volumeInfo']['publishedDate']

                if ('categories' in repIsbnGoogle['items'][0]['volumeInfo']):
                    catSearched = repIsbnGoogle['items'][0]['volumeInfo']['categories'][0]

                descSearched = repIsbnGoogle['items'][0]['searchInfo']['textSnippet']                    
        
        #book is searched on internet thanks to its title and 1st author
        else:
            if ((title != None) and (author != None)):

                titleSearched = title.encode('ascii', 'ignore').decode('ascii')
                autSearched = author.encode('ascii', 'ignore').decode('ascii').lower()
                
                #Request format for a search on Google Book web site
                #=> We must take care of ' (replace('\'', '')) and space (replace(' ','%20'))
                requeteTitleGoogle = "https://www.googleapis.com/books/v1/volumes?q=title:%s" % (titleSearched.replace('\'', '').replace(' ','%20'))
#                print(requeteTitleGoogle)
                repTitleGoogle = pd.read_json(requeteTitleGoogle) 
                
                #The Title has been found on Google Books
                #We only analyse the first book's reference retrieved => repTitleGoogle['items'][0]
                if (repTitleGoogle['totalItems'][0] != 1):
    
                    if ('authors' in repTitleGoogle['items'][0]['volumeInfo']):
                        
                        #All authors proposed by Google
                        autGoogle = repTitleGoogle['items'][0]['volumeInfo']['authors']
                        
                        #Among all authors proposed by Google, we search correspondance with the first provided author
                        j = 0
                        while ((j < len(autGoogle)) and (AUTHORfound == False)):
                            
                            if (autSearched == autGoogle[j].lower()):
                                AUTHORfound = True    
                                
                                #'industryIdentifiers' stands for ISBN_10, ISBN_13 or OtherID
                                if ('industryIdentifiers' in repTitleGoogle['items'][0]['volumeInfo']):
                                    ISBNfound = True
                                    
                                    #Among all identifiers type proposed by Google, we search "ISBN_10", "ISBN_13" or "OtherID"
                                    for k in range(len(repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'])):
                                        
                                        if repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_10":
                                            ISBNdict["ISBN_10"] = repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                                            
                                        elif repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_13":
                                            ISBNdict["ISBN_13"] = repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                                            
                                        else:
                                            ISBNdict["OtherID"] = repTitleGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                                    
                                    if ('publishedDate' in repTitleGoogle['items'][0]['volumeInfo']):
                                        pubData = repTitleGoogle['items'][0]['volumeInfo']['publishedDate']
                                                            
                                    if ('publisher' in repIsbnGoogle['items'][0]['volumeInfo']):
                                        pubSearched = repIsbnGoogle['items'][0]['volumeInfo']['publisher']
                                        
                                    if ('categories' in repIsbnGoogle['items'][0]['volumeInfo']):
                                        catSearched = repIsbnGoogle['items'][0]['volumeInfo']['categories'][0]
                                    
                                    descSearched = repIsbnGoogle['items'][0]['searchInfo']['textSnippet']
                                        
                            j += 1

        return ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, pubData, pubSearched, catSearched, descSearched]

    except Exception as excp:
        raise Exception("There is un problem: ", excp)




    #'PLEADING GUILTY' found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0671870432

def GoogleSearch():
#Example of Google Requests:
############################
    #'Classical Mythology' found with ISBN - no subtitle - ISBN found: https://www.googleapis.com/books/v1/volumes?q=isbn:0195153448
    
    #'Flu' found with ISBN - with subtitle - ISBN found: https://www.googleapis.com/books/v1/volumes?q=isbn:0374157065
    
    #'Pride and Prejudice' NOT found with ISBN:https://www.googleapis.com/books/v1/volumes?q=isbn:055321215X
    # => found with title - Other identifier than isbn: https://www.googleapis.com/books/v1/volumes?q=title:Pride%20and%20Prejudice
    
    #'Jogn Doe' NOT found with IBBN: https://www.googleapis.com/books/v1/volumes?q=isbn:1552041778
    # => found with title : https://www.googleapis.com/books/v1/volumes?q=title:Jane%20Doe
    # => But author on Google is wrong, so book considered as NOT FOUND
    
    #'Beloved (Plume Contemporary Fiction)' NOT found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0452264464
    # => Several references found with title: https://www.googleapis.com/books/v1/volumes?q=title:Beloved%20(Plume%20Contemporary%20Fiction)
    # => But those references are not the one searched (but only the first reference is used), so book considered as NOT FOUND

    #Problem with unknown characters, for example 'title = Die Mars- Chroniken. Roman in Erz?¤hlungen' triggers exception 
    #Exception: ('There is un problem: ', UnicodeEncodeError('ascii', 'GET /books/v1/volumes?q=title:Die%20Mars-%20Chroniken.%20Roman%20in%20Erz?¤hlungen. HTTP/1.1', 74, 75, 'ordinal not in range(128)'))
    #=> The solutyion is title.encode('ascii', 'ignore').decode('ascii') = Die Mars- Chroniken. Roman in Erz?hlungen


#Internet search:
#################
    #extraitFch = pd.read_csv(chemin + 'Extrait1000_BX-Books.csv', nrows = 32, delimiter = ';', header = 0)
    #ligne 33 pose problème à l'ouverture: encoding utf-32 marche encore moins bien que l'encoding par défaut
    
    SaveFileName = 'GoggleBooks_InternetSearch_05_03_2021.csv'
    
    f = open(cheminBookCrossing + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    NotFoubndBooks = 0    
    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Category', 'Description']
    pdT = pd.DataFrame(columns = theColumns)

    csvLineParsed = ParserCsvInputBookCrossing(f.readline())
    ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
    pdT.loc[0] = refBook
    pd.DataFrame(pdT.loc[0:1], columns = theColumns).to_csv(cheminGoogleBooks + SaveFileName, sep = ';', index = False, mode = 'w')

#    for i in range(1, 175): 
#        f.readline()
        
    savingRate = 5   
    for i in range(1, 10):    
        csvLineParsed = ParserCsvInputBookCrossing(f.readline())

        ret = False
        ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            ret, refBook = GoogleSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
            
        if (ret == False):
            NotFoubndBooks += 1

        pdT.loc[len(pdT)] = refBook
        if (i % savingRate == 0) and (i != 0):
            pdT.loc[len(pdT) - savingRate:len(pdT)+1].to_csv(cheminGoogleBooks + SaveFileName, sep = ';', index = False, mode = 'a', header = False)
            time.sleep(10.0)
    
    print("Not found books: %d" % NotFoubndBooks)
    f.close()


def GoodReadsSearchFunction():
#Example of Google Requests:
############################
    #recherche avec le titre 'Jane Doe' et le nom de l'auteur 'Kaiser'
#    r = requests.get('https://www.goodreads.com/search?utf8=%E2%9C%93&q=jane+doe+kaiser&search_type=books')
#    print(r.content, type(r))
#    with open('D:/DocsDeCara/Boulot/IA_ML/DSTI/Programme/ML_with_Python/Projet/Donnees/GoodReads/urlRecupereee.txt', "wb") as f:				#il faut ouvrir au format binaire
#        f.write(r.content)

    #Dedans il y a <div id="1730953" et <div id="9675352" qui indique les identifiants Good Reads pour ces livres
    #=> il y a 2 autres <div id="... mais ce ne sont pas des chiffres qui suivents derrière
    
    #Ensuite si on fait : 'https://www.goodreads.com/book/show/1730953', on va sur la page du livre
    
    #Jane Doe: 'https://www.goodreads.com/book/show/1730953'
#    source = urlopen('https://www.goodreads.com/book/show/1730953') 
    
    #Book with 'Literary Awards': The Millionaire Next Door: The Surprising Secrets of America's Wealthy 
#    source = urlopen('https://www.goodreads.com/book/show/998') 

#Internet search:
############################
    #Books in Series: Asterix The Gaulois
    source = urlopen('https://www.goodreads.com/book/show/71292') 
    
#    r = requests.get('https://www.goodreads.com/book/show/71292')
#    with open(cheminGoodReads + 'Asterix_PageLivreRecupereee.txt', "wb") as f:				#il faut ouvrir au format binaire
#        f.write(r.content)    
    
    soup = bs4.BeautifulSoup(source, 'html.parser')
    print(soup.find("h1", id="bookTitle").text)
    
    print(soup.find("a", class_="authorName").find("span", itemprop="name").text)
#    r = requests.get(soup.find("a", class_="authorName")["href"])
#    with open(cheminGoodReads + 'authorAsterix_PageRecupereee.txt', "wb") as f:				#il faut ouvrir au format binaire
#        f.write(r.content)    
    sourceAuthor = urlopen(soup.find("a", class_="authorName")["href"])
    soupAuthor = bs4.BeautifulSoup(sourceAuthor, 'html.parser')
    
    searchForAuthorGenre = soupAuthor.find_all("div", class_="dataTitle")
    for i in range(len(searchForAuthorGenre)):
        if (searchForAuthorGenre[i].text == "Genre"):
            print(searchForAuthorGenre[i].find_next("div", class_="dataItem").text.split(',')[0])
    
    searchForISBN_Lang_Awards_Serires = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")
    for i in range(len(searchForISBN_Lang_Awards_Serires)):

        if searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowTitle").text == 'ISBN':
            isbnFull = searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowItem")
            
            if isbnFull.find("span", class_="greyText"):
                print(isbnFull.text.split(isbnFull.find("span", class_="greyText").text))
                print(isbnFull.find("span", class_="greyText").text)
    
        if searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowTitle").text == 'Edition Language':
            print(searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowItem").text)
    
        if searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowTitle").text == 'Literary Awards':
            print(searchForISBN_Lang_Awards_Serires[i].find("div", "infoBoxRowItem").text)
            
           
    searchForPublished = soup.find("div", id="details").find_all("div", class_="row")
    for i in range(len(searchForPublished)):
        if 'Published' in searchForPublished[i].text:
            
            if (searchForPublished[i].find("nobr", class_="greyText")):
                infoFirstPublished = searchForPublished[i].find("nobr", class_="greyText")
                tempPublished = searchForPublished[i].text.split(infoFirstPublished.text)
                print(tempPublished[0].strip().replace('\n', '').replace('Published', '').split('by'))
            else:
                print(searchForPublished[i].text.strip().replace('\n', '').replace('Published', '').split('by'))

    searchForPages = soup.find("div", id="details").find_all("div", class_="row")
    for i in range(len(searchForPages)):
        if 'pages' in searchForPages[i].text:
            print(searchForPublished[i].text)

    print(soup.find_all("a", class_="actionLinkLite bookPageGenreLink")[0].text)
    
    if soup.find("div", class_="seriesList").find_next("h2").text == 'Other books in the series':
        linkTowardSeries = soup.find("div", class_="seriesList").find_next("h2").find_next("a")["href"]
        
        r = requests.get('https://www.goodreads.com' + linkTowardSeries)
        seriesList = re.findall('href="/book/show/[0-9]+', str(r.content))
        linksSeriesList = [seriesList[i].replace('href="', 'https://www.goodreads.com') for i in range(len(seriesList)) if i%2 == 0]
        print(linksSeriesList, len(linksSeriesList))
    
    
    
if __name__ == "__main__":
    GoogleSearch()    
    GoodReadsSearchFunction()


 
