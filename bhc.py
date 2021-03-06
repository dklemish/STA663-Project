import math
import numpy as np
import operator as op
import scipy as sc
from sets import Set
from string import punctuation

class clusterNode:
    def __init__(self,log_beta_fac,left=None,right=None,ID=None,x=None,n=1,ld=0,beta=1,logpi=1,r=0,ll=None,log_const=None):
        self.left  = left  # pointer down to left node
        self.right = right # pointer down to right node
        self.ID    = ID    # node ID
        self.x     = x     # total counts of each word across all points in cluster
        self.n     = n     # number of data points in node
        self.ld    = ld    # log d
        self.logpi = logpi # prior probability of merging
        self.r     = r     # posterior probability of merging
        
        # Normalizing constant
        if log_const is None:
            self.log_const = [math.lgamma(sum(x)+1) - sum([math.lgamma(elem+1) for elem in self.x])]
        else:
            self.log_const = log_const

        # Marginal log-likelihood
        if ll is None:
            self.ll = (log_beta_fac + sum(self.log_const) + 
                       sum([math.lgamma(beta+x[j]) for j in range(0,len(self.x))]) - 
                       math.lgamma(sum(self.x)+len(self.x)*beta))
        
    def __str__(self):
        return "ID=%s\nx=%s\nn=%s\nld=%s\nlogpi=%s\nll=%s\nr=%s" % (self.ID, self.x, self.n, self.ld, self.logpi, self.ll, self.r)

		
def merge_nodes(c1, c2, alp, log_beta_fac, r, new_ID):
    ### Merges nodes together and combines data appropriately
    x_k = c1.x + c2.x  # New word counts = sum of word counts
    n_k = c1.n + c2.n  # New observations = sum of observations
    
    # Note: log(a+b) = log(a) + log(1+exp(log(b)-log(a))) if a > b
    temp1 = math.log(alp) + math.lgamma(n_k) 
    temp2 = c1.ld + c2.ld
    
    t1 = max(temp1, temp2)
    t2 = min(temp1, temp2)
    
    ld_k    = t1 + math.log(1 + math.exp(t2-t1))
    logpi_k = temp1 - ld_k
    
    log_const_k = c1.log_const + c2.log_const
    
    return clusterNode(log_beta_fac=log_beta_fac,
                       left=c1, 
                       right=c2, 
                       ID=new_ID, 
                       x=x_k, 
                       n=n_k,
                       r=r,
                       ld=ld_k,
                       logpi=logpi_k,
                       log_const = log_const_k)

					   
def calc_probability(c1, c2, alp, log_beta_fac):
    ### Calculates the r_k from Heller, the probability that clusters 
    ### c1 and c2 should be merged together, given hyperparameters 
    ### alpha and beta
    temp_node = merge_nodes(c1, c2, alp, log_beta_fac, r=0, new_ID=-1)
    logpi_k = temp_node.logpi
    logll   = temp_node.ll
    
    temp1 = logpi_k + logll
    temp2 = math.log(1-math.exp(logpi_k)) + c1.ll + c2.ll
        
    t1 = max(temp1, temp2)
    t2 = min(temp1, temp2)    
    
    return math.exp(temp1 - t1 - math.log(1 + math.exp(t2-t1)))


def create_word_matrix(docs):
    # Define stop words to remove from documents, since these words have little lexographic 
    # information.  This list is taken from Python's NLTK english stopwords.
    stopWords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
                 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 
                 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
                 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
                 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
                 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
                 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 
                 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 
                 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
                 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']
    
    # Create list of words
    # First split possessive ("Bill's) into separate 's' for later removal with stopWords
    # Then update set of words for each word in consecutive document
    words = Set()
    [words.update(new_doc) for doc in docs for new_doc in [str(doc.split("'")).translate(None,punctuation).lower().split()]]

    # Remove stop words from set of words found in all documents
    [words.discard(w) for w in stopWords]
    
    # Create array where each row contains the count of 
    # each unique word from all documents
    words = sorted(list(words))
    return (words, 
            np.array([[item.count(w) for w in words] for doc in docs for item in [str(doc.split("'")).translate(None,punctuation).lower().split()]]))

			
