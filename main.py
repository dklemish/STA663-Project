import bhc

import matplotlib
matplotlib.use('Agg') # To avoid graphical output in a non-Ipython environment

import scipy
import scipy.cluster.hierarchy as hier

texts = [open('Data/Text1.txt','r').read().replace('\r\n',''),
         open('Data/Text2.txt','r').read().replace('\r\n',''),
         open('Data/Text3.txt','r').read().replace('\r\n',''),
         open('Data/Text4.txt','r').read().replace('\r\n',''),
         open('Data/Text5.txt','r').read().replace('\r\n',''),
         open('Data/Text6.txt','r').read().replace('\r\n',''),
         open('Data/Text7.txt','r').read().replace('\r\n',''),
         open('Data/Text8.txt','r').read().replace('\r\n',''),
         open('Data/Text9.txt','r').read().replace('\r\n',''),
         open('Data/Text10.txt','r').read().replace('\r\n',''),
         open('Data/Text11.txt','r').read().replace('\r\n',''),
         open('Data/Text12.txt','r').read().replace('\r\n',''),
         open('Data/Text13.txt','r').read().replace('\r\n',''),
         open('Data/Text14.txt','r').read().replace('\r\n',''),
         open('Data/Text15.txt','r').read().replace('\r\n','')]
#         open('Data/Text16.txt','r').read().replace('\r\n','')]

#results = bhc.BHCmultinomial(texts, 1, 1)

#bhc.draw_dendrogram(results, cutoff=0.5)


## Run standard hierarchical clustering to compare
text_words, data = bhc.create_word_matrix(texts)

Y = hier.linkage(data)
Z = hier.dendrogram(Y)

matplotlib.pylab.savefig("scipy_cluster.png", format="png")

