from operator import itemgetter
from converter import *
import numpy as np
class HMM:

    def normalize(self):
        sanno_a = []        # arrays till normaliserade matrisen
        sanno_b = []
        for line in self.a:     # Jag normaliserar matriserna rad för rad
            sannolikrad = []        # Detta kommer att vara raden med sannolikhetsfördelning
            totalt = sum(line)
            for integ in line:       # Här går jag igenom varje integer i raden
                if integ == 0. and totalt == 0.: 
                    sanno = 0.
                else:
                    sanno = integ/totalt        # Här räknar jag ut sannolikheten för varje ordklassföljd i raden
                sannolikrad.append(sanno)      # Nu har jag en array av sannolikheter som motsvarar "line"
            sanno_a.append(sannolikrad)  # Rad-arrayn läggs sist i listan sanno_a, som är en lista av alla arrays som ska bilda normaliserade self.a
        for line in self.b:
            sannolikrad = [] 
            totalt = sum(line)                      
            for integ in line:
                if integ == 0. and totalt == 0.:
                    sanno = 0.
                else:
                    sanno = integ/totalt
                sannolikrad.append(sanno)
            sanno_b.append(sannolikrad)
        self.b = np.array(sanno_b)        # Här skapar jag nya self.a och self.b-matriser på den normaliserade datan
        self.a = np.array(sanno_a)
            
    def initialize(self,corpus):
        # I nedanstående rad gör jag en gememsam lista av de listor som finns i corpus, för att enkelt kunna hitta de största värdena.
        hittastorst = [tup for list in corpus for tup in list]     # Hjälp från: https://coderwall.com/p/rcmaea/flatten-a-list-of-lists-in-one-line-in-python
        sortw = sorted(hittastorst, key=itemgetter(0))[-1:][0][0]+1     # Föregående rad: För varje lista i corpus lägger jag till varje tupel från denna i sortw  
        sortc = sorted(hittastorst, key=itemgetter(1))[-1:][0][1]+1 # Här tar jag fram det största värdet för klasser, och i föregående samma sak fast för ord
        self.a = np.zeros( (sortc,sortc) )
        self.b = np.zeros( (sortc,sortw) )  
           
        for lista in corpus: 
            men_num = list(enumerate(lista)) # men_num är en lista med numrerade tupler(ordconv,klassconv) [(0,(1,3)),(1,(3,5))...]
            lastone = men_num[-1:][0][0]       # Eftersom den sista tupeln inte har en efterföljande tupel behöver jag avbryta for-loopen i tid, därför behövs denna variabel
            i = 0                                
            for pair in men_num:    
                ett_c = pair[1][1] 
                if i <= lastone -1:                 # Så länge loopen inte är på det sista tupelparet i listan ska self.a uppdateras
                    tva_c = men_num[i+1][1][1]          
                    self.a[ett_c,tva_c] += 1            #self.a uppdateras på detta sätt: a-rader(x): nuvarande klass. a-kulumner(y): följande klass
                    i += 1          # Index används för att kunna jämföra nuvarande pair med "lastone"
                else:
                    break
            i2 = 0    
            for pair in men_num:                # I denna for-loop uppdateras self.b på liknande sätt, men nu behöver jag inte ta hänsyn
                ord = pair[1][0]                # ... till sista tupeln då self.b endast behöver information om varje tupel för sig
                klass = pair[1][1]
                self.b[klass,ord] += 1 
                i2 += 1
        self.normalize()            # Här normaliserar jag self.a och self.b
                                 
    def viterbi(self,sentence): 
        viterbi_m = np.zeros( (len(sentence),len(self.b)) )      
        backp_m = np.zeros( (len(sentence),len(self.b)),dtype=int)  # För att inte få problem senare ser jag till att back_m består av integers. Detta med hjälp av dtype=int
        viterbi_m[0,0] = 1               
        ro_i = 0                       # Detta är index för rad (alltså ord)
        for row in viterbi_m:  
            if ro_i == 0:               # Första raden vet vi är 0:or (förutom [0,0] som ju är 1). Därför hoppar jag över den raden 
                ro_i += 1
                continue
            else:             
                rut_i = 0           # Index för varje ruta i row
                for ruta in row:           
                    if rut_i == 0:   
                        rut_i += 1      # Första rutan vet vi är 0, därför hoppar vi över den rutan
                        continue
                    else:        
                        valjmellan = []         # Lista med eventuella sannolikheter för rutan
                        prp_i = 0   
                        for prevprob in viterbi_m[ro_i-1]:  # Denna forloop ser till alla möjliga ordklasser för föregående ord. Alltså: ruta i föregående rad har variabeln prevprob
                            evbp =  prevprob * self.a[prp_i,rut_i] * self.b[rut_i,sentence[ro_i]]   # Här multipliceras prevprob (ruta i föregående rad) med sannolikheten för ordklassföljden (hämtat från self.a) samt med sannolikheten för ord och ordklass-kombinationen (hämtat från self.b)
                            valjmellan.append(evbp)  # Denna sannolikhet läggs på listan valjmellan.
                            prp_i += 1
                        vinnare = max(valjmellan)    # Nu väljer jag ut det största sannolikhetsvärdet 
                        valarr = np.asarray(valjmellan)
                        vinnindex = valarr.argmax()            # Här hittar jag index för den högst sannolika tidigare ordklassen
                        viterbi_m[ro_i,rut_i] = vinnare        # Det mest sannolika värdet läggs in i nuvarande ruta i viterbi-matrisen
                        backp_m[ro_i,rut_i] = vinnindex        # Det mest sannolika värdets index läggs in i nuvarande ruta i backpointer-matrisen
                        rut_i += 1
                ro_i += 1
        bestpath = [] 
        backw_i = len(backp_m)        # Eftersom jag kommer att gå igenom backp_m nedifrån behöver jag vet längden på matrisen
        bestpath.append(1)              # Eftersom jag vet att den sista taggen i alla meningar är STOP(1) är 1 given som första steg i bestpath. 
        for row in backp_m:               
            if backw_i == 1:          # När den for-loopen kommit till den sista raden, är det dags att avsluta loopen, då det inte finns fler rader att backa till
                break
            else:
                before = bestpath[-1:]      # Before är alltså rutan på den tidigare raden (alltså längre ner i backp_m) som pekar till vilken ruta vi ska till i raden efter.
                before = before[0]
                now = backp_m[backw_i-1,before]     # Nästa "pointer" är hittad
                bestpath.append(now)                # Pointern läggs till i listan bestpath, som är en lista på de mest sannolika ordklasserna för meningen, bakifrån.
                backw_i -= 1
        bestpathright = []
        for num in reversed(bestpath):              # Här vänder jag på bestpath så att de sannolika ordklasserna presenteras åt rätt håll
            bestpathright.append(num)               
        print (backp_m)    
        print (bestpath)
        print (bestpathright)
        return (bestpathright)                      # Ut kommer de mest sannolika ordklasserna (i indexform)
         
                
