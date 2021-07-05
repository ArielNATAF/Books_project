import re

    
def ParserCsvInputBookCrossing(currentLine, Re = False):
    if Re == False:
        L = currentLine.split('"')
        
        return [L[i] for i in range(16) if i%2 == 1]

    else:
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
    
    
if __name__ == "__main__":
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')

    f = open(cheminBookCrossing + 'BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    for i in range(10):
        print(ParserCsvInputBookCrossing(f.readline()))
        print()

    f.close()
 
