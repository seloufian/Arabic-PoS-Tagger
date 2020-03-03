# Arabic PoS Tagger

> An implementation of a morphosyntactic tagger for the Arabic language based on a dedicated corpus, going through various steps of NLP, such as: tokenization, stemming, normalization and PoS-Tagging (using the Viterbi algorithm). The result is presented in a graphical interface offering various functionalities.

## General info

Project realized in **January 2020** as a university practical work, field: Artificial Intelligence (AI), level: Master 2. The goal was to deepen knowledge on the steps by which passes the morphosyntactic tagging in general: tokenization, stemming, normalization and PoS-tagging, and that, by implementing the different algorithms (in particular that of "Viterbi") from scratch. In addition, an emphasis was placed on the complexity of the treatment of the Arabic language (ambiguity, the concept of "diacritics", etc.).

## Project content

```text
.
├── screenShots                              <- Contains GUI illustrations
│
├── examples                                 <- Contains simulation data to fully test the application
│
├── src                                      <- Contains the application source-code (algorithms and GUI)
│   ├── files                                <- Contains some files needed for the application
│   ├── include                              <- Contains the application core
│   │   ├── morph_analyzer                   <- Contains the Buckwalter Stemmer (2002 version)
│   │   ├── posTagGeneration                 <- Contains the definition of the PoS-Tagging window
│   │   │   ├── importQuran.py               <- Window for importing verses from the Koran
│   │   │   ├── importURL.py                 <- Window for importing the source-code of a web page
│   │   │   ├── posTagGenerationTab.py       <- General PoS-Tagging window
│   │   │   ├── posTaggingTab.py             <- Window of the result of a morphosyntactic analysis
│   │   │   └── textVisualizationTab.py      <- Display window of the entered text (for PoS-Tagging)
│   │   ├── adminInterface.py                <- Administrator manager window (adding/removing a corpus)
│   │   ├── functions.py                     <- Application back-end (implementation of NLP algorithms)
│   │   ├── mainWindow.py                    <- Main window (which groups all the functionalities)
│   │   ├── modifyPosTag.py                  <- Window for modifying a PoS-Tag for a given word (stem)
│   │   ├── posTagInsertionTab.py            <- Window for inserting a tagged text into a corpus
│   │   └── posTagModificationTab.py         <- PoS-Tags modification window for a text (in a corpus)
│   ├── model                                <- Contains the database used by the application
│   │   ├── corpus                           <- Contains the list of corpora (in XML format)
│   │   ├── lexique                          <- Contains updates to PoSLexicon
│   │   ├── POS_LEXICON_2005                 <- Contains the initial PoSLexicon (without any modification)
│   │   ├── results                          <- Contains the results of the morphosyntactic analysis of a given text
│   │   └── sources                          <- Contains the model (in binary format) used by the different algorithms
│   └── __main__.py                          <- Application entry point (the main file to execute)
│
└── README.md                                <- Current project info
```

## Technologies

