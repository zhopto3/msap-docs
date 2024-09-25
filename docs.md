# Morphosyntax Parsing Shared Task Data Annotation Guidelines

## Introduction

### Motivation

Words have long been an essential concept in the definition of treebanks in Universal Dependencies (UD), since the first stage in their construction is delimiting words in the language at hand. This is done due to the common view in theoretical linguistics of words as the dividing line between syntax, the grammatical module of word combination, and morphology, that is word construction.

However, delimiting syntactically relevant words gets exponentially more complicated the less isolating languages are. Thus, this operation, which is as simple as breaking the text on white spaces for English, is borderline impossible for polysynthetic languages, in which a single word may be composed of several lexemes that have predicate-argument relations. This reflects the fact that despite the presumed role of words in contemporary linguistics, there is no consensus on a coherent cross-lingual definition of words.

We suggest defining the content-function boundary to differentiate 'morphological' from 'syntactic' elements. In our morpho-syntactic data structure, content words are represented as separate nodes on a dependency graph, even if they share a whitespace-separated word, and both function words and morphemes contribute morphology-style features to characterize the nodes.

We will thus avoid (most) theoretical debates on word boundaries, and solve much of the word segmentation inconsistencies that occur in UD, either across languages, e.g., Japanese is treated as isolating and Korean as agglutinative,  although they are very similar typologically, or across treebanks of the same language, e.g., the different treebanks for Hebrew segment and attribute different surface forms for clitics.
Morpho-syntactic data will be more inclusive towards languages that are currently treated unnaturally, most prominently noun-incorporating languages. Morpho-syntactic models will be able to parse sentences in more languages and enable better cross-lingual studies.

We are amending the CoNLL-U files to include MS-features for content words. These features will be annotated mostly automatically from current morphological features and function words. 
Including all nodes will result in a regular dependency graph, while ignoring all nodes without MS-features will result in a morpho-syntactic tree for this task.

### Principles

#### Independence of Word Boundary

#### Content-Function Divide

#### Crosslingual Parallelism

#### Minimal Deviation from CoNLL-U

## Schema Description

### Content Nodes (Syntax)

#### Non-morphosyntactic Features

#### Abstract Nodes

#### Gaps

### Function Features (Morphology)

#### Feature Structure

no agreement features - discuss

conjunction, disjunction and negation of features

#### List of Features and Values

## Annotation Guidelines

### Conversion from UD

#### General

- create a new column
- decide what your content words and your function words are (by UPOS)
- go through your function words and classify them according to UPOS, relation, and maybe lemma
- for each of these categories, figure out the morphosyntactic feature and place it on the head content word

#### English Rules

parataxis, reparandum and punct relations are left alone
fixed relation: combined to a temporary lemma to look for in the relevant map in 'eng_relations.py'.

Nominal lemmas: NOUN, PROPN, PRON, NUM
Verbal lemmas: VERB

keep existing features for all except VERB (Tense may be wrong)
get features from all the children
aux-children: all AUX and PART  that are not "'s"

Mood: Default Ind, or Int if an aux-child comes before a subj-child and (any child is a "?" or annotator decides), or Cnd if annotator decides
Polarity: default Pos, Neg if "not" child
VerbForm: default Fin, except if "to" as aux-child
if there is only one "do"-child, copy the tense to the verb
if there is a "be"-child:
    if there is one "be"-child of a verb:
        if the head verb is VerbForm Ger, or VerbForm Part and Tense Pres, set Aspect to Prog
        if the head verb is VerbForm Part and Tense Past, set Voice to Pass
    if there are two "be"-children, set Aspect to Prog, and if it's a verb, set Voice to Pass
    otherwise Voice Active
    if there are no auxiliaries left, copy the remaining TAM feats from the "higher" auxiliary
    if aux are not only be and not, and the VerbForm is not inf:
        the higher be, if there were two, is the first one that does not end in -ing
        copy Tense from higher be if exists
        if the head is not a verb, copy Mood and VerbForm from higher be if exists

if there is a "get"-child, set Voice to Pass, and if aux lemmas do not contain anything other than get and not, copy Tense and VerbForm from the "get"-child

if there is a "have"-child
    if the head is not a verb or the head has VerbForm Part and Tense Past: add Perf to Aspect
    if there are no auxiliaries left, copy the remaining feats from the have

if there is a "will"-child, set Tense to Fut

if there is a "would"-child, let the annotator decide:
    Mood Conditional (conditional)
    Tense Past and add Prosp to Aspect (future in the past)

Modality
    can --> Pot
    could --> Pot, plus annotator decision between adding Cnd to Mood, or setting Tense to Past
    may or might --> Prms
    shall or should --> Des
    must --> Nec
    not --> set the previous modality to neg(modality), and delete the Polarity
concatenate all modalities

get features from relations. relevant are all children with case, mark, or cc, or where the lemma is in marker_feat_map, or in case_feat_map. Remove all children that are PART, unless they're "'s"

for nominals,
    RelType are looked up in the feature map, for any child nodes with a mark relation, or that appear in the feature map
    Case are looked up in the feature map, for any child nodes with a case relation, or that appear in the feature map
for verbs, 
    all child nodes are looked up in the marker feature map, and as a backup in the case feature map

for verbs,
    copy existing features if they have not been set
    set Voice to Act if not otherwise set
    if a finite Verb has no nsubj child, create an abstract nsubj. All UD slots will be empty except for deprel and head. Take the Number and Person and Gender from somewhere
for nominals and adjectives and adverbs:
    assign features for the determiner, if any
        a: Definite Ind
        the: Definite Def
        another: Definite Ind
        no: Definite Ind and Polaritz Neg
        this: Dem Prox
        that: Dem Dist
    for adjectives and averbs,
        if 'more' child, set Degree to Cmp
        if 'most' child, set Degree to Sup
