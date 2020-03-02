# -*- coding: utf-8 -*-
import pickle, re, timeit
import unicodedata as ud

from nltk import trigrams, bigrams, FreqDist, sent_tokenize

from include.morph_analyzer import Analyzer, buckwalter


def talaa_pos_xml2talaa_pos_dic_phrase(annotated_corpus_path, annotated_corpus_name, path):
    """

    Parameters
    ----------
    annotated_corpus_path : str
        the full path of the annotated corpus (in xml format).
        e.g. "/home/user/corpus/".
    annotated_corpus_name : str
        the name of the corpus.
        e.g. copus1 (without the extension).
    path : str
        the path where to save the resulted dictionnary ("talaa_pos_dic_phrase"+annotated_corpus_name).

    Returns
    -------
    create a dictionnary ("talaa_pos_dic_phrase"+annotated_corpus_name) that contains {phrase_number : [Text, Tokenisation, POS_Tag, Nb_Mot, Nb_Token]},    and saved in the specified path.
    """
    phrases = re.findall(r"<Phrase.+?</Phrase_\d+>", open(annotated_corpus_path+annotated_corpus_name+".xml", encoding = "utf-8").read(), re.DOTALL)
    d = {}
    for phrase in phrases:
        try:
            phrase = re.sub(r"\n|\ufeff", "", phrase)
            Num_phrase = int(re.findall(r"<Num_phrase>(.*)</Num_phrase>", phrase)[0])
            Text = re.findall(r"<Text>(.+)</Text>", phrase)[0]
            Tokenisation = re.findall(r"<Tokenisation>(.*)</Tokenisation>", phrase)[0].split()
            POS_Tag = re.findall(r"<POS_Tag>(.*)</POS_Tag>", phrase)[0].split()
            Nb_Mot = int(re.findall(r"<Nb_Mot>(.*)</Nb_Mot>", phrase)[0])
            Nb_Token = int(re.findall(r"<Nb_Token>(.*)</Nb_Token>", phrase)[0])

            d[Num_phrase] = [Text, Tokenisation, POS_Tag, Nb_Mot, Nb_Token]
        except:
#            print("il y a une erreur dans la phrase :\n", phrase)
            continue

    save_obj(d, "talaa_pos_dic_phrase_"+annotated_corpus_name, path)

#********************************************************
def pos_lexicon_file2dict_morphem_setOfTags(pos_lexicon_file_path, path = None):
    """

    Parameters
    ----------
    pos_lexicon_file_path : str
        the full path where POSLexicon file (.txt) exist.
        e.g. /home/user/corpus/POSLexicon.txt .
    path : str, optional
        the path where to save the generated dictionnary "pos_lexicon".
        The default is None.

    Returns
    -------
    create a "pos_lexicon" dictionnary that contains {morpheme : {tag1,tag2,..}}.

    """
    f = open(pos_lexicon_file_path, encoding = "windows-1256")
    d = {}
    for line in f:
        line = line.split()
        if len(line) > 1:
            d[line[0]] = set(line[1:])

    if path:
        save_obj(d, "pos_lexicon", path)
    else:
        save_obj(d, "pos_lexicon", pos_lexicon_file_path)

#********************************************************
def update_pos_lexicon(path_sources, annotated_corpus_name, path__updates__, percent_phrases = 100, path = None):
    """

    Parameters
    ----------
    path_sources : str
        specify where pos_lexicon and talaa_pos_dic_phrase dictionnaries exist.
    annotated_corpus_name : str
        the name of the corpus.
        e.g., copus1 .
    path__updates__ : str
        the path where to save the updates made to pos_lexicon.
    pecent_phrases : float
        specify the percentage of sentences concerned by updating the pos_lexicon.
        by default all sentences will be used to update the pos_lexicon, else the percentage specified will be used.
    path : str
        specify the path where to save the dictionnary resulted, by default its the same as path_sources
    Returns
    -------
    create a dictionary with the name updated_pos_lexicon and save it in the same path as pos_lexicon.
    That dictionnary contains the content of the POSLexicon dictionnary + any new entry (new morpheme and new tag)

    """
    pos_lexicon = load_obj("pos_lexicon", path_sources)
    talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)

    limit = len(talaa_pos_dic_phrase) * percent_phrases/100

    #
    updates = ""

    phrase = 0
    while phrase < limit:
        count_morpheme = 0

        while count_morpheme < len(talaa_pos_dic_phrase[phrase][1]):
            #print(count_morpheme)
            morpheme = talaa_pos_dic_phrase[phrase][1][count_morpheme]
            tag = talaa_pos_dic_phrase[phrase][2][count_morpheme + 1]
            try:
                # add a new tag to an exist morpheme
                pos_lexicon[morpheme].add(tag)
                # +
                updates += "\najout de " + tag + " à " + morpheme
            except:
                # create a new entry in the pos_lexicon dictionnary : morpheme : {tag}
                pos_lexicon[morpheme] = {tag}
                # +
                updates += "\najout d'un nouveau morpheme ( " + morpheme + " ) avec le tag : " + tag

            count_morpheme += 1
        phrase += 1


    if path:
        save_obj(pos_lexicon, "updated_pos_lexicon", path)
    else:
        save_obj(pos_lexicon, "updated_pos_lexicon", path_sources)

    # =
    with open(path__updates__ + "lesMajApportAvecLeCorpus_"+ annotated_corpus_name +".txt", "w", encoding = "utf-8") as file:
        file.seek(0)
        file.truncate()
        file.write(updates)
        file.close()

#********************************************************
def transition_prob(annotated_corpus_names, path_sources, path = None, learning_percentage = 100):
    """

    Parameters
    ----------
    annotated_corpus_names : list
        the list of all annotated corpus names used to generate model.
    path_sources : str
        specify where "talaa_pos_dic_phrase_.." dictionnaries exist.
    path : str
        specify where to save the resulted dictionnary.

    Returns
    -------
    create a dictionary with the name transition_prob_dict in the specified path.
    That dictionnary contains P(tg2|tg0 tg1) P(tg2|tg1)
    """
    tr_tg = []
    bi_tg = []
    un_tg = []
    for name in annotated_corpus_names:
        talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_n_"+name, path_sources)

        limit = len(talaa_pos_dic_phrase) * learning_percentage/100
        phrase = 0
        while phrase < limit:
            tr_tg += trigrams(talaa_pos_dic_phrase[phrase][2])
            bi_tg += bigrams(talaa_pos_dic_phrase[phrase][2])
            un_tg += talaa_pos_dic_phrase[phrase][2]

            phrase += 1

    fd_tags = FreqDist(tr_tg + bi_tg + un_tg)

    transition_prob_dict = {}
    for (tg1,tg2,tg3) in tr_tg:
        transition_prob_dict[(tg3,(tg1,tg2))] = fd_tags[(tg1,tg2,tg3)]/fd_tags[(tg1,tg2)] # tg3|tg1 tg2
    for (tg1,tg2) in bi_tg:
        transition_prob_dict[(tg2,tg1)] = fd_tags[(tg1,tg2)]/fd_tags[tg1] # tg2|tg1

    if path:
        save_obj(transition_prob_dict, "transition_prob_dict", path)
    else:
        save_obj(transition_prob_dict, "transition_prob_dict", path_sources)