- **Python** (Used version: *3.7.4*), with some external packages:
  - [nltk](https://pypi.org/project/nltk/) (Used version: *3.4.5*).
  - [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) (Used version: *4.8.0*).
  - [urllib](https://pypi.org/project/urllib3/) (Used version: *1.24.2*).
  - [PyQt5](https://pypi.org/project/PyQt5/) (Used version: *5.13.1*).

## How it works

A brief review of the main aspects of the developed application (back-end and front-end sides) will be presented. However, the exact understanding of the different concepts will require other sources of information (see the [License](#License) section).

### POSLexicon update

The *POSLexicon* is one of the most important files, it defines the Part of Speech annotations (PoS-Tags) which a word (stem) can take. The work done consists of updating it, from an old version (dating from 2005), by adding new tags (retrieved from a recent corpus, named *"TALAA-PoS Annotated Corpus"*, which contains correctly PoS-tagged texts [checked manually]) to the corresponding stems.

### Morphosyntactic analysis

- **Tokenization**: Division of a text into distinct units, called *"tokens"*, going through two steps:
  - *Transformation of a text into sentences*: By using the function ``sent_tokenize`` of ``nltk`` (used for English, but also effective for Arabic).
  - *Transformation of a sentence into tokens*: By removing the non-Arabic letters, separating the punctuation of the words and extracting of tokens (division by the *"space"* caracter).

- **Stemming**: Decomposition of a stem into unit parts (radicals and its affixes), called *"stems"*, by using the ``Buckwalter Stemmer`` (version 2002) implemented under Python (with some modifications). In addition, this step include the removal of diacritics.

- **Normalization**: Replacement of non-existent stems in PoSLexicon with the keyword *"unk"* (unknown).

- **Generating a model**: Definition of the necessary elements to perform the PoS-tagging.
  - *Transition probabilities*: Conditional probabilities of tags successions (bigrams and trigrams).
  - *State observation probabilities*: Conditional probability of a word (stem) knowing a succession of annotations (bigrams [word, tag, tag] or trigrams [word, tag, word, tag, tag]).
  - *Viterbi's algorithm*: Exploitation of the previous probabilities to calculate the best sequence of PoS-tags which corresponds to a sequence of tokens.

### GUI functionalities

A detailed review of all features of the developed application with explanations will be presented. Below, the application's home window.

<p align="center">
    <img width="50%" src="screenShots/1 - Home (PoS-Tag Insertion).png" title="Home (PoS-Tag Insertion)" alt="Home (PoS-Tag Insertion)">
</p>

#### Admin interface

It allows adding or deleting a corpus (use in manual mode), it is done as follows:

- *Adding a new corpus*: The administrator is invited to select a corpus in *XML format* (which respects the syntax of existing corpora). Once the corpus is selected and the <kbd>Add new corpus</kbd> button clicked, the corpus is added (after confirmation) in the model used by the system: the XML file is copied in ``./src/model/corpus/`` (with adding its name in the binary file ``corpusNames.pkl``), a dictionary (binary file) is generated in ``./src/model/sources/`` and the learning step is restarted again.

- *Deleting of an existing corpus*: Inverse task, select the corpus to delete and click on <kbd>Delete corpus</kbd>.

<p align="center">
    <img width="35%" src="screenShots/2.1 - Add new corpus (Admin interface).png" title="Add new corpus (Admin interface)" alt="Add new corpus (Admin interface)">
    <img width="35%" src="screenShots/2.2 - Delete corpus (Admin interface).png" title="Delete corpus (Admin interface)" alt="Delete corpus (Admin interface)">
</p>

#### Insertion of an annotated sentence

Direct insertion of an annotated sentence into a corpus is possible (use in manual mode). For that, the user can optionally select the plain text (import *[in TXT format]* or manual entry) and must select the annotated text (in ***word/tag*** form). Thus, the sentence will be added to the end of the selected corpus and the learning step is restarted again. The illustration for the ["home page"](#GUI-functionalities) represents this section.

#### Modification of the PoS-tags of a sentence

<p align="center">
    <img width="50%" src="screenShots/3.1 - Select sentence (PoS-Tag Modification).png" title="Select sentence (PoS-Tag Modification)" alt="Select sentence (PoS-Tag Modification)">
</p>

Editing annotations of a specific sentence in a given corpus is possible. For that, the user must select the corpus and the sentence number, and click on <kbd>Import sentence</kbd> to display the sentence as ***Word/tag***. The modification is done by selecting (passing by the cursor) a tag, the button <kbd>Modify tag</kbd> is displayed. Once this last is clicked, the change of the current tag is possible via the appeared window. To finish the modification, the <kbd>Submit modifications</kbd> button must be clicked: the sentence will be modified, and the learning step will be repeated.

<p align="center">
    <img src="screenShots/3.2 - Select tag (PoS-Tag Modification).png" title="Select tag (PoS-Tag Modification)" alt="Select tag (PoS-Tag Modification)">
</p>

<p align="center">
    <img width="20%" src="screenShots/3.3 - Modify tag (PoS-Tag Modification).png" title="Modify tag (PoS-Tag Modification)" alt="Modify tag (PoS-Tag Modification)">
</p>

#### Generation of PoS-Tags

The most interesting part concerns the annotation of an input text. This functionality has two steps: importing a text and its annotation, details below.

##### Input text and its functionalities

<p align="center">
    <img width="50%" src="screenShots/4.1 - Text Visualization (PoS-Tag Generation).png" title="Text Visualization (PoS-Tag Generation)" alt="Text Visualization (PoS-Tag Generation)">
</p>

To start, a source text must be entered, this can be done in four different ways:

- Enter a manual text.
- Import source-code of a web page.
- Import of a text file.
- Import of verses from the Koran.

Once the text is entered, statistics are calculated and displayed in the interface. In addition, the search option of a word/expression is activated, just enter text in the corresponding zone to activate the button. Text annotation is done by clicking on the <kbd>Start PoS-Tagging</kbd> button.

##### Annotated text and its functionalities

Once the text is annotated, the corresponding tab is activated. As for the entry of the text, statistics are displayed and the search for a stem is possible. In addition, resulting text files are generated in ``./src/Model/results/``. The user can modify the generated annotations (use in automatic mode) in the same way as for the functionality ["modification of PoS-Tags of a sentence"](#Modification-of-the-PoS-tags-of-a-sentence). So, the click on the button <kbd>Submit modifications</kbd> will add this sentence (in the last position) in the selected corpus and the learning step is restarted again.

<p align="center">
    <img width="50%" src="screenShots/4.2 - PoS Tagging (PoS-Tag Generation).png" title="PoS Tagging (PoS-Tag Generation)" alt="PoS Tagging (PoS-Tag Generation)">
</p>

## Application use

To run this application, make sure that all required packages are already installed. Then, it can be launched via the entry point:

```text
$ python3 src/__main__.py
```

To test all functionalities of this application, example files are available in ``./examples/``.

## License

This application uses other projects made by third parties. This project is distributed under the ``MIT`` license. For more details, see the [``LICENSE.md``](https://github.com/seloufian/Arabic-PoS-Tagger/blob/master/LICENSE.md) file.
