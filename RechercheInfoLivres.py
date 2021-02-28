import sys
import pandas as pd
import re

chemin = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
chemin = chemin.replace('\\', '/')

sys.path.append(chemin)


def BooksSearchFunction(isbn = None, title = None, author = None):

    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
#    print("\nRecherche livre: %d" % i)
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
        if (isbn is not None):
            
            ISBNdict["ISBN_10"] = isbn

            #We have to format the ISBN so that it is written on 10 digits => {0:0>10s}
            requeteIsbnGoogle = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0:0>10s}".format(ISBNdict["ISBN_10"])
    
            try:
                repIsbnGoogle = pd.read_json(requeteIsbnGoogle)
                ISBNfound = True
            except:
                repIsbnGoogle = pd.read_json(requeteIsbnGoogle, typ = 'series')
                ISBNfound = False
            
            #ISBN has been recognized on Google Books
            if (ISBNfound == True):
                titleSearched = repIsbnGoogle['items'][0]['volumeInfo']['title']
                
                if 'subtitle' in repIsbnGoogle['items'][0]['volumeInfo']:
                    titleSearched = titleSearched + ' : ' + repIsbnGoogle['items'][0]['volumeInfo']['subtitle']
        
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
                    
                print(repIsbnGoogle['items'][0]['volumeInfo']['publishedDate'], 'publishedDate' in repIsbnGoogle['items'][0]['volumeInfo'])
                if ('publishedDate' in repIsbnGoogle['items'][0]['volumeInfo']):
                    print(repIsbnGoogle['items'][0]['volumeInfo']['publishedDate'], 'publishedDate' in repIsbnGoogle['items'][0]['volumeInfo'])
                    pubData = repIsbnGoogle['items'][0]['volumeInfo']['publishedDate']
                    print(pubData)
    
        else:
            if ((title != None) and (author != None)):

                titleSearched = title
                autSearched = author.lower()
                
                requeteTitleGoogle = "https://www.googleapis.com/books/v1/volumes?q=title:%s" % (titleSearched.replace('\'', '').replace(' ','%20'))
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


if __name__ == "__main__":

    #extraitFch = pd.read_csv(chemin + 'Extrait1000_BX-Books.csv', nrows = 32, delimiter = ';', header = 0)
    #ligne 33 pose problème à l'ouverture: encoding utf-32 marche encore moins bien que l'encoding par défaut
    
    with open(chemin + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="replace") as f:
        L = f.readlines()
    
    LLpropre = []
    
    for i in range (1, len(L)):
        L_i = L[i].split(';')
        
        if len(L_i) == 8:
            LLpropre.append(L_i)
            
        else:
            g = re.search('([0-9X]+);(.+);([0-9]{4,4})(.+)(;http.+.jpg)+(;http.+.jpg)+(;http.+.jpg)+', L[i])
    
            g_2 = g[2].split('"')
            if len(g_2) == 1:
                g_2_12 = g[2].split(';')
            else:
                g_2_12 = [g_2[i] for i in range(len(g_2)) if not (g_2[i] == '' or g_2[i] == ';')]
         
            LLpropre.append([x.strip(';') for x in [g[1], g_2_12[0], g_2_12[1], g[3], g[4], g[5], g[6], g[7]]])
    
    pdL = pd.DataFrame(LLpropre, columns = L[0].split(';'))
    taille = pdL.shape[0]

    NotFoubndBooks = 0    
    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
    pdT = pd.DataFrame(columns = theColumns)
    
       
    for i in range(0, 5):
        ret = False
        
        ret, refBook = BooksSearchFunction(isbn = pdL.iloc[i,0])
        
        if (ret == False):
            ret, refBook = BooksSearchFunction(title = pdL.iloc[i,1], author = pdL.iloc[i,2].split(';')[-1])
            
        if (ret == False):
            NotFoubndBooks += 1
        else:
            pdT.loc[len(pdT)] = refBook
    
    print("Not found books: %d" % NotFoubndBooks)
  
    
        

