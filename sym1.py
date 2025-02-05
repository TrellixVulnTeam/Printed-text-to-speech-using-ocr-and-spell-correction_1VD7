import re, random
import spacy
nlp = spacy.load('en_core_web_sm')

to_sample = False # if you're impatient switch this flag

def spacy_tokenize(text):
    return [token.text for token in nlp.tokenizer(text)]

def dameraulevenshtein(seq1, seq2):
    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        twoago, oneago, thisrow = (oneago, thisrow, [0] * len(seq2) + [x + 1])
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                    and seq1[x - 1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]


class SymSpell:
    def __init__(self, max_edit_distance=3, verbose=0):
        self.max_edit_distance = max_edit_distance
        self.verbose = verbose
        self.dictionary = {}
        self.longest_word_length = 0

    def get_deletes_list(self, w):
        deletes = []
        queue = [w]
        for d in range(self.max_edit_distance):
            temp_queue = []
            for word in queue:
                if len(word) > 1:
                    for c in range(len(word)):  # character index
                        word_minus_c = word[:c] + word[c + 1:]
                        if word_minus_c not in deletes:
                            deletes.append(word_minus_c)
                        if word_minus_c not in temp_queue:
                            temp_queue.append(word_minus_c)
            queue = temp_queue

        return deletes

    def create_dictionary_entry(self, w):
        '''add word and its derived deletions to dictionary'''
        new_real_word_added = False
        if w in self.dictionary:
            self.dictionary[w] = (self.dictionary[w][0], self.dictionary[w][1] + 1)
        else:
            self.dictionary[w] = ([], 1)
            self.longest_word_length = max(self.longest_word_length, len(w))

        if self.dictionary[w][1] == 1:
            new_real_word_added = True
            deletes = self.get_deletes_list(w)
            for item in deletes:
                if item in self.dictionary:
                    self.dictionary[item][0].append(w)
                else:
                    self.dictionary[item] = ([w], 0)

        return new_real_word_added

    def create_dictionary_from_arr(self, arr, token_pattern=r'[a-z]+'):
        total_word_count = 0
        unique_word_count = 0

        for line in arr:
            words = re.findall(token_pattern, line.lower())
            for word in words:
                total_word_count += 1
                if self.create_dictionary_entry(word):
                    unique_word_count += 1

        print("total words processed: %i" % total_word_count)
        print("total unique words in corpus: %i" % unique_word_count)
        print("total items in dictionary (corpus words and deletions): %i" % len(self.dictionary))
        print("  edit distance for deletions: %i" % self.max_edit_distance)
        print("  length of longest word in corpus: %i" % self.longest_word_length)
        return self.dictionary

    def create_dictionary(self, fname):
        total_word_count = 0
        unique_word_count = 0

        with open(fname) as file:
            for line in file:
                words = re.findall('[a-z]+', line.lower())
                for word in words:
                    total_word_count += 1
                    if self.create_dictionary_entry(word):
                        unique_word_count += 1

        print("total words processed: %i" % total_word_count)
        print("total unique words in corpus: %i" % unique_word_count)
        print("total items in dictionary (corpus words and deletions): %i" % len(self.dictionary))
        print("  edit distance for deletions: %i" % self.max_edit_distance)
        print("  length of longest word in corpus: %i" % self.longest_word_length)
        return self.dictionary

    def get_suggestions(self, string, silent=False):
        """return list of suggested corrections for potentially incorrectly
           spelled word"""
        if (len(string) - self.longest_word_length) > self.max_edit_distance:
            if not silent:
                print("no items in dictionary within maximum edit distance")
            return []

        suggest_dict = {}
        min_suggest_len = float('inf')

        queue = [string]
        q_dictionary = {}  # items other than string that we've checked

        while len(queue) > 0:
            q_item = queue[0]  # pop
            queue = queue[1:]

            # early exit
            if ((self.verbose < 2) and (len(suggest_dict) > 0) and
                    ((len(string) - len(q_item)) > min_suggest_len)):
                break

            # process queue item
            if (q_item in self.dictionary) and (q_item not in suggest_dict):
                if self.dictionary[q_item][1] > 0:
                    assert len(string) >= len(q_item)
                    suggest_dict[q_item] = (self.dictionary[q_item][1],
                                            len(string) - len(q_item))
                    # early exit
                    if (self.verbose < 2) and (len(string) == len(q_item)):
                        break
                    elif (len(string) - len(q_item)) < min_suggest_len:
                        min_suggest_len = len(string) - len(q_item)

                for sc_item in self.dictionary[q_item][0]:
                    if sc_item not in suggest_dict:

                        assert len(sc_item) > len(q_item)

                        assert len(q_item) <= len(string)

                        if len(q_item) == len(string):
                            assert q_item == string
                            item_dist = len(sc_item) - len(q_item)
                        assert sc_item != string

                        item_dist = dameraulevenshtein(sc_item, string)

                        if (self.verbose < 2) and (item_dist > min_suggest_len):
                            pass
                        elif item_dist <= self.max_edit_distance:
                            assert sc_item in self.dictionary  # should already be in dictionary if in suggestion list
                            suggest_dict[sc_item] = (self.dictionary[sc_item][1], item_dist)
                            if item_dist < min_suggest_len:
                                min_suggest_len = item_dist
                        if self.verbose < 2:
                            suggest_dict = {k: v for k, v in suggest_dict.items() if v[1] <= min_suggest_len}

            assert len(string) >= len(q_item)

            if (self.verbose < 2) and ((len(string) - len(q_item)) > min_suggest_len):
                pass
            elif (len(string) - len(q_item)) < self.max_edit_distance and len(q_item) > 1:
                for c in range(len(q_item)):  # character index
                    word_minus_c = q_item[:c] + q_item[c + 1:]
                    if word_minus_c not in q_dictionary:
                        queue.append(word_minus_c)
                        q_dictionary[word_minus_c] = None  # arbitrary value, just to identify we checked this

        if not silent and self.verbose != 0:
            print("number of possible corrections: %i" % len(suggest_dict))
            print("  edit distance for deletions: %i" % self.max_edit_distance)
        as_list = suggest_dict.items()
        outlist = sorted(as_list, key=lambda x: (x[1][1], -x[1][0]))

        if self.verbose == 0:
            return outlist[0]
        else:
            return outlist
    def best_word(self, s, silent=False):
        try:
            return self.get_suggestions(s, silent)[0]
        except:
            return None