#********************************************************
def state_observation_prob(annotated_corpus_names, path_sources, path = None, learning_percentage = 100):
    """

    Parameters
    ----------
    annotated_corpus_names : list
        the list of all annotated corpus names used to generate model
    path_sources : str
        specify where "talaa_pos_dic_phrase_n_..." dictionnar(y|ies) exist(s).
    path : str
        specify where to save the resulted dictionnary.

    Returns
    -------
    create a dictionnary with the name state_observation_dict in the specified path (if not specified then it will be saved in the same path as talaa_pos...).
    That dictionnary contains P(w2|w0 tg0 w1 tg1 tg2) P(w2|w1 tg1 tg2) P(w2|tg2)

    """
    tr_c = [] # w1t1 w2t2 w3t3
    tr_n = [] # w1t1 w2t2 t3

    bi_c = [] # w1t1 w2t2
    bi_n = [] # w1t1 t2

    un_c = [] # w1t1
    un_n = [] # t1
    for name in annotated_corpus_names:
        talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_n_"+name, path_sources)

        limit = len(talaa_pos_dic_phrase) * learning_percentage/100
        phrase = 0
        while phrase < limit:
            tr_to = list(trigrams([""] + talaa_pos_dic_phrase[phrase][1]))
            bi_to = list(bigrams([""] + talaa_pos_dic_phrase[phrase][1]))
            un_to = talaa_pos_dic_phrase[phrase][1]

            tr_tg = list(trigrams(talaa_pos_dic_phrase[phrase][2]))
            bi_tg = list(bigrams(talaa_pos_dic_phrase[phrase][2]))
            un_tg = talaa_pos_dic_phrase[phrase][2][1:]

            i = 0
            while i < len(tr_to):
                tr_c.append((tr_to[i][0], tr_tg[i][0], tr_to[i][1], tr_tg[i][1], tr_to[i][2], tr_tg[i][2]))
                tr_n.append((tr_to[i][0], tr_tg[i][0], tr_to[i][1], tr_tg[i][1], tr_tg[i][2]))
                i += 1
            i = 0
            while i < len(bi_to):
                bi_c.append((bi_to[i][0], bi_tg[i][0], bi_to[i][1], bi_tg[i][1]))
                bi_n.append((bi_to[i][0], bi_tg[i][0], bi_tg[i][1]))
                i += 1
            i = 0
            while i < len(un_to):
                un_c.append((un_to[i], un_tg[i]))
                un_n.append(un_tg[i])
                i += 1

            phrase += 1

    fd_state_observation_tr_c = FreqDist(tr_c)
    fd_state_observation_tr_n = FreqDist(tr_n)

    fd_state_observation_bi_c = FreqDist(bi_c)
    fd_state_observation_bi_n = FreqDist(bi_n)

    fd_state_observation_un_c = FreqDist(un_c)
    fd_state_observation_un_n = FreqDist(un_n)

    state_observation_tr = []
    for w1,t1,w2,t2,w3,t3 in fd_state_observation_tr_c.keys():
        state_observation_tr.append(((w3,(w1,t1,w2,t2,t3)),fd_state_observation_tr_c[(w1,t1,w2,t2,w3,t3)]/fd_state_observation_tr_n[(w1,t1,w2,t2,t3)]))

    state_observation_bi = []
    for w1,t1,w2,t2 in fd_state_observation_bi_c.keys():
        state_observation_bi.append(((w2,(w1,t1,t2)),fd_state_observation_bi_c[(w1,t1,w2,t2)]/fd_state_observation_bi_n[(w1,t1,t2)]))

    state_observation_un = []
    for w1,t1 in fd_state_observation_un_c.keys():
        state_observation_un.append(((w1,t1),fd_state_observation_un_c[(w1,t1)]/fd_state_observation_un_n[t1]))

    state_observation_dict = dict(state_observation_tr + state_observation_bi + state_observation_un)

    if path:
        save_obj(state_observation_dict, "state_observation_dict", path)
    else:
        save_obj(state_observation_dict, "state_observation_dict", path_sources)


