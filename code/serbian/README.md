### 

As part of the directions in the msap-docs, it says that we should find the corresponding functional units for all the cases in `../../inventory.md` (i.e., add a column for Serbian). 

I added the list of cases and their corresponding functional units in Serbian to the file `./rel.json`. When I couldn't find a Serbian preposition/functional word for a case, I encoded the case as "NONE" (I see there are empty entries for other languages in the inventory.md table so I think that's fine). 

*IMPORTANT*: The rel.json may need another look from you in case there are functional words I missed or misunderstood; if you update it, also re-run the python script `compile_relations.py`, because this will change a file that is needed for the script `./serbian.py`.

In `../english/english.py`, there is a small dictionary of determiners and their features. In the Serbian data, there were so many determiners that I decided it would be a bit more organized if I saved this list as a json (`./determiners.json`). The features are all based on the features as they appear in the Serbian UD data. 

* `./serbian.py`: 

    * A heavvily edited version of the script ../english/english.py

    * Takes an arg ('train' 'dev' or 'test') and applies rules that create "ms features" column in that split of the Serbian UD data

    * output data gets saved to ../../data/serbian/ (there are already outputs for Serbian UD data there, but in case you run it again that's where they end up).

    * From what I understand, in the final column there should be:

        * a "_" if the unit is functional

        * a "|" if the unit is a content unit but it has no children

        * a list of the content word's morphological features and all of it's functional childrens "relation types" (from rel.json) or features 

    * Things that might need another look from a native speaker in serbian.py:

        *  lines 167-172: There are a lot of "discourse particles" that I really wasn't sure what to do with. It seemed like some of their meanings were context dependent. For now I just throw them out, but it's possible they should add to the MS feats of their parent nodes somehow—I'm really not sure. If they change the mood or meaning somehow of the parent node, it may be relevant to encode how (for an example, in the lines 174-176, I change the tense of the sentence if 'hteti' is being used as a modal verb.) Just change feats[FEAT_NAME] and discard the word from aux_lemmas

        * Right now I think I'm only accounting for nagation if it's with "ne" (line 187). Maybe there are other ways I don't know about that could be accounted for their too. 

        * I would also check some examples in the test set where there's an abstract node (from the dropped subject) and see if the new MS features that are there make sense based on the examples they give from Basque in the main readme.


