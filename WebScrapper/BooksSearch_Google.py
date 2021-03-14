import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P
    
import pandas as pd
import time
import re


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
    langSearched = ''
    imageSearched = ''
    pageSearched = 0

    ISBNfound = False
    AUTHORfound = False
    repGoogle = ''
    
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
                repGoogle = pd.read_json(requeteIsbnGoogle)
                ISBNfound = True
            except:
                #In case where a book reference has NOT been found                
                repGoogle = pd.read_json(requeteIsbnGoogle, typ = 'series')
                ISBNfound = False
            
        
        #book is searched on internet thanks to its title and 1st author
        else:
            if ((title != None) and (author != None)):

                titleSearched = title.encode('ascii', 'ignore').decode('ascii')
                autSearched = author.encode('ascii', 'ignore').decode('ascii')
                #We keep only the author familly name
                autSearchedInternal = autSearched.lower().split()[-1]
                
                #Request format for a search on Google Book web site
                #=> We must take care of ' (replace('\'', '')) and space (replace(' ','%20'))
                requeteTitleGoogle = "https://www.googleapis.com/books/v1/volumes?q=title:%s" % (titleSearched.replace('\'', '').replace(' ','%20'))
#                print(requeteTitleGoogle)
                repGoogle = pd.read_json(requeteTitleGoogle) 
                
                #The Title has been found on Google Books
                #We only analyse the first book's reference retrieved => repTitleGoogle['items'][0]
                if (repGoogle['totalItems'][0] != 1):
    
                    if ('authors' in repGoogle['items'][0]['volumeInfo']):
                        
                        #All authors proposed by Google
                        autGoogle = repGoogle['items'][0]['volumeInfo']['authors']
                        
                        #Among all authors proposed by Google, we search correspondance with the first provided author
                        j = 0
                        while ((j < len(autGoogle)) and (AUTHORfound == False)):
                            
                            if (autSearchedInternal in autGoogle[j].lower()):
                                AUTHORfound = True  
                                ISBNfound = True
                                
                            j += 1

        #ISBN or title/author has been recognized on Google Books
        if (ISBNfound == True):
            titleSearched = repGoogle['items'][0]['volumeInfo']['title']
            
            if 'subtitle' in repGoogle['items'][0]['volumeInfo']:
                titleSearched = titleSearched + ' : ' + repGoogle['items'][0]['volumeInfo']['subtitle']
            #'industryIdentifiers' stands for ISBN_10, ISBN_13 or OtherID
            if ('industryIdentifiers' in repGoogle['items'][0]['volumeInfo']):
                
                #Among all identifiers type proposed by Google, we search "ISBN_10", "ISBN_13" or "OtherID"
                for k in range(len(repGoogle['items'][0]['volumeInfo']['industryIdentifiers'])):
                    
                    if repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_10":
                        ISBNdict["ISBN_10"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        ISBNfound = True
                        
                    elif repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_13":
                        ISBNdict["ISBN_13"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        ISBNfound = True
                        
                    else:
                        ISBNdict["OtherID"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        ISBNfound = True

            if ('authors' in repGoogle['items'][0]['volumeInfo']):
                autSearched = repGoogle['items'][0]['volumeInfo']['authors'][0]
                
            if ('publisher' in repGoogle['items'][0]['volumeInfo']):
                pubSearched = repGoogle['items'][0]['volumeInfo']['publisher']
                                    
            if ('publishedDate' in repGoogle['items'][0]['volumeInfo']):
                pubData = repGoogle['items'][0]['volumeInfo']['publishedDate']
                pubData = re.search("[0-9]{4,4}", pubData)[0]

            if ('categories' in repGoogle['items'][0]['volumeInfo']):
                catSearched = repGoogle['items'][0]['volumeInfo']['categories'][0]

            if ('searchInfo' in repGoogle['items'][0]):
                descSearched = repGoogle['items'][0]['searchInfo']['textSnippet']                    

            if ('language' in repGoogle['items'][0]['volumeInfo']):
                langSearched = repGoogle['items'][0]['volumeInfo']['language']

            if ('imageLinks' in repGoogle['items'][0]['volumeInfo']):
                imageSearched = repGoogle['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']

            if ('pageCount' in repGoogle['items'][0]['volumeInfo']):
                pageSearched = repGoogle['items'][0]['volumeInfo']['pageCount']

        return (ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                           pubData, pubSearched, catSearched, descSearched, langSearched, imageSearched, pageSearched, '', '', ''])

    except:
        return (False, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                           pubData, pubSearched, catSearched, descSearched, langSearched, imageSearched, pageSearched, '', '', ''])



def GoogleSearch(f, SaveFileName, theColumns, ind_start, ind_end):

    NotFoundBooks = 0    
    pdT = pd.DataFrame(columns = theColumns)

    for i in range(0, ind_start-1): 
        f.readline()
        
    csvLineParsed = P.ParserCsvInputBookCrossing(f.readline())
    ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
    pdT.loc[0] = refBook
    pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'w')

    #i doesn't start at 0 so that the trigger index 'len(pdT) - savingRate:len(pdT)+1' of save is correct
    for i in range(ind_start+1, ind_end):    
        csvLineParsed = P.ParserCsvInputBookCrossing(f.readline())

        ret = False
        ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            ret, refBook = GoogleSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
        
        if (ret == False):
            NotFoundBooks += 1

        pdT.loc[0] = refBook
        pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)
        #Google doesn't like when too much requests are performed...
        #time.sleep(10.0)
    
    return NotFoundBooks



    
if __name__ == "__main__":
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

    #'PLEADING GUILTY' found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0671870432
    
#Search result
############################
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
    
    cheminGoogleBooks = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\GoogleBooks/'
    cheminGoogleBooks = cheminGoogleBooks.replace('\\', '/')
    SaveFileName = cheminGoogleBooks + 'GoogleBooks_InternetSearch_14_03_2021.csv'

    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                        'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                        'Image', 'Pages', 'Awards', "Author's genre", 'Same serie']

    #List of books to search on Google
    f = open(cheminBookCrossing + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    #Google search function
    NotFoundBooks = GoogleSearch(f, SaveFileName, theColumns, 0, 15) 

    print("Not found books: %d" % NotFoundBooks)
    f.close()   
    
    
 
