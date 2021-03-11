from operator import itemgetter     # itemgetter importeras för att enkelt kunna sortera items i en dictionary efter value (andra värdet i tuplerna).
class Converter:

    def __init__(self):        
        self.word_index = {}            # Här skapas två dicts för översättning mellan strings och integers, 
        self.class_index = {}           # ...en för ord och en för ordklasser. 
        
    def convert_word(self,word):
        newindex = len(self.word_index)             # Här får orden ett indexnummer 
        self.word_index.setdefault(word,newindex)   # Översättningarna sparas i self.word_index, som är en dictionary.
        
    def convert_class(self,word_class):             # Samma sak som i metoden ovan sker, fast denna gång  med ordklasser
        newindex = len(self.class_index) 
        self.class_index.setdefault(word_class,newindex)    
    
    def get_classes(self):
        tupeltop = sorted(self.class_index.items(), key=itemgetter(1))  # Returnerar lista av tupler med paren (översättningarna), sorterad enligt ordklassernas index
        classtop = []
        for tup in tupeltop:            # De sorterade ordklasserna läggs i rätt ordning i en lista
            classtop.append(tup[0])
        return classtop                 # classtop är en lista med ordklasser, sorterade enligt sitt index i self.class_index

    def convert_sentence(self, sentence):        
        convlista = []
        split1 = sentence.split(' ')        # Jag börjar med att dela upp varje ord-och-ordklasspar för sig.
        split1.append('slut/SLUT')
        split1 = ['start/START'] + split1          # Här lägger jag till särskilda start och stop ord-och-ordklasspar i meningen
        self.convert_word('start')              
        self.convert_class('START')        # Genom att lägga till start/stop-ord och ordklasser i bestämd ordning, kommer de att får de första
        self.convert_word('slut')               #... indexnumrena i dictarna, och jag vet således att start alltid har indexnmr 0 och stop indexnmr 1 (i båda indexdictarna)
        self.convert_class('SLUT')
        for tagdword in split1:             # När start och stop finns i dictarna kan jag gå vidare med det egentliga argumentet i metoden. For-loopen arbetar par för par.
            list = tagdword.split('/')    
            self.convert_word(list[0])              # Ordet tilldelas index (om det ej redan finns i dict)
            self.convert_class(list[1])             # Ordklassen tilldelas index     (-//-)
            convword = self.word_index[list[0]]
            convclass = self.class_index[list[1]] 
            convpair = (convword,convclass)         # Index till ord och ordklass i ord-ordklassparet blir en tupel 
            convlista.append(convpair)              # Tupeln läggs till i convlista
        return convlista                   # Det som returneras är en lista av tupler bestående av nummer som representerar orden och ordklasserna i sentence

if __name__== "__main__":
    test = Converter()
    print (test.convert_sentence("fiskare/NN fiskar/VB fiskar/NN"))
    print (test.word_index)
    print (test.class_index)
    print (test.get_classes())
    