#********************************************************
def viterbi(phrase, path_sources, return_list_of_tuples__token_tag = False):
    """

    Parameters
    ----------
    phrase : list
        list of tokens.
    path_sources : str
        specify the path where state_observation_dict, transition_prob_dict and updated_pos_lexicon exist.
    return_list_of_tuples__token_tag : boolean
        Specify the type of result [tag1, tag2, ...] or [(token1,tag1), (token2,tag2), ...]

    Returns
    -------
    list of tags
        returns a list of tags of the correspond sentence.

    """
    # input
    state_observation_dict = load_obj("state_observation_dict", path_sources)
    transition_prob_dict = load_obj("transition_prob_dict", path_sources)
    updated_pos_lexicon = load_obj("updated_pos_lexicon", path_sources)

    # initialization
        ## add of Start ("") to the phrase in input
    words_sequence = [""] + phrase

        ## initialize the viterbi matrix
    viterbi_matrix = { 0:[("NULL",1)] } # NULL <=> Start
    w = 1
    while w <= len(phrase):
        viterbi_matrix[w] = []
        for tg in updated_pos_lexicon[words_sequence[w]]:
            viterbi_matrix[w].append((tg,0))
        w += 1

        ## initialize the backtrace matrix
    backtrace_matrix = {}
    w = 1
    while w <= len(phrase):
        for tg in updated_pos_lexicon[words_sequence[w]]:
            backtrace_matrix[(w,tg)] = ""
        w += 1

    # update both of viterbi and backtrace matrix
    i = 1
    while i <= len(phrase):
        prob_transition_all_null = True
        update = False
        """
        tg2|tg0 tg1
        w2|w0 tg0 w1 tg1 tg2
        or ( i == 1 )
        tg2|tg1
        w2|w1 tg1 tg2
        """
        tg_wi = 0
        while tg_wi < len(viterbi_matrix[i]):
            for tg1,value in viterbi_matrix[i-1]: # tg1 <=> tgi-1 value = viterbi[wi-1, tgi-1]
                # calculate the new score
                if value == 0: # test if viterbi_matrix[w-1][tgi-1] == 0 or not
                    continue
                # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                tg2 = viterbi_matrix[i][tg_wi][0]

                # now we don't have tg0
                if i-1 > 0:
                    # in that case tg0 exist
                    tg0 = backtrace_matrix[(i-1,tg1)]
                    try:
                        P_trans = transition_prob_dict[(tg2,(tg0,tg1))]
                    except:
                        continue
                else:
                    try:
                        P_trans = transition_prob_dict[(tg2,tg1)]
                    except:
                        # P_trans == 0
                        continue
                prob_transition_all_null = False # P_trans != 0

                # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                w2 = words_sequence[i]
                w1 = words_sequence[i-1]
                if i-1 > 0:
                    # in that we already have tg0 from the previous step
                    w0 = words_sequence[i-2]
                    try:
                        P_tag_observ = state_observation_dict[(w2,(w0,tg0,w1,tg1,tg2))]
                    except:
                        continue
                else:
                    try:
                        P_tag_observ = state_observation_dict[(w2,(w1,tg1,tg2))]
                    except:
                        continue

                score = value * P_trans * P_tag_observ
                # if score == 0:
                #     continue
                if score > viterbi_matrix[i][tg_wi][1]:
                    # update viterbi_matrix
                    viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                    # update backtrace_matrix
                    backtrace_matrix[(i,tg2)] = tg1

                    update = True

            tg_wi += 1

        if update == False and i > 1:
            """
            i > 1
            """
            if prob_transition_all_null == True:
                """
                tg2|tg1
                w2|w1 tg1 tg2
                """
                tg_wi = 0
                while tg_wi < len(viterbi_matrix[i]):
                    for tg1,value in viterbi_matrix[i-1]:
                        # calculate the new score
                        if value == 0:
                            continue
                        # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                        tg2 = viterbi_matrix[i][tg_wi][0]

                        try:
                            P_trans = transition_prob_dict[(tg2,tg1)]
                        except:
                            # P_trans == 0
                            continue
                        prob_transition_all_null = False

                        # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                        w2 = words_sequence[i]
                        w1 = words_sequence[i-1]

                        try:
                            P_tag_observ = state_observation_dict[(w2,(w1,tg1,tg2))]
                        except:
                            continue

                        score = value * P_trans * P_tag_observ
                        # if score == 0:
                        #     continue
                        if score > viterbi_matrix[i][tg_wi][1]:
                            # update viterbi_matrix
                            viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                            # update backtrace_matrix
                            backtrace_matrix[(i,tg2)] = tg1

                            update = True

                    tg_wi += 1

                if update == False:
                    if prob_transition_all_null == False:
                        """
                        tg2|tg1
                        w2|tg2
                        """
                        tg_wi = 0
                        while tg_wi < len(viterbi_matrix[i]):
                            for tg1,value in viterbi_matrix[i-1]:
                                # calculate the new score
                                if value == 0:
                                    continue
                                # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                                tg2 = viterbi_matrix[i][tg_wi][0]

                                try:
                                    P_trans = transition_prob_dict[(tg2,tg1)]
                                except:
                                    # P_trans == 0
                                    continue


                                # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                                w2 = words_sequence[i]
                                w1 = words_sequence[i-1]

                                try:
                                    P_tag_observ = state_observation_dict[(w2,tg2)]
                                except:
                                    # P_tag_observ == 0
                                    continue

                                score = value * P_trans * P_tag_observ
                                # if score == 0:
                                #     continue
                                if score > viterbi_matrix[i][tg_wi][1]:
                                    # update viterbi_matrix
                                    viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                                    # update backtrace_matrix
                                    backtrace_matrix[(i,tg2)] = tg1

                                    update = True

                            tg_wi += 1

                        # if update == False:
                        #     print(update)
                        #     break
                        """
                    else: # tg2|tg1 = 0 pout tout tg2
                        Go to (*)
                        """

            else:
                """
                tg2|tg0 tg1
                w2|w1 tg1 tg2
                """
                tg_wi = 0
                while tg_wi < len(viterbi_matrix[i]):
                    for tg1,value in viterbi_matrix[i-1]:
                        # calculate the new score
                        if value == 0:
                            continue
                        # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                        tg2 = viterbi_matrix[i][tg_wi][0]
                        # now we don't have tg0

                            # in that case tg0 exist
                        tg0 = backtrace_matrix[(i-1,tg1)]
                        try:
                            P_trans = transition_prob_dict[(tg2,(tg0,tg1))]
                        except:
                            continue


                        # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                        w2 = words_sequence[i]
                        w1 = words_sequence[i-1]

                        try:
                            P_tag_observ = state_observation_dict[(w2,(w1,tg1,tg2))]
                        except:
                            continue

                        score = value * P_trans * P_tag_observ
                        # if score == 0:
                        #     continue
                        if score > viterbi_matrix[i][tg_wi][1]:
                            # update viterbi_matrix
                            viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                            # update backtrace_matrix
                            backtrace_matrix[(i,tg2)] = tg1

                            update = True

                    tg_wi += 1

                if update == False:
                    """
                    tg2|tg0 tg1
                    w2|tg2
                    """
                    tg_wi = 0
                    while tg_wi < len(viterbi_matrix[i]):
                        for tg1,value in viterbi_matrix[i-1]:
                            # calculate the new score
                            if value == 0:
                                continue
                            # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                            tg2 = viterbi_matrix[i][tg_wi][0]
                            # now we don't have tg0

                            tg0 = backtrace_matrix[(i-1,tg1)]
                            try:
                                P_trans = transition_prob_dict[(tg2,(tg0,tg1))]
                            except:
                                continue


                            # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                            w2 = words_sequence[i]
                            w1 = words_sequence[i-1]


                            try:
                                P_tag_observ = state_observation_dict[(w2,tg2)]
                            except:
                                # P_tag_observ == 0
                                continue

                            score = value * P_trans * P_tag_observ
                            # if score == 0:
                            #     continue
                            if score > viterbi_matrix[i][tg_wi][1]:
                                # update viterbi_matrix
                                viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                                # update backtrace_matrix
                                backtrace_matrix[(i,tg2)] = tg1

                                update = True

                        tg_wi += 1


        # if update == False:
        #     break
        """
        (*)
        """
        if update == False:
            if i == 1:
                if not prob_transition_all_null:
                    """
                    tg2|tg1
                    w2|tg2
                    """
                    tg_wi = 0
                    while tg_wi < len(viterbi_matrix[i]):
                        for tg1,value in viterbi_matrix[i-1]:
                            # calculate the new score
                            if value == 0:
                                continue
                            # P_trans we want p_trans(tg2|tg0 tg1)   if not equal to 0, else p_trans(tg2|tg1)
                            tg2 = viterbi_matrix[i][tg_wi][0]

                            try:
                                P_trans = transition_prob_dict[(tg2,tg1)]
                            except:
                                # P_trans == 0
                                continue


                            # P_tag_observ we want P_tag_observ(w2|w0 tg0 w1 tg1 tg2) if != 0 , else P_tag_observ(w2|w1 tg1 tg2) if != 0, else P_tag_onbserv(w2|tg2)
                            w2 = words_sequence[i]
                            w1 = words_sequence[i-1]

                            try:
                                P_tag_observ = state_observation_dict[(w2,tg2)]
                            except:
                                # P_tag_observ == 0
                                continue

                            score = value * P_trans * P_tag_observ
                            # if score == 0:
                            #     continue
                            if score > viterbi_matrix[i][tg_wi][1]:
                                # update viterbi_matrix
                                viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],score)
                                # update backtrace_matrix
                                backtrace_matrix[(i,tg2)] = tg1

                                update = True

                        tg_wi += 1

                    i += 1
                    continue
            # for each case affect w2|tg2
            tg_wi = 0
            while tg_wi < len(viterbi_matrix[i]):
                tg2 = viterbi_matrix[i][tg_wi][0]
                w2 = words_sequence[i]
                # update viterbi_matrix
                try:
                    viterbi_matrix[i][tg_wi] = (viterbi_matrix[i][tg_wi][0],state_observation_dict[(w2,tg2)])
                except:
                    None
                # update backtrace_matrix
                # find tg1
                tg1,score_w1_tg1 = viterbi_matrix[i-1][0]
                for tg,score in viterbi_matrix[i-1]:
                    if score > score_w1_tg1:
                        tg1,score_w1_tg1 = (tg,score)
                backtrace_matrix[(i,tg2)] = tg1

                tg_wi += 1

        i += 1

    ######################
    # backtrace
    i -= 1
    tag_sequence = []
    max_ = ("", -1)
    for tg,score in viterbi_matrix[i]:
        if score > max_[1]:
            max_ = (tg,score)
    tg = max_[0]
    tag_sequence.append(tg)
    while i > 0:
        tg = backtrace_matrix[(i,tg)]
        tag_sequence.append(tg)
        i -= 1
    tag_sequence.reverse()
    ############################

    if return_list_of_tuples__token_tag:
        result = []
        for i in range(len(phrase)):
            result.append((phrase[i],tag_sequence[i+1]))

        return result
    else:
        return tag_sequence[1:]