def spell_corrector(word_list, words_d, native) -> str:
    result_list = []
    for word in word_list:
        #start of special block
        if word in native:
            result_list.append(word)
            continue
        #end of special block
        if word not in words_d:
            suggestion = ss.best_word(word, silent=True)
            if suggestion is not None:
                result_list.append(suggestion)
            #added this to original to avoid deletion of word when dictionary lookup is not found under edit distance 2
            else:
                result_list.append(word)
        else:
            result_list.append(word)
    return " ".join(result_list)

if __name__ == '__main__':
    # build symspell tree
    ss = SymSpell(max_edit_distance=2)

    # fetch list of bad words
    #with open('./input/bad-bad-words/bad-words.csv') as bf:
    #    bad_words = bf.readlines()
    #bad_words = [word.strip() for word in bad_words]

    # fetch english words dictionary
    with open('./input/479k-english-words/dictionary1.txt') as f:
        words = f.readlines()
    eng_words = [word.strip() for word in words]
        
    #custom dataset block
    with open('./input/479k-english-words/customdictionary.txt') as f:
        words = f.readlines()
    native = [word.strip() for word in words]
    with open('./input/479k-english-words/indian_names.txt') as f:
        words = f.readlines()
    native += [word.strip() for word in words]
    with open('./input/479k-english-words/indian_cities.txt') as f:
        words = f.readlines()
    native += [word.strip() for word in words]
#    with open('./input/479k-english-words/indian_states.txt') as f:
#        words = f.readlines()
#    native += [word.strip() for word in words]
    with open('./input/479k-english-words/english_names.txt') as f:
        words = f.readlines()
    native += [word.strip() for word in words]
    native = ' '.join(native)
    #print(native)
    native = re.sub('\s+', ' ', native)
    native = native.split(' ')
    native.sort()
    f.close()
    # Print some examples
    print(eng_words[:5])
    print(native[:5])
    #print(bad_words[:5])

    print('Total english words: {}'.format(len(eng_words)))
    #print('Total bad words: {}'.format(len(bad_words)))

    print('create symspell dict...')

    if to_sample:
        # sampling from list for kernel runtime
        sample_idxs = random.sample(range(len(eng_words)), 100)
        eng_words = [eng_words[i] for i in sorted(sample_idxs)] + \
            sample_idxs.split() # make sure our sample misspell is in there
    #attempt to change sample_text to sample _idxs
    #all_words_list = list(set(bad_words + eng_words))
    all_words_list = list(set(eng_words))
    silence = ss.create_dictionary_from_arr(all_words_list, token_pattern=r'.+')

    # create a dictionary of rightly spelled words for lookup
    words_dict = {k: 0 for k in all_words_list}
    exit=0
    '''
    sample_text = 'to infifity and byond'
    print('enter text:')
    sample_text = input()
    '''

    #custom input from text file generated by OCR
    #infile=open('text.txt','r')
    #words = open('text.txt', 'r').read()
    #words = infile.readlines()
    #words = [word.strip() for word in words]
    words=''
    with open('text.txt', 'r') as file:
        words = file.read().replace('\n', ' ')
    print('text read by symspell: '+ words)
    #tokens = spacy_tokenize(sample_text)
    words = words.lower()
    tokens = spacy_tokenize(words)
    #tokens is of type list
    print('run spell checker...')
    print()
    print('original text: ' + words)
    print()
    #added native attb to spell_corrector
    correct_text = spell_corrector(tokens, words_dict, native)
    print('corrected text: ' + correct_text)
    outFile=open('corrected_text.txt', "w")
    outFile.write(correct_text)
    outFile.close()


    print('Done.')