def BHCmultinomial(texts, alpha, beta):
    possible_merge = {}
    R = {}
    currentclustid = -1
    
    # Convert text data into "bag of words" n x p matrix with n documents 
    # and p different words contained in all documents
    
    words, word_data = create_word_matrix(texts)

    # Calculate factor that is a function of the beta prior
    p = len(words)
    lBetaFac = math.lgamma(sum(beta*np.ones(p))) - sum([math.lgamma(beta) for i in np.arange(p)])
    
    # clusters are initially just the individual rows
    clust = [clusterNode(log_beta_fac = lBetaFac, 
                         log_const = None,
                         ID = i, 
                         x = word_data[i],
                         beta = beta,
                         ld = math.log(alpha)) for i in range(len(word_data))]
    
    while len(clust)>1:
        closest = float("-inf")

        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                # R is the cache of probability calculations
                if (clust[i].ID,clust[j].ID) not in possible_merge: 
                    R[(clust[i].ID,clust[j].ID)] = calc_probability(c1 = clust[i], 
                                                                    c2 = clust[j], 
                                                                    alp = alpha,
                                                                    log_beta_fac = lBetaFac)
                    
                r_k = R[(clust[i].ID,clust[j].ID)]

                if r_k > closest:
                    closest = r_k
                    lowestpair = (i,j)

        # create the new cluster
        newcluster = merge_nodes(clust[lowestpair[0]], clust[lowestpair[1]],
                                 alp=alpha, log_beta_fac=lBetaFac, r = closest,
                                 new_ID = currentclustid)

        # cluster ids that weren't in the original set are negative
        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)

    return clust[0]
	
# Code adapted from "Programming Collective Intelligence" by Toby Segaran (O'Reilly Media 2007)

from PIL import Image,ImageDraw

def getheight(clust):
    if clust.left == None and clust.right == None:
        return 1
    else:
        return getheight(clust.left) + getheight(clust.right)
    
def getdepth(clust):
    if clust.left == None and clust.right == None:
        return 0
    else:
        return max(getdepth(clust.left),getdepth(clust.right)) + 1
    

def draw_dendrogram(clust,cutoff,jpeg='clusters.png'):
    # height and width
    h = getheight(clust)*50
    #w = getdepth(clust)*300
    #w=1200
    w = h
    depth=getdepth(clust)

    #print h, w, depth
    
    # width is fixed, so scale distances accordingly
    #scaling=float(w-150)/depth
    scaling = 5

    # Create a new image with a white background
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)

    if clust.r < cutoff:
        col = (255,0,0)
    else:
        col = (0,0,0)
    
    draw.line((0,h/2,10,h/2),fill=col)    

    # Draw the first node
    draw_node(draw,clust,cutoff,10,(h/2),scaling,img)
    img.save(jpeg)

def draw_node(draw,clust,cutoff,x,y,scaling,img):
    if clust.ID<0:
        h1=getheight(clust.left)*50
        h2=getheight(clust.right)*50
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        # Line length
        #ll=clust.distance*scaling
        ll=10*scaling
        
        #print clust.r
        if(clust.r < cutoff):
            col=(255,0,0)
        else:
            col=(0,0,0)
        
        # Vertical line from this cluster to children    
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=col)   

        # Horizontal line to left item
        draw.line((x,top+h1/2,x+ll,top+h1/2),fill=col)    

        # Horizontal line to right item
        draw.line((x,bottom-h2/2,x+ll,bottom-h2/2),fill=col)

        # Call the function to draw the left and right nodes    
        draw_node(draw,clust.left,cutoff,x+ll,top+h1/2,scaling,img)
        draw_node(draw,clust.right,cutoff,x+ll,bottom-h2/2,scaling,img)
    else:   
        # If this is an endpoint, write the cluster ID onto the image
        draw.text((x+5,y-5),str(clust.ID),fill=(0,0,0))
