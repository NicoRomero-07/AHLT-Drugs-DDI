#! /usr/bin/python3

import sys, os
from xml.dom.minidom import parse

# folder where this file is located
THISDIR=os.path.abspath(os.path.dirname(__file__))
# go two folders up and locate "util" folder there
LABDIR=os.path.dirname(os.path.dirname(THISDIR))
UTILDIR=os.path.join(LABDIR, "util")
# add "util" to search path so python can find "deptree"
sys.path.append(UTILDIR)

from deptree import *
import patterns


## ------------------- 
## -- Convert a pair of drugs and their context in a feature vector

def extract_features(tree, entities, e1, e2) :
   feats = set()

   # get head token for each gold entity
   tkE1 = tree.get_fragment_head(entities[e1]['start'],entities[e1]['end'])
   tkE2 = tree.get_fragment_head(entities[e2]['start'],entities[e2]['end'])

   if tkE1 is not None and tkE2 is not None:

      # features for tokens in between E1 and E2
      for tk in range(tkE1+1, tkE2) :
         if not tree.is_stopword(tk):
            word  = tree.get_word(tk)
            lemma = tree.get_lemma(tk).lower()
            tag = tree.get_tag(tk)
            feats.add("lib=" + lemma)
            feats.add("wib=" + word)
            feats.add("lpib=" + lemma + "_" + tag)

            # feature indicating the presence of an entity in between E1 and E2
            if tree.is_entity(tk, entities) :
               feats.add("eib")


      # features for tokens before tkE1
      for tk in range(tkE1):
         if not tree.is_stopword(tk):
            word  = tree.get_word(tk)
            lemma = tree.get_lemma(tk).lower()
            tag = tree.get_tag(tk)
            feats.add("l_before=" + lemma)
            feats.add("w_before=" + word)
            feats.add("lp_before=" + lemma + "_" + tag)

            # entity before tkE1
            if tree.is_entity(tk, entities):
               feats.add("ebf")


      # features for tokens after tkE2
      for tk in range(tkE2, tree.get_n_nodes()):
         if not tree.is_stopword(tk):
            word  = tree.get_word(tk)
            lemma = tree.get_lemma(tk).lower()
            tag = tree.get_tag(tk)
            feats.add("l_after=" + lemma)
            feats.add("w_after=" + word)
            feats.add("lp_after=" + lemma + "_" + tag)

            # entity after E2
            if tree.is_entity(tk, entities):
               feats.add("eaf")


      # features about paths in the tree
      lcs = tree.get_LCS(tkE1,tkE2)
      
      path1 = tree.get_up_path(tkE1,lcs)
      path1 = "<".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path1])
      feats.add("path1="+path1)

      path2 = tree.get_down_path(lcs,tkE2)
      path2 = ">".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path2])
      feats.add("path2="+path2)

      path = path1+"<"+tree.get_lemma(lcs)+"_"+tree.get_rel(lcs)+">"+path2      
      feats.add("path="+path)

      lemma = patterns.check_LCS_svo(tree,tkE1,tkE2)
      if lemma is not None:
         feats.add("LCS_svo="+lemma)



      # features about the LCS
      lcs = tree.get_LCS(tkE1,tkE2)

      word  = tree.get_word(lcs)
      lemma = tree.get_lemma(lcs).lower()
      tag = tree.get_tag(lcs)
      rel = tree.get_rel(lcs)
      feats.add("LCS_w=" + word)
      feats.add("LCS_l=" + lemma)
      feats.add("LCS_tag=" + tag)
      feats.add("LCS_rel=" + rel)
      feats.add("LCS_ l_t=" + lemma + "_" + tag)

      # LCS is entity
      if tree.is_entity(lcs, entities):
         feats.add("lcs_entity")
      
      # LCS is ROOT
      if lcs == "ROOT":
         feats.add("lcs_root")



      # features about parent entities
      p1 = tree.get_parent(tkE1)
      p2 = tree.get_parent(tkE2)

      # parents of the entities
      if p1 is not None:
         lemma = tree.get_lemma(p1).lower()
         tag = tree.get_tag(p1)
         feats.add("lemma_p1=" + lemma)
         feats.add("tag_p1=" + tag) 
      if p2 is not None:
         lemma = tree.get_lemma(p2).lower()
         tag = tree.get_tag(p2)
         feats.add("lemma_p2=" + lemma)
         feats.add("tag_p2=" + tag) 

      # same entities in the pair
      if tree.get_lemma(tkE1) == tree.get_lemma(tkE2):
         feats.add("same_lemma")

      # one entity under the other
      if tkE2 == tree.get_parent(tkE1):
         feats.add("e1_under_e2")
      if tkE1 == tree.get_parent(tkE2):
         feats.add("e2_under_e1")

      # same parent
      if p1 == p2 and (p1 is not None):
         tag = tree.get_tag(p1)
         feats.add("same_parent_tag=" + tag) 


      # # num of tokens in between
      # feats.add("ntokens_in_bt="+str(tkE2 - tkE1))

      # # features for tkE1
      # feats.add('tkE1_word='+tree.get_word(tkE1))
      # feats.add('tkE1_lemma='+tree.get_lemma(tkE1).lower())
      # feats.add('tkE1_tag='+tree.get_tag(tkE1))
      # feats.add('tkE1_word_lenght'+str(len(tree.get_word(tkE1))))
      # feats.add('tkE1_lemma_lenght'+str(len(tree.get_lemma(tkE1))))

      # # features for tkE2
      # feats.add('tkE2_word='+tree.get_word(tkE2))
      # feats.add('tkE2_lemma='+tree.get_lemma(tkE2).lower())
      # feats.add('tkE2_tag='+tree.get_tag(tkE2))
      # feats.add('tkE2_word_lenght'+str(len(tree.get_word(tkE2))))
      # feats.add('tkE2_lemma_lenght'+str(len(tree.get_lemma(tkE2))))



      
   return feats


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
## --

# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in os.listdir(datadir) :

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir+"/"+f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences :
        sid = s.attributes["id"].value   # get sentence id
        stext = s.attributes["text"].value   # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents :
           id = e.attributes["id"].value
           offs = e.attributes["charOffset"].value.split("-")           
           entities[id] = {'start': int(offs[0]), 'end': int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1 : continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if (ddi=="true") : dditype = p.attributes["type"].value
            else : dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction

            feats = extract_features(analysis,entities,id_e1,id_e2) 
            # resulting vector
            print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")