if __name__== "__main__":
    test = Converter()
    sentences = ["hon/PN fiskar/VB lax/NN","hjälper/VB hon/PN henne/PN","fiskare/NN fiskar/VB fiskar/NN","hon/PN diskar/VB hon/NN"]
    conv_sentences = [test.convert_sentence(sentence) for sentence in sentences]
    print    (test.word_index)
    print   (test.class_index)
    
    print (conv_sentences)
    print ('get:',test.get_classes)
    hmm1 = HMM()
    hmm1.initialize(conv_sentences)
    print ('npar_a,2:',np.around(hmm1.a, 2))
    print ('npar_b,2:',np.around(hmm1.b, 2))
    hmm1.viterbi([0,3,4,1])
    overs = hmm1.viterbi([0,3,4,1])
    output = []
    for numb in overs:
        for tag, number in test.class_index.items():
            if number == numb:
                output.append(tag)
            else:
                continue
    origwords = []
    for numb in overs:
        for word, number in test.word_index.items():
            if number == numb:
                origwords.append(word)
            else:
                continue
    
    class_strings = test.get_classes()
    for original, sentence in zip(sentences, conv_sentences):
        print (original)
        print ('s',sentence)
        words = [word for word,word_class in sentence]
        print (words)           
        print ('vit:',hmm1.viterbi(words))
        classes = [class_strings[word_class] for word_class in hmm1.viterbi(words)]
        print ('Orginalmening:', original)
        print ('Ordklasser enligt modellen:', classes)
        print ()