#********************************************************
def tokenization(phrase):
    """

    Parameters
    ----------
    phrase : string
        the sentence (phrase) that will be tokenized.

    Returns
    -------
    tokens : list
        list of tokens.

    """
    # delete any non arabic letters
    n_phrase = ""
    for i in phrase:
        # add a pre and post space to any punctuation
        if ud.category(i).startswith('P'):
            n_phrase += " "+ i + " "
        else:
            if re.match("[\u0030-\u0039\uFE70-\uFEFF\u0600-\u06FF ]", i, re.UNICODE):
                n_phrase += i
                # \u0030-\u0039 for digits
                # \uFE70-\uFEFF\u0600-\u06FF arabic chars
                # \u002E\u2E3C\uFF0E\u3002\uA78F\u00B7 .


    # extract the tokens NB: و is not treated here
    tokens = n_phrase.split()
     # words_sequence = re.findall(r"\s*([\uFE70-\uFEFF\u0600-\u06FF]+)\s*", n_phrase, re.UNICODE)
     # words_sequence = word_tokenize(sentence)

    return tokens

#********************************************************
def buckwalter_analyzer(phrase):
    """

    Parameters
    ----------
    phrase : string
        the string that will be stemmed.

    Returns
    -------
    new_words_sequence : list
        returns a list of tokens without the diactrics.

    """
    analyzer = Analyzer.Analyzer()
    results = analyzer.analyze_text(phrase)

    new_words_sequence = []

    for analyses in results:
        intermediate_f = re.findall(rb"pos:\s*(.+)\s*", analyses[1].encode('utf-8')) # intermediate form
        intermediate_f = intermediate_f[0]
        intermediate_f = intermediate_f.decode('utf-8')
        ###################################################
        # get the prefix if exists, else the stem
        pre_stem = re.findall(r"(.+?)/", intermediate_f, re.DOTALL)[0]
        if len(pre_stem) > 2:
            if pre_stem[:2] == "h`":
                pre_stem = 'h'+pre_stem[2:]
            if pre_stem[:2] == "l`":
                pre_stem = 'l'+pre_stem[2:]
        pre_stem = buckwalter.buck2uni(pre_stem) # convert from backwalter format to unicode format
        pre_stem = pre_stem.encode('utf-8').decode('utf-8')
        pre_stem = re.sub(r"[\u0618-\u061A\u064B-\u0652]","", pre_stem) # omit the Fatha, Kasra, Damma, Small Fatha, Small Kasra, Small Damma, Fathatan, Kasratan, Dammatan, Shadda and Sukun
        # pre_stem = Analyzer._clean_arabic(word) we can use this instead
        if pre_stem != "":
            new_words_sequence.append(pre_stem)
        ###################################################
        # get the stem or/and the suffixes if exist
        for stem_suf in re.findall(r"\+(.+?)/", intermediate_f, re.DOTALL):
            if stem_suf == "(null)":
                continue
            # if stem_suf.beginswith(""):
            if len(pre_stem) > 2:
                if pre_stem[:2] == "h`":
                    pre_stem = 'h'+pre_stem[2:]
            stem_suf = buckwalter.buck2uni(stem_suf)
            stem_suf = stem_suf.encode('utf-8').decode('utf-8') # omit the Fatha, Kasra, Damma, Small Fatha, Small Kasra, Small Damma, Fathatan, Kasratan, Dammatan, Shadda and Sukun
            stem_suf = re.sub(r"[\u0618-\u061A\u064B-\u0652]","", stem_suf)
            if stem_suf != "":
                new_words_sequence.append(stem_suf)


    return new_words_sequence

#********************************************************
def stemming(tokens):

    """
    Parameters
    ----------
    tokens : list
        list of tokens.

    Returns
    -------
    new_tokens : list
        tokens stemmed using the backwalter stemmer.

    """
    new_tokens = []
    for token in tokens:
        if len(token) == 1 and ud.category(token).startswith('P'):
            new_tokens.append(token)
        else:
            result = buckwalter_analyzer(token)
            if len(result) == 0:
                new_tokens.append(token)
            else:
                new_tokens += buckwalter_analyzer(token)
    return new_tokens

#********************************************************
def normalization(tokensIn, path_sources):
    """

    Parameters
    ----------
    tokens : list
        list of tokens.
    path_sources : str
        the path where "updated_pos_lexicon" dictionnary exist

    Returns
    -------
    tokens : list
        list of tokens with normalized form
        (i.e., if one token doesn't exist in the POSLexicon, il will
        be replaced by مجه ).

    """
    updated_pos_lexicon = load_obj("updated_pos_lexicon", path_sources)
    tk = 0

    tokens = []

    while tk < len(tokensIn):
        if tokensIn[tk] not in updated_pos_lexicon:
            tokens.append("مجه")
        else:
            tokens.append(tokensIn[tk])
        tk += 1

    return tokens

#********************************************************
def tok_stem(string, is_phrase = True): # phrase is string
    """

    Parameters
    ----------
    string : str
        the sentence that will be tokenized, stemmed and normalized.
    is_phrase : boolean
        specify if string is a phrase (sentence) or a text.

    Returns
    -------
    list | list of list
        list of tokens (after tokenization and stemming) with normalized
        form (i.e., omit the diactritics), if the parameter is_phrase is True (the default option).
        else list of list of tokens (after tokenization and stemming) with
        normalized form (i.e., omit the diactritics).
        NB : we don't treat the case if a token is unknown or not.

    """
    stemmed_phrase = ' '.join(buckwalter_analyzer(string))
    # sent = re.sub(r"[\u0618-\u061A\u064B-\u0652]","", phrase) # omit the Fatha, Kasra, Damma, Small Fatha, Small Kasra, Small Damma, Fathatan, Kasratan, Dammatan, Shadda and Sukun
    i = 0
    sent = "" # after the while the sent will contain the phrase without the diacritics and the punctuation will be isolated by spaces and الأ (resp. اﻹ) will be replaced by ال أ (resp. ال إ)
    while i < len(string):
        if string[i] not in ['\u0618', '\u0619', '\u061A', '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652']: # diacritics
            if ud.category(string[i]).startswith('P'): # punctuations
                sent += " " + string[i] + " "
                i += 1
            else:
                if len(string) - i > 3:
                    if string[i] in ['\u0627', '\u0644', '\u0623']: # ا
                        if string[i+1] in ['\u0644', '\uFEDD', '\uFEDE', '\uFEDF']: # ل
                            if string[i+2] == '\u0623': # أ
                                sent += '\u0627' + '\u0644' + ' ' + '\u0623' # ال أ
                            else:
                                if string[i+2] == '\u0625': # إ
                                    sent += '\u0627' + '\u0644' + ' ' + '\u0625' # ال إ
                                else:
                                    sent += string[i] + string[i+1] + string[i+2]
                            i += 3
                        else:
                            if string[i+1] == "\uFEF7": # ﻷ
                                sent += '\u0627' + '\u0644' + ' ' + '\u0623' # ال أ
                            else:
                                if string[i+1] == "\uFEF9": # ﻹ
                                    sent += string[i] + string[i+1] + string[i+2] # ال إ
                                else:
                                    sent += string[i] + string[i+1]

                            i += 2

                    else:

                        sent += string[i]
                        i += 1
                else:
                    sent += string[i]
                    i += 1
        else:
            i += 1
    result = ""
    i_st = 0
    i_se = 0
    while i_se < len(sent) and i_st < len(stemmed_phrase):
        if equal(sent[i_se],stemmed_phrase[i_st]):
            result += sent[i_se]
            i_st += 1
            i_se += 1
        else:

            if stemmed_phrase[i_st] == " ":
                result += " "
                i_st += 1
            else:
                result += sent[i_se]
                i_se += 1
    while i_se < len(sent):
        result += sent[i_se]
        i_se += 1

    if is_phrase:
        return result.split()
    else:
        return [sent.split() for sent in sent_tokenize(result)]

