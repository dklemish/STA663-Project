import bhc
import math
import numpy as np
from nose.tools import *

texts = ["Cat cat dog", "Dog dog bird", "Bird bird this"]
text_words, data = bhc.create_word_matrix(texts)

def test_words():
    ''' Test extraction of words from documents is correct '''
    assert text_words == ["bird", "cat", "dog"]

def test_data():
    ''' Test creation of word counts is correct '''
    assert (data == [[0,2,1],[1,0,2],[2,0,0]]).all()

p = len(text_words)
beta = 1.00
log_beta_factor = math.lgamma(sum(beta*np.ones(p))) - sum([math.lgamma(beta) for i in np.arange(p)])
node1 = bhc.clusterNode(log_beta_fac=log_beta_factor, log_const=None, ID=1, x=data[0], beta=1.0, ld=0)
node2 = bhc.clusterNode(log_beta_fac=log_beta_factor, log_const=None, ID=2, x=data[1], beta=1.0, ld=0)
node3 = bhc.clusterNode(log_beta_fac=log_beta_factor, log_const=None, ID=3, x=data[2], beta=1.0, ld=0)

testnode = bhc.merge_nodes(node2, node3, alp=1, log_beta_fac=log_beta_factor, r=0, new_ID=-1)

def test_create_node_data():
    ''' Test creation of a leaf node based upon given data '''
    assert (node1.x == [0,2,1]).all()
    assert node1.n == 1
    assert node1.ID == 1

def test_create_node_loglik():
    ''' Test the marginal log-likelihood calculation of the data given hyperparameters beta '''
    assert round(node1.ll,4) == -2.3026

def test_calc_prob():
    ''' Test the calculation of the probability of merging two nodes together is correct '''
    assert round(bhc.calc_probability(node2, node3, alp=1, log_beta_fac = log_beta_factor),6) == 0.461538

def test_merge_node():
    ''' Test merging of nodes is correct '''
    assert (testnode.x == [3,0,2]).all()
    assert testnode.n == 2
    assert round(testnode.ll,9) == -4.248495242

bhc_tree = bhc.BHCmultinomial(texts, 1, 1)

def test_final_result():
    ''' Test top of tree has all data'''
    assert bhc_tree.n == 3
    assert (bhc_tree.x == [3,2,3]).all()
