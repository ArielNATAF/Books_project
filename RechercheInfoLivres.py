import sys
import pandas as pd
import re
import time

chemin = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
chemin = chemin.replace('\\', '/')

sys.path.append(chemin)

    
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



def BooksSearchFunction(isbn = None, title = None, author = None):
    ''' Find information on internet about the book entered in function's arguments 
        Either isbn = ..., Or title = ..., author = ... '''
    
    #3 kinds of books identifiers
    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
    #all is reset
    ISBNdict["ISBN_10"] = 0
    ISBNdict["ISBN_13"] = 0   
    ISBNdict["OtherID"] = 0
    autGoogle = []
    titleSearched = ''
    autSearched = ''
    pubData = ''

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
                    
#                if ('publisher' in repIsbnGoogle['items'][0]['volumeInfo']):
#                    autSearched = repIsbnGoogle['items'][0]['volumeInfo']['publisher']
                                        
                if ('publishedDate' in repIsbnGoogle['items'][0]['volumeInfo']):
                    pubData = repIsbnGoogle['items'][0]['volumeInfo']['publishedDate']
    
        #book is searched on internet thanks to its title and 1st author
        else:
            if ((title != None) and (author != None)):

                titleSearched = title
                autSearched = author.lower()
                
                #Request format for a search on Google Book web site
                #=> We must take care of ' (replace('\'', '')) and space (replace(' ','%20'))
                requeteTitleGoogle = "https://www.googleapis.com/books/v1/volumes?q=title:%s" % (titleSearched.replace('\'', '').replace(' ','%20'))
                repTitleGoogle = pd.read_json(requeteTitleGoogle) 
#                print(requeteTitleGoogle)
                
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
                                        
                            j += 1

        return ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, pubData, '', '', '', '']

    except Exception as excp:
        raise Exception("There is un problem: ", excp)




    #'PLEADING GUILTY' found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0671870432

if __name__ == "__main__":
#Example of Google Requests:
############################
    #'Classical Mythology' found with ISBN - no subtitle - ISBN found: https://www.googleapis.com/books/v1/volumes?q=isbn:0195153448
    
    #'Flu' found with ISBN - with subtitle - ISBN found:     https://www.googleapis.com/books/v1/volumes?q=isbn:0374157065
    
    #'Pride and Prejudice' NOT found with ISBN:https://www.googleapis.com/books/v1/volumes?q=isbn:055321215X
    # => found with title - Other identifier than isbn: https://www.googleapis.com/books/v1/volumes?q=title:Pride%20and%20Prejudice
    
    #'Jogn Doe' NOT found with IBBN: https://www.googleapis.com/books/v1/volumes?q=isbn:1552041778
    # => found with title : https://www.googleapis.com/books/v1/volumes?q=title:Jane%20Doe
    # => But author on Google is wrong, so book considered as NOT FOUND
    
    #'Beloved (Plume Contemporary Fiction)' NOT found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0452264464
    # => Several references found with title: https://www.googleapis.com/books/v1/volumes?q=title:Beloved%20(Plume%20Contemporary%20Fiction)
    # => But those references are not the one searched (but only the first reference is used), so book considered as NOT FOUND


#Internet serach:
#################
    #extraitFch = pd.read_csv(chemin + 'Extrait1000_BX-Books.csv', nrows = 32, delimiter = ';', header = 0)
    #ligne 33 pose problème à l'ouverture: encoding utf-32 marche encore moins bien que l'encoding par défaut
    f = open(chemin + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="ignore")
    f.readline()
    
    NotFoubndBooks = 0    
    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
    pdT = pd.DataFrame(columns = theColumns)

    csvLineParsed = ParserCsvInputBookCrossing(f.readline())
    ret, refBook = BooksSearchFunction(isbn = csvLineParsed[0])
    pdT.loc[0] = refBook
    pd.DataFrame(pdT.loc[0:1], columns = theColumns).to_csv(chemin + 'BookCrossing_InternetSearch.csv', sep = ';', index = False, mode = 'w')

    savingRate = 20   
    for i in range(1, 1000):    
        csvLineParsed = ParserCsvInputBookCrossing(f.readline())

        ret = False
        ret, refBook = BooksSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            ret, refBook = BooksSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
            
        if (ret == False):
            NotFoubndBooks += 1

        pdT.loc[len(pdT)] = refBook
        if (i % savingRate == 0) and (i != 0):
            pdT.loc[len(pdT) - savingRate:len(pdT)+1].to_csv(chemin + 'BookCrossing_InternetSearch.csv', sep = ';', index = False, mode = 'a', header = False)
            time.sleep(10.0)
    
    print("Not found books: %d" % NotFoubndBooks)
    f.close()
    
  
    
        