#****************************************************************
def equal(l1,l2):
    """

    Parameters
    ----------
    l1 : unicode char
        A character in unicode.
    l2 : unicode char
        A character in unicode.

    Returns
    -------
    boolean
        True if l1 equals or equivalent to l2.

    """
    if l1 == l2:
        return True
    equivalent = {
        ("\u0627","\uFE8D"), ("\u0627","\uFE8E"), ("\uFE8D","\uFE8E"), # ("\u0627","\u0623"), ("\u0627","\u0625"),
        ("\u0628","\uFE8F"), ("\u0628","\uFE90"), ("\u0628","\uFE92"), ("\u0628","\uFE91"), ("\uFE8F","\uFE90"), ("\uFE8F","\uFE92"), ("\uFE8F","\uFE91"), ("\uFE90","\uFE92"), ("\uFE90","\uFE91"), ("\uFE92","\uFE91"),
        ("\u062A","\uFE95"), ("\u062A","\uFE96"), ("\u062A","\uFE98"), ("\u062A","\uFE97"), ("\uFE95","\uFE96"), ("\uFE95","\uFE98"), ("\uFE95","\uFE97"), ("\uFE96","\uFE98"), ("\uFE96","\uFE97"), ("\uFE98","\uFE97"),
        ("\u062B","\uFE99"), ("\u062B","\uFE9A"), ("\u062B","\uFE9C"), ("\u062B","\uFE9B"), ("\uFE99","\uFE9A"), ("\uFE99","\uFE9C"), ("\uFE99","\uFE9B"), ("\uFE9A","\uFE9C"), ("\uFE9A","\uFE9B"), ("\uFE9C","\uFE9B"),
        ("\u062C","\uFE9D"), ("\u062C","\uFE9E"), ("\u062C","\uFEA0"), ("\u062C","\uFE9F"), ("\uFE9D","\uFE9E"), ("\uFE9D","\uFEA0"), ("\uFE9D","\uFE9F"), ("\uFE9E","\uFEA0"), ("\uFE9E","\uFE9F"), ("\uFEA0","\uFE9F"),
        ("\u062D","\uFEA1"), ("\u062D","\uFEA2"), ("\u062D","\uFEA4"), ("\u062D","\uFEA3"), ("\uFEA1","\uFEA2"), ("\uFEA1","\uFEA4"), ("\uFEA1","\uFEA3"), ("\uFEA2","\uFEA4"), ("\uFEA2","\uFEA3"), ("\uFEA4","\uFEA3"),
        ("\u062E","\uFEA5"), ("\u062E","\uFEA6"), ("\u062E","\uFEA8"), ("\u062E","\uFEA7"), ("\uFEA5","\uFEA6"), ("\uFEA5","\uFEA8"), ("\uFEA5","\uFEA7"), ("\uFEA6","\uFEA8"), ("\uFEA6","\uFEA7"), ("\uFEA8","\uFEA7"),
        ("\u062F","\uFEA9"), ("\u062F","\uFEAA"), ("\uFEA9","\uFEAA"),
        ("\u0630","\uFEAB"), ("\u0630","\uFEAC"), ("\uFEAB","\uFEAC"),
        ("\u0631","\uFEAD"), ("\u0631","\uFEAE"), ("\uFEAD","\uFEAE"),
        ("\u0632","\uFEAF"), ("\u0632","\uFEB0"), ("\uFEAF","\uFEB0"),
        ("\u0633","\uFEB1"), ("\u0633","\uFEB2"), ("\u0633","\uFEB4"), ("\u0633","\uFEB3"), ("\uFEB1","\uFEB2"), ("\uFEB1","\uFEB4"), ("\uFEB1","\uFEB3"), ("\uFEB2","\uFEB4"), ("\uFEB2","\uFEB3"), ("\uFEB4","\uFEB3"),
        ("\u0634","\uFEB5"), ("\u0634","\uFEB6"), ("\u0634","\uFEB8"), ("\u0634","\uFEB7"), ("\uFEB5","\uFEB6"), ("\uFEB5","\uFEB8"), ("\uFEB5","\uFEB7"), ("\uFEB6","\uFEB8"), ("\uFEB6","\uFEB7"), ("\uFEB8","\uFEB7"),
        ("\u0635","\uFEB9"), ("\u0635","\uFEBA"), ("\u0635","\uFEBC"), ("\u0635","\uFEBB"), ("\uFEB9","\uFEBA"), ("\uFEB9","\uFEBC"), ("\uFEB9","\uFEBB"), ("\uFEBA","\uFEBC"), ("\uFEBA","\uFEBB"), ("\uFEBC","\uFEBB"),
        ("\u0636","\uFEBD"), ("\u0636","\uFEBE"), ("\u0636","\uFEC0"), ("\u0636","\uFEBF"), ("\uFEBD","\uFEBE"), ("\uFEBD","\uFEC0"), ("\uFEBD","\uFEBF"), ("\uFEBE","\uFEC0"), ("\uFEBE","\uFEBF"), ("\uFEC0","\uFEBF"),
        ("\u0637","\uFEC1"), ("\u0637","\uFEC2"), ("\u0637","\uFEC4"), ("\u0637","\uFEC3"), ("\uFEC1","\uFEC2"), ("\uFEC1","\uFEC4"), ("\uFEC1","\uFEC3"), ("\uFEC2","\uFEC4"), ("\uFEC2","\uFEC3"), ("\uFEC4","\uFEC3"),
        ("\u0638","\uFEC5"), ("\u0638","\uFEC6"), ("\u0638","\uFEC8"), ("\u0638","\uFEC7"), ("\uFEC5","\uFEC6"), ("\uFEC5","\uFEC8"), ("\uFEC5","\uFEC7"), ("\uFEC6","\uFEC8"), ("\uFEC6","\uFEC7"), ("\uFEC8","\uFEC7"),
        ("\u0639","\uFEC9"), ("\u0639","\uFECA"), ("\u0639","\uFECC"), ("\u0639","\uFECB"), ("\uFEC9","\uFECA"), ("\uFEC9","\uFECC"), ("\uFEC9","\uFECB"), ("\uFECA","\uFECC"), ("\uFECA","\uFECB"), ("\uFECC","\uFECB"),
        ("\u063A","\uFECD"), ("\u063A","\uFECE"), ("\u063A","\uFED0"), ("\u063A","\uFECF"), ("\uFECD","\uFECE"), ("\uFECD","\uFED0"), ("\uFECD","\uFECF"), ("\uFECE","\uFED0"), ("\uFECE","\uFECF"), ("\uFED0","\uFECF"),
        ("\u0641","\uFED1"), ("\u0641","\uFED2"), ("\u0641","\uFED4"), ("\u0641","\uFED3"), ("\uFED1","\uFED2"), ("\uFED1","\uFED4"), ("\uFED1","\uFED3"), ("\uFED2","\uFED4"), ("\uFED2","\uFED3"), ("\uFED4","\uFED3"),
        ("\u0642","\uFED5"), ("\u0642","\uFED6"), ("\u0642","\uFED8"), ("\u0642","\uFED7"), ("\uFED5","\uFED6"), ("\uFED5","\uFED8"), ("\uFED5","\uFED7"), ("\uFED6","\uFED8"), ("\uFED6","\uFED7"), ("\uFED8","\uFED7"),
        ("\u0643","\uFED9"), ("\u0643","\uFEDA"), ("\u0643","\uFEDC"), ("\u0643","\uFEDB"), ("\uFED9","\uFEDA"), ("\uFED9","\uFEDC"), ("\uFED9","\uFEDB"), ("\uFEDA","\uFEDC"), ("\uFEDA","\uFEDB"), ("\uFEDC","\uFEDB"),
        ("\u0644","\uFEDD"), ("\u0644","\uFEDE"), ("\u0644","\uFEE0"), ("\u0644","\uFEDF"), ("\uFEDD","\uFEDE"), ("\uFEDD","\uFEE0"), ("\uFEDD","\uFEDF"), ("\uFEDE","\uFEE0"), ("\uFEDE","\uFEDF"), ("\uFEE0","\uFEDF"),
        ("\u0645","\uFEE1"), ("\u0645","\uFEE2"), ("\u0645","\uFEE4"), ("\u0645","\uFEE3"), ("\uFEE1","\uFEE2"), ("\uFEE1","\uFEE4"), ("\uFEE1","\uFEE3"), ("\uFEE2","\uFEE4"), ("\uFEE2","\uFEE3"), ("\uFEE4","\uFEE3"),
        ("\u0646","\uFEE5"), ("\u0646","\uFEE6"), ("\u0646","\uFEE8"), ("\u0646","\uFEE7"), ("\uFEE5","\uFEE6"), ("\uFEE5","\uFEE8"), ("\uFEE5","\uFEE7"), ("\uFEE6","\uFEE8"), ("\uFEE6","\uFEE7"), ("\uFEE8","\uFEE7"),
        ("\u0647","\uFEE9"), ("\u0647","\uFEEA"), ("\u0647","\uFEEC"), ("\u0647","\uFEEB"), ("\uFEE9","\uFEEA"), ("\uFEE9","\uFEEC"), ("\uFEE9","\uFEEB"), ("\uFEEA","\uFEEC"), ("\uFEEA","\uFEEB"), ("\uFEEC","\uFEEB"),
        ("\u0648","\uFEED"), ("\u0648","\uFEEE"), ("\uFEED","\uFEEE"),
        ("\u064A","\uFEF1"), ("\u064A","\uFEF2"), ("\u064A","\uFEF4"), ("\u064A","\uFEF3"), ("\uFEF1","\uFEF2"), ("\uFEF1","\uFEF4"), ("\uFEF1","\uFEF3"), ("\uFEF2","\uFEF4"), ("\uFEF2","\uFEF3"), ("\uFEF4","\uFEF3"),
        ("\u0622","\uFE81"), ("\u0622","\uFE82"), ("\uFE81","\uFE82"),
        ("\u0629","\uFE93"), ("\u0629","\uFE94"), ("\uFE93","\uFE94"),
        ("\u0649","\uFEEF"), ("\u0649","\uFEF0"), ("\uFEEF","\uFEF0")
        }
    return ((l1,l2) in equivalent) or ((l2,l1) in equivalent)

