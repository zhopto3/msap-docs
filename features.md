# Morpho-Syntactic Features

quick links: [feature inventory](https://github.com/omagolda/msud-docs/blob/pages-source/inventory.md)

The morpho-syntactic features are the one of the key characteristics of morpho-syntactic
dependency trees. They are modelled after the morphological features in UD and may be
viewed as a generalization of them. [Like in UD]( https://universaldependencies.org/u/overview/morphology.html),
the features are an unordered set of name and value pairs separated by pipes, of the
structure `Name1=Value1|Name2=Value2`. Most feature names and values are equivalent to
those in UD, for example `Gender=Masc`, `Voice=Pass`, etc. But there are also a couple
of new feature type, see below for details.

However, morpho-syntactic features also differ from morphological features in a couple
important characteristics:
* The features are defined not only by morphemes but by any _grammatical_ function marker,
be it a morpheme or a word. So the content node _go_ in _will go_ should bear the feature
`Tense=Fut`.
  * All applicable features should be marked on the respective content nodes, even if
  expressed by non-concatenative means. E.g., the node _go_ in _did you go?_ should be
  marked with `Mood=Int` even though it is expressed mostly by word order.
* Features should be applied only to their relevant node. In other words, no agreement
features are needed, and in a phrase like _he goes_ only _he_ should bear
`Person=3|Number=Sing`, and _goes_ should have only `Tense=Pres` (and other features if
relevant).
* The feature structure is not flat. In other words, features are not necessarily single 
strings. They can contain:
  * a list of values, for example `Aspect=Perf,Prog` on the verb of the English clause
  _I have been walking_,
  * a negation of a value, for example `Mood=not(Pot)` on the Turkish verb _yürüyemez_
  (“he can’t walk”) where the negation refers to the ability,[^1]
  * a conjunction of values, for example `RelType=and(Cond,Temp)` that is the
  manifestation of the English phrase _if and when_ when connecting two clauses,
  * and a disjunction of values, `Tense=or(Past,Fut)`.

[^1] This is in contrast with the verb _yürümebilir_ (literally “he is able to not walk”,
i.e., he may not walk), where the negation pertains to the verb itself and should be
tagged as `Mood=Pot|Polarity=Neg`.