#****************************************************************
def add_new_sent(phrase, tokenized_phrase, POS_TAGS, annotated_corpus_path, annotated_corpus_name, path_sources):
    """

    Parameters
    ----------
    phrase : str
        the sentence that will be added to annotated_corpus.
    tokenized_phrase : list
        a list of tokens of phrase.
    POS_TAGS : list
        the tags attributed to the diffrent tokens of tokenized_phrase.
    annotated_corpus_path : str
        specify the path of the XML file where to add the new phrase
        e.g. /home/user/corpus/
    annotated_corpus_name : str
        specify the name of the corpus
    path_sources : str
        specify the path where ("talaa_pos_dic_phrase_"+annotated_corpus_name) dictionnary exist.

    Returns
    -------
    add a new phrase in the end of the specified xml file.
    and update the correspond dictionnary.

    """

    talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)

    n_phrase = len(talaa_pos_dic_phrase)
    header = "\t<Phrase_" + str(n_phrase) + ">\n"
    footer = "\t</Phrase_" + str(n_phrase) + ">\n"
    Num_phrase = "\t\t<Num_phrase>" + str(n_phrase) + "</Num_phrase>\n"
    Text = "\t\t<Text>" + phrase + "\n</Text>\n"
    Tokenisation = "\t\t<Tokenisation>" + " ".join(tokenized_phrase) + "</Tokenisation>\n"
    POS_Tag = "\t\t<POS_Tag>" + " ".join(POS_TAGS) + "</POS_Tag>\n"
    Nb_Mot = "\t\t<Nb_Mot>" + str(len(set(tokenized_phrase))) + "</Nb_Mot>\n"
    Nb_Token = "\t\t<Nb_Token>" + str(len(tokenized_phrase)) + "</Nb_Token>\n"

    with open(annotated_corpus_path+annotated_corpus_name+".xml", "r+", encoding = "utf-8") as file:
        content_of_file = file.read().replace("</BASE_DE_DONNEE>", header + Num_phrase + Text + Tokenisation + POS_Tag + Nb_Mot + Nb_Token + footer + "</BASE_DE_DONNEE>")
        file.seek(0)
        file.truncate()
        file.write(content_of_file)
        file.close()

    talaa_pos_dic_phrase[n_phrase] = [phrase, tokenized_phrase, POS_TAGS, str(len(set(tokenized_phrase))), str(len(tokenized_phrase))]
    save_obj(talaa_pos_dic_phrase, "talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)

#****************************************************************
def edit_annotated_corpus(phrase_number, token_tag, annotated_corpus_path, annotated_corpus_name, path_sources):
    """

    Parameters
    ----------
    phrase_number : int
        number of the phrase that will be modified (begins from 0).
    token_tag : list of 2 tuples (token, tag)
        List of new tokens/tags with which the "phrase_number" will be edited.
    annotated_corpus_path : str
        specify the full path of the XML file.
    annotated_corpus_name : str
        specify the name of the corpus
    path_sources : str
        specify the path where "talaa_pos_dic_phrase" dictionnary exist..

    Returns
    -------
    update both of ("talaa_pos_dic_phrase_"+annotated_corpus_name) and the annotated corpus if necessary.

    """
    talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)

    size_of_corpus = len(talaa_pos_dic_phrase)

    if not (0 <= phrase_number < size_of_corpus):
        return

    Tokenization = []
    POS_TAG = ['NULL']
    for token, tag in token_tag:
        Tokenization.append(token)
        POS_TAG.append(tag)

    talaa_pos_dic_phrase[phrase_number][1] = Tokenization
    talaa_pos_dic_phrase[phrase_number][2] = POS_TAG


    with open(annotated_corpus_path+annotated_corpus_name+".xml", "w", encoding = "utf-8") as file:
        content_of_file = "<BASE_DE_DONNEE>"
        phrase_number = 0
        while phrase_number < size_of_corpus:

            header = "\t<Phrase_" + str(phrase_number) + ">\n"
            footer = "\t</Phrase_" + str(phrase_number) + ">\n"
            Num_phrase = "\t\t<Num_phrase>" + str(phrase_number) + "</Num_phrase>\n"
            Text = "\t\t<Text>" + talaa_pos_dic_phrase[phrase_number][0] + "\n</Text>\n"
            Tokenisation = "\t\t<Tokenisation>" + " ".join(talaa_pos_dic_phrase[phrase_number][1]) + "</Tokenisation>\n"
            POS_Tag = "\t\t<POS_Tag>" + " ".join(talaa_pos_dic_phrase[phrase_number][2]) + "</POS_Tag>\n"
            Nb_Mot = "\t\t<Nb_Mot>" + str(talaa_pos_dic_phrase[phrase_number][3]) + "</Nb_Mot>\n"
            Nb_Token = "\t\t<Nb_Token>" + str(talaa_pos_dic_phrase[phrase_number][4]) + "</Nb_Token>\n"

            content_of_file += header + Num_phrase + Text + Tokenisation + POS_Tag + Nb_Mot + Nb_Token + footer
            phrase_number += 1

        content_of_file += "</BASE_DE_DONNEE>"
        file.seek(0)
        file.truncate()
        file.write(content_of_file)
        file.close()

    save_obj(talaa_pos_dic_phrase, "talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)


#****************************************************************
def generate_model(annotated_corpus_path, annotated_corpus_names, path_sources, path__updates__, annotated_corpus_dictionnaries_updated = True, learning_percentage = 100, percent_phrases = 100):
    """

    Parameters
    ----------
    annotated_corpus_path : str
        specify full path of the annotated XML corpus.
        e.g. /home/user/corpus/
    annotated_corpus_names : list
        specify the list of the names of the annotated corpus.
    path_sources : str
        specify where the updated_pos_lexicon exist,
          //     //   //  annotated corpus dictionnaries (talaa_...) exist or will be saved
        (also it is the path where the generated files will be saved).
    path__updates__ : str
        the path where to save the updates made to pos_lexicon.
    annotated_corpus_dictionnaries_updated : boolean
        specify if the annotated corpus dictionnaries is updated|created + pos_lexicon updated or not;
        if True then we skip the step of creating|updating the dictionnaries, else this step will be done
        NB: By default, its True.
    learning_percentage : int
        the percentage of phrases concerned by the learning phase.
        By default all the phrases of the corpus is concerned.
    percent_phrases : int
        the percentage of the phrases from the phrases of learning for which the pos_lexicon will be updated.

    Returns
    -------
    An updated POSLexicon dictionnary.
    A new transition prob dictionnary.
    A new state observation prob dictionnary.

    """
    # convert the corpus with xml format to a dictionary "talaa_pos_dic_phrase" { key: n°Phrase => value:[phrase_text,tokenixation,POS_Tag,Nb_mots,Nb_tokens]}
    if not annotated_corpus_dictionnaries_updated:
        for name_of_corpus in annotated_corpus_names:
            talaa_pos_xml2talaa_pos_dic_phrase(annotated_corpus_path, name_of_corpus,path_sources)
            update_pos_lexicon(path_sources, name_of_corpus, path__updates__, int(learning_percentage * percent_phrases/100))

    # normalize the dictionary created (i.e. "talaa_pos_dic_phrase")
    for name_of_corpus in annotated_corpus_names:
        normalize_corpus(path_sources, name_of_corpus, path__updates__, learning_percentage, percent_phrases)

    # create the transition prob matrix P(tg2|tg0 tg1) P(tg2|tg1)
    transition_prob(annotated_corpus_names, path_sources)

    # create the state observation prob P(w2|w0 tg0 w1 tg1 tg2) P(w2|w1 tg1 tg2) P(w2|tg2)
    state_observation_prob(annotated_corpus_names, path_sources)


#********************************************************
def normalize_corpus(path_sources, annotated_corpus_name, path__updates__, learning_percentage = 100, percent_phrases = 100):
    """

    Parameters
    ----------
    path_sources : str
        specify where the updated_pos_lexicon and the talaa_pos_dic_phrase_[annotated_corpus_name] exist.
    annotated_corpus_name : str
        specify the name of the corpus.
    path__updates__ : str
        the path where to save the updates made it to pos_lexicon.
    learning_percentage : int
        the percentage of phrases concerned by the learning phase.
        By default all the phrases of the corpus is concerned.
    percent_phrases : int
        the percentage of the phrases from the phrases of learning for which the pos_lexicon will be updated.


    Returns
    -------
    regenerate the two dictionnaries "updated_pos_lexicon" and ("talaa_pos_dic_phrase_"+annotated_corpus_name)
    after a potential modifications.
    modifications :
       - create (if not exist) a new entry in "updated_pos_lexicon" ukn : {"NOUN"}
       - create a copy of "talaa_pos_dic_phrase" and replace each token (in that copy) that is not in updated_pos_lexicon by ukn = "مجه" and add its tag to "updated_pos_lexicon" if its not there
       - if a token is tagged with new tag (which is not in "updated_pos_lexicon") then added it to "updated_pos_lexicon"
       - save the

    """
    # input
    updated_pos_lexicon = load_obj("updated_pos_lexicon", path_sources)
    talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_"+annotated_corpus_name, path_sources)

    # constants
    unk = "مجه"
    # the updates
    updates = ""

    if unk not in updated_pos_lexicon:
        # update the POSLexicon dictionary {POSLexicon["مجه"] => {tg1,...,tgn}}
        updated_pos_lexicon[unk] = {"NOUN"}
        # +
        updates += "\najout d'un nouveau morpheme ( " + unk + " ) avec le tag : NOUN"

    # normalize the talaa_pos_dic_phrase
    len_talaa_pos_dic_phrase = len(talaa_pos_dic_phrase)
    start = int(len_talaa_pos_dic_phrase * int(learning_percentage * percent_phrases/100)/100)
    end = int(len_talaa_pos_dic_phrase * learning_percentage / 100)

    phrase = start
    while phrase < end:
        tk = 0
        while tk < len(talaa_pos_dic_phrase[phrase][1]):
            token = talaa_pos_dic_phrase[phrase][1][tk]
            tag = talaa_pos_dic_phrase[phrase][2][tk+1]
            if token not in updated_pos_lexicon:
                talaa_pos_dic_phrase[phrase][1][tk] = unk
                updated_pos_lexicon[unk].add(tag)
                # +
                updates += "\najout de " + tag + " à " + unk

            else:
                if tag not in updated_pos_lexicon[token]:
                    updated_pos_lexicon[token].add(tag)
                    # +
                    updates += "\najout de " + tag + " à " + token
            tk += 1
        phrase += 1

    save_obj(updated_pos_lexicon, "updated_pos_lexicon", path_sources)
    save_obj(talaa_pos_dic_phrase, "talaa_pos_dic_phrase_n_"+annotated_corpus_name, path_sources)

    # =
    with open(path__updates__ + "lesMajApportAvecLeCorpus_"+ annotated_corpus_name +".txt", "a", encoding = "utf-8") as file:
        file.seek(0)
        file.truncate()
        file.write(updates)
        file.close()

#********************************************************
def POSTagging___time(phrase, path_sources, number_of_times):
    """

    Parameters
    ----------
    phrase : list
        list of tokens.
    path_sources : str
        specify the path where state_observation_dict, transition_prob_dict and updated_pos_lexicon exist.
    number_of_times : int
        the number of times the viterbi is repeated.

    Returns
    -------
    None.

    """
    # preparation
    # normalize the list in order to pass it to POSTagging function as string
    normalized_form_of_new_phrase = "["
    for token in phrase:
        normalized_form_of_new_phrase += "'"+ token +"',"
    normalized_form_of_new_phrase = normalized_form_of_new_phrase[:-1] +"]"

    SETUP_CODE = '''
from __main__ import viterbi
    '''

    TEST_CODE = '''
viterbi('''+normalized_form_of_new_phrase+",'"+ path_sources+'''')
    '''
    times = timeit.repeat(setup = SETUP_CODE,
                          stmt = TEST_CODE,
                          repeat = 3,
                          number = number_of_times)

    print("time = ",min(times)/number_of_times)

#********************************************************


#********************************************************
def Tokenization___time(string, is_phrase, number_of_times):
    """

    Parameters
    ----------
    string : str
        the sentence that will be tokenized, stemmed and normalized.
    is_phrase : boolean
        specify if string is a phrase (sentence) or a text.
    number_of_times : TYPE
        the number of times the tok_stem is repeated.

    Returns
    -------
    None.

    """

    SETUP_CODE = '''
from __main__ import tok_stem
    '''

    TEST_CODE = '''
tok_stem("'''+ string +'",'+ is_phrase +''')
    '''
    times = timeit.repeat(setup = SETUP_CODE,
                          stmt = TEST_CODE,
                          repeat = 3,
                          number = number_of_times)

    print("time = ",min(times)/number_of_times)


#********************************************************
def evaluate_POSTagger(path_sources, annotated_corpus_names, test_percentage):

    # Calculate the recall
    total_correct = 0
    response_correct = 0
    for name_of_corpus in annotated_corpus_names:
        talaa_pos_dic_phrase = load_obj("talaa_pos_dic_phrase_"+name_of_corpus, path_sources)

        len_talaa_pos_dic_phrase = len(talaa_pos_dic_phrase)
        start = int(len_talaa_pos_dic_phrase * (100 - test_percentage) / 100)
        end = len_talaa_pos_dic_phrase

        phrase = start
        while phrase < end:
            print(phrase)
            tokens = talaa_pos_dic_phrase[phrase][1]
            pos_tags = talaa_pos_dic_phrase[phrase][2][1:]

            result_pos_tagging = viterbi(tokens, path_sources)

            len_pos_tags = len(pos_tags)
            total_correct += len_pos_tags
            # comparison
            pos_tag = 0
            while pos_tag < len_pos_tags:
                try:
                    if pos_tags[pos_tag] == result_pos_tagging[pos_tag]:
                        response_correct += 1
                except:
                    None
                pos_tag += 1
            phrase += 1
    return response_correct/total_correct

#********************************************************
def save_obj(obj, name, path):
    """

    Parameters
    ----------
    obj : object
        the object that will be saved.
    name : string
        the name of the saved file (pkl file).
    path : string
        the full path where obj will be saved.

    Returns
    -------
    None.

    """
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

#********************************************************
def load_obj(name, path):
    """

    Parameters
    ----------
    name : string
        the named of the pkl file that will be loaded.
    path : string
        the full path of the intended file.

    Returns
    -------
    type of the object within the file
        the object in the specified file.

    """
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)


##### Test #####
if __name__ == '__main__':

    projectPath = 'C:/Users/SOUFIAN/Desktop/TALN_Lamine/'
    pos_lexicon_file_path = projectPath + "test/POS_LEXICON_2005/POSLexicon.txt"
    annotated_corpus_path = projectPath + "test/corpus/"
    path_sources = projectPath + "test/sources/"
    annotated_corpus_names = ["TALAA--POS annotated corpus v1", "TALAA--POS annotated corpus v2"]
    path__updates__ = projectPath + "test/Lexique/"

    ########################################################
    pos_lexicon_file2dict_morphem_setOfTags(pos_lexicon_file_path, path_sources)


    ########################################################
    for corpus_name in annotated_corpus_names:
        talaa_pos_xml2talaa_pos_dic_phrase(annotated_corpus_path, corpus_name, path_sources)

    ########################################################
    # update_pos_lexicon(path_sources, "TALAA--POS annotated corpus v1", path__updates__, 80)
    # update_pos_lexicon(path_sources, "TALAA--POS annotated corpus v2", path__updates__, 90)


    ########################################################
    generate_model(annotated_corpus_path, annotated_corpus_names, path_sources, path__updates__, annotated_corpus_dictionnaries_updated = True, learning_percentage = 90, percent_phrases = 90)
    # or we can use instead :
    # generate_model(annotated_corpus_path, annotated_corpus_names, path__updates__, path_sources)

    #######################################################
    phrase = "كما تم اكتشاف مصاحف في باتنة على غلافها نجمة داود."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "إثارة الشك والتشكيك في جدية هذه المشاريع."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = " لم يتخلص من غيه ."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "ألقى اﻷستاذ الدرس."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "سارع إلى إطفاء الحريق."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "الشمس مشرقة."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "طلع البدر علينا."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "ألئك."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    phrase = "لكنهم أتو."
    new_phrase = normalization(tok_stem(phrase), path_sources)
    print(new_phrase)
    print(tok_stem(phrase))
    print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    text = "لم يلتفت الحكام إلى مطالب المتظاهرين. لذا فإن المتظاهرين ألحوا في الطلب."
    print(text)
    for tokens in tok_stem(text, False):
        new_phrase = normalization(tokens, path_sources)
        print(new_phrase)
        print(viterbi(new_phrase, path_sources))

    print("\n-----------------------")

    for corpus_name in annotated_corpus_names:
         print("\nedit corpus :")
         print(corpus_name+" :\n\n")
         edit_annotated_corpus(annotated_corpus_path, corpus_name, path_sources)

    print("\n-----------------------")
    phrase = "طلع البدر علينا."
    new_phrase = normalization(tokens, path_sources)

    POSTagging___time(new_phrase, path_sources, 2)

    print("\n-----------------------")
    text = "لم يلتفت الحكام إلى مطالب المتظاهرين. لذا فإن المتظاهرين ألحوا في الطلب."

    Tokenization___time(text, 'False', 2)

    print("\n-----------------------")
    print("evaluation :")
    print("Recall = " + str(evaluate_POSTagger(path_sources, annotated_corpus_names, 10) * 100), "%")
