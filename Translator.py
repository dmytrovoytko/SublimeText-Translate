# Written by Dmytro Voytko (https://github.com/dmytrovoytko)
# Largely inspired by the (outdated) "Inline Google Translate" plugin of MTimer 
#  and Bing translate API https://github.com/plainheart/bing-translate-api by Zhongxiang Wang
# Used https://github.com/mediacloud/sentence-splitter for text analysis

import json
from urllib import parse, request
from collections import OrderedDict

import os
import re
import sys
import time
import random
import hashlib
import functools
import warnings

import requests

try:
    from .sentence_splitter import SentenceSplitter, split_text_into_sentences
    import regex
    #print("sentence_splitter loaded!")
except Exception as e:
    try:
        from sentence_splitter import SentenceSplitter, split_text_into_sentences
        import regex
        #print("sentence_splitter loaded!")
    except Exception as e:
        print("Module sentence_splitter dependency didn't work! Look's like you need to restart Sublime Text.", e)

from os.path import dirname, realpath
PLUGINPATH = dirname(realpath(__file__))

__version__ = "3.3.0"
# 3.0.0 + Bing translate engine
# 3.0.1 + show_popup option to see translation without changing the text
# 3.0.2 + better error handling (unsuccessful requests)
# 3.1.0 + translation of the current word (without selection); 
#       + new results_mode "to_buffer" (to clipboard)
# 3.2.0 + new command - translate clipboard
#       + ability to replace line breaks inside text while translating (with space, comma, etc)
# 3.3.0 + text statistics and readability checks
#       + improved behaviour while inserting translation from clipboard without selection

REGIONS_ON = False
DEBUG_TEST = False
try:
    import sublime
except Exception as e:
    # Used for quick translation test outside SublineText before updating the plugin 
    DEBUG_TEST = True

class TextAnalysis():
    def __init__(self, language='en', tokenization='simple'):
        self.special_characters = ['!','"','#','$','%','&','(',')','*','+','/',':',';',
                                    '<','=','>','@','[','\\',']','^','`','{','|','}','~','\t']

        self.language = language
        # self.vowels = 'аоиеёэыуюя'+'aeiouy' # 'aeiouy'
        if self.language == 'en':
            self.vowels = 'aeiouy'
        elif self.language == 'uk':
            self.vowels = 'аеиоуяюєії'+'ёэы'+'aeiouy' # extended with russian and english
        elif self.language == 'ru':
            self.vowels = 'аеиоуяюёэы'+'aeiouy'
        print('\n\nText Analysis:', self.language, '' if DEBUG_TEST==False else self.vowels)

    def clean_text(self, text):
        """
        Removes Non-ASCII characters from text.
        """
        return str(text.encode().decode("utf-8", errors="ignore")) # ascii

    def sent_tokenize(self, text):
        #return text.split('. ')
        splitter = SentenceSplitter(language=self.language)
        sentences = splitter.split(text=text)
        #print(sentences)
        return sentences

    def word_tokenize(self, text):
        return text.split(' ')

    def para_tokenize(self, text):
        return text.split('\n\n')

    def count_syllables(self, word): #syllable_count
        # dictionary = pyphen.Pyphen(lang="en_US")
        # hyphenated = dictionary.inserted(word)
        # return len(hyphenated.split("-"))
        
        # from nltk.corpus import cmudict
        # d = cmudict.dict()
        # return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]]        
        
        #referred from stackoverflow.com/questions/14541303/count-the-number-of-syllables-in-a-word
        count = 0
        vowels = self.vowels # 'aeiouy'
        word = word.lower()

        if self.language=='en':
            if word[0] in vowels:
                count +=1
            for index in range(1,len(word)):
                if word[index] in vowels and word[index-1] not in vowels:
                    count +=1
            if word.endswith('e'):
                count -= 1
            if word.endswith('le'):
                count += 1
                # ? while 2
                # ,.!?) may influence - clean
                # — 1
                # behavior. 3 - 4!
                # well-being, 2 - 3!
                # influencing, 3 - 4!
                # individual 4 - 5!
                # realizes 3 - 4!
                # life, 2 - 1!
                #
        elif self.language in ['uk', 'ru']:
            for index in range(0,len(word)):
                if word[index] in vowels:
                    count += 1

        if count == 0:
            count += 1
        pattern = '[A-Za-zА-Яа-яєіїґё`\']'
        lett_count = len(re.findall(pattern, word))
        #print(word, count, lett_count)
        return count

    def remove_special_characters(self, text):
        for i in self.special_characters: 
            text = text.replace(i, '')
        return text

    def calculate_statistics(self, text, debug=False): # compute_counts(text):
        """
        Tokenize and Calculate Word count, Sentence count and Syllables count for scores like Flesch-Kincaid 
        """

        def paragraph_length_check(paragraphs, debug=False):
            # Paragraph length check: (below 150 - green) (150-200 - yellow) (>200 - red)

            # TODO Should be using the same trim/replaces as main loop in calculate_statistics
            LONG_PARAGRAPH_THRESHOLD1 = 150 # words
            LONG_PARAGRAPH_THRESHOLD2 = 200 # words 
            punctuation = ".,!?/-—–[]{}()<>'\"`@#*+"
            p_warnings = ""
            word_count = 0
            _ = 0
            for paragraph in paragraphs:
                _ += 1
                _paragraph = re.sub(r"\s+", " ", paragraph)
                words = self.word_tokenize(_paragraph)
                _word_count = 0 # len(words)
                for _word in words:
                    if _word not in punctuation:
                        _word_count += 1
                if debug:
                    print('Paragraph\'s words:', words, 'Word count:', _word_count)
                word_count += _word_count
                if _word_count>LONG_PARAGRAPH_THRESHOLD2:
                    p_warnings += " ‼️ Paragraph {} is longer than {} words ({}). It should be corrected!\n".format(_,LONG_PARAGRAPH_THRESHOLD2, _word_count) 
                elif _word_count>LONG_PARAGRAPH_THRESHOLD1:
                    p_warnings += " ❗️ Paragraph {} is longer than {} words ({}).\n".format(_,LONG_PARAGRAPH_THRESHOLD1, _word_count) # Pay attention.
            if p_warnings=="":
                # if True: #debug:
                #     print('Paragraphs:', para_count, 'Word count:', word_count)
                p_warnings = " Max Paragraph length is OK (<{} words, avg. {}/{} = {} words/par).\n".format(LONG_PARAGRAPH_THRESHOLD1, word_count,para_count,round(word_count/para_count, 2)) # {} {} , 

            return p_warnings

        def sentence_length_check(sentences, debug=False):
            # Sentences length check
            LONG_SENTENCE_LENGTH = 20 
            LONG_SENTENCE_THRESHOLD = 0.25
            s_warnings = ""
            sent_count = len(sentences)
            # if debug:
            #     print('check', _text, sent_count, sentences)
            if sent_count == 0:
                return "", [], []
            long_sentences_count = 0
            long_sentences = []
            long_sentences_len = []
            word_count = 0
            for sentence in sentences:
                words = self.word_tokenize(sentence)
                word_count += len(words)
                if len(words)>LONG_SENTENCE_LENGTH:
                    long_sentences_count += 1
                    long_sentences.append(sentence)
                    long_sentences_len.append(len(words))
            long_sentences_ratio = long_sentences_count/sent_count
            word_sentences_ratio = word_count/sent_count 
            s_warnings = " {}% of sentences are longer than {} words. Average sentence length is {} words.\n".format(round(long_sentences_ratio*100,2),LONG_SENTENCE_LENGTH, round(word_sentences_ratio,2)) 
            if long_sentences_ratio > LONG_SENTENCE_THRESHOLD:
                if debug:
                    print(s_warnings)
                    print('\n '.join(long_sentences))     
                s_warnings = " ‼️" + s_warnings
                return s_warnings, long_sentences, long_sentences_len
            else:
                s_warnings = " Sentence length looks OK. Only" + s_warnings
                return s_warnings, [], []

        stats = {'total_paragraphs': 0,
                 'total_sentences': 0,
                 'total_words': 0,
                 'total_syllables': 0,
                 'total_letters': 0
                 }
        check = {'need_attention_p': "",
                 'need_attention_s': "",
                 'long_sentences': [],
                 'long_sentences_words': [],
                 }
        """
        Calculate Word count, Sentence count and recommended Sentence/Paragraph length 
        Annotations could be added by lines, or by paragraphs
        """
        ## replacing multiple spaces (' ', '\t', '\n') with 1 space
        ## _text = re.sub(r"\s+", " ", text)
        # replacing multiple spaces (' ', '\t') + '\n' with 1 space, but not '\n\n' - it's a paragraph break
        _text = re.sub(r"\n[\s]*\n", "\n\n", text)
        paragraphs = self.para_tokenize(_text)
        para_count = len(paragraphs)
        if debug:
            print('Paragraphs:', para_count)
        if para_count == 0:
            return stats, []
        p_warnings = paragraph_length_check(paragraphs, debug)

        _text = re.sub(r"[ \t]+", " ", _text)
        _text = re.sub(r"(\w)\n(\w)", "\\1 \\2", _text) # sentence w/o ',' followed by new line with word = 1 sentence 
        _text = re.sub(r"[\n]+[\s]*", "\n", _text)
        #print('->', _text)
        sentences = self.sent_tokenize(_text)
        #print('->', sentences)
        sent_count = len(sentences)
        if sent_count == 0:
            return stats, check, []
        # print(sent_count, sentences)

        s_warnings, long_sentences, long_sentences_len = sentence_length_check(sentences, debug)

        check = {'need_attention_p': p_warnings,
                 'need_attention_s': s_warnings,
                 'long_sentences': long_sentences,
                 'long_sentences_words': long_sentences_len,
                 }

        words = [self.word_tokenize(sentence) for sentence in sentences]
        punctuation = ".,!?/-—–[]{}()<>'\"`@#*+"
        sybl_count = 0
        word_count = 0
        pattern = '[A-Za-zА-Яа-яєіїґё`\'-]'
        lett_count = 0 #len(re.findall(pattern, text))
        trim_punctuation1 = "^[!\"#\$\%\&'()\*\+,\-\—\–/:;\<=\>\?\@\[\]\\\^\_`{}|~«»]+"
        trim_punctuation2 = "[!\"#\$\%\&'()\*\+.,\-\—\–/:;\<=\>\?\@\[\]\\\^\_`{}|~«»]+$"
        # special cases to keep and count '.' at the end
        prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)[.]"
        acronyms2 = "^([A-Z][.])([A-Z])[.]$"
        acronyms3 = "^([A-Z][.])([A-Z][.])([A-Z])[.]$"

        for word_list in words:
            for word in word_list:
                _word = re.sub(trim_punctuation1, '', word)
                # TODO TEST check also Mr. Ms. etc & Inc. Ltd. etc
                _word = re.sub(prefixes,"\\1<PRD>",_word)
                _word = re.sub(suffixes,"\\1<PRD>",_word)
                _word = re.sub(acronyms2,"\\1\\2<PRD>",_word)
                _word = re.sub(acronyms3,"\\1\\2\\3<PRD>",_word)
                if _word[-5:]=="<PRD>":
                    _word = _word.replace("<PRD>",".")
                else:
                    _word = re.sub(trim_punctuation2, '', _word)
                    if _word[-4:]=="<PRD": # last '>' trimmed
                        _word = _word.replace("<PRD",".")
                if debug:
                    print(' word `{}` -> `{}`'.format(word, _word))
                if _word not in punctuation:
                    word_count += 1
                    lett_count += len(_word)
                    x = self.count_syllables(_word)
                    sybl_count += x
        stats = {'total_paragraphs': para_count,
                 'total_sentences': sent_count,
                 'total_words': word_count,
                 'total_syllables': sybl_count,
                 'total_letters': lett_count
                 }
        if debug:
            print(' -> Sentences:', sent_count, '\tWords:', word_count, '\tSyllables:', sybl_count, '\tLetters:', lett_count, words)
        return stats, check, sentences

    def ARI_score(self, total_letters, total_words, total_sentences):
        """ Automated Readability Index (ARI) Score 
        https://en.wikipedia.org/wiki/Automated_readability_index
        """
        if total_words == 0 or total_sentences == 0: 
            return 0
        ARI_X_en = 4.71
        ARI_Y_en = 0.5
        ARI_Z_en = 21.43
        if True: #self.language == 'en':
            ARI_X = ARI_X_en
            ARI_Y = ARI_Y_en
            ARI_Z = ARI_Z_en
        elif self.language in ['uk', 'ru']:
            ARI_X = 6.26   #ARI_X_en
            ARI_Y = 0.2805 #ARI_Y_en
            ARI_Z = 31.04  #ARI_Z_en

        ari_score = ARI_X * (float(total_letters) / total_words) + ARI_Y * (float(total_words) / total_sentences) - ARI_Z
        #print(total_letters, total_words, total_sentences, ari_score)
        return ari_score

    def Coleman_Liau_index_score(self, total_letters, total_words, total_sentences):
        """ Coleman-Liau Index 
        https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index
        """
        if total_words == 0: 
            return 0
        CLI_X_en = 0.0588
        CLI_Y_en = 0.296
        CLI_Z_en = 15.8
        if True: #self.language == 'en':
            CLI_X = CLI_X_en
            CLI_Y = CLI_Y_en
            CLI_Z = CLI_Z_en
        elif self.language in ['uk', 'ru']:
            CLI_X = 0.055 #CLI_X_en
            CLI_Y = 0.35  #CLI_Y_en
            CLI_Z = 20.33 #CLI_Z_en

        cli_score = CLI_X * (float(total_letters) *100 / total_words) - CLI_Y * (float(total_sentences) *100 / total_words) - CLI_Z
        #print(total_letters, total_words, total_sentences, cli_score)
        return cli_score

    def Flesch_Kincaid_grade_level_score(self, total_sentences, total_words, total_syllables):
        """ Flesch-Kincaid Grade Level Score """
        if self.language == 'en':
            grade_level_score = (0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words)) - 15.59
        elif self.language in ['uk', 'ru']:
            grade_level_score = (0.49 * (total_words / total_sentences) + 7.3 * (total_syllables / total_words)) - 16.59
        return grade_level_score


    def Flesch_Kincaid_readability_score(self, total_sentences, total_words, total_syllables):
        """ Flesch Reading Ease Score Test (FRES)
        https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_Reading_Ease
        """
        if self.language == 'en':
            fres = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        elif self.language in ['uk', 'ru']:
            fres = 220.755 - 1.315 * (total_words / total_sentences) - 50.1 * (total_syllables / total_words)
            # Yoast for ru
            #fres = 206.835 - 1.3 * (total_words / total_sentences) - 60.1 * (total_syllables / total_words)
        if fres <= 10:
            remark = "Extremely difficult to read. Best understood by university graduates."
        elif 10 < fres <= 30:
            remark = "Very difficult to read. Best understood by university graduates. "
        elif 30 < fres <= 50:
            remark = "Difficult to read. "
        elif 50 < fres <= 60:
            remark = "Fairly difficult to read. "
        elif 60 < fres <= 70:
            remark = "Plain English. Easily understood by 13 to 15-year-old students."
        elif 70 < fres <= 80:
            remark = "Fairly easy to read. "
        elif 80 < fres <= 90:
            remark = "Easy to read, Conversational English. "
        elif 90 < fres <= 100:
            remark = "Very easy to read. Easily understood by an average 11-year-old student. "
        elif fres > 100:
            remark = "Very easy to read."

        return fres, remark

    def  calculate_scores(self, input_text, debug=False): # compute_score
        # Process Input.
        clean_input = self.clean_text(input_text)

        # Stats
        stats, check, sentences = self.calculate_statistics(clean_input, debug)
        total_sentences = stats['total_sentences']
        total_words = stats['total_words']
        total_syllables = stats['total_syllables']
        total_letters = stats['total_letters']

        scores = {'ari_score': 0,
                  'cli_score': 0,
                  'fres': 0,
                  'remark': "",
                  'grade_score': 0}

        #return scores, stats

        # Readability Tests.
        fres, remark_computed = self.Flesch_Kincaid_readability_score(total_sentences, total_words, total_syllables)
        grade_score = self.Flesch_Kincaid_grade_level_score(total_sentences, total_words, total_syllables)
        ari_score = self.ARI_score(total_letters, total_words, total_sentences)
        cli_score = self.Coleman_Liau_index_score(total_letters, total_words, total_sentences)
        if debug:
            print('Sentences:',total_sentences, '\tWords:',total_words, '\tSyllables:',total_syllables, '\tLetters:',total_letters)
            print('Automated Readability Index:',round(ari_score,2), 'Coleman-Liau Index:',round(cli_score,2), 'FRES:',round(fres,2), 'FR Grade:',round(grade_score,2))
            # print('\n  '.join(sentences))

        if fres <= 60:
            # check which sentences need attention
            if debug:
                print('\nSentence(s) to pay attention:\n')
            for s in sentences:
                _stats, _check, _sentences = self.calculate_statistics(s) #, debug=debug
                _total_sentences = _stats['total_sentences']
                _total_words = _stats['total_words']
                _total_syllables = _stats['total_syllables']
                _total_letters = _stats['total_letters']
                _fres, _remark_computed = self.Flesch_Kincaid_readability_score(_total_sentences, _total_words, _total_syllables)
                _grade_score = self.Flesch_Kincaid_grade_level_score(_total_sentences, _total_words, _total_syllables)
                _ari_score = self.ARI_score(_total_letters, _total_words, _total_sentences)
                _cli_score = self.Coleman_Liau_index_score(_total_letters, _total_words, _total_sentences)
                if _fres <= 60:
                    if debug:
                        print(_total_words, _total_syllables, _total_letters, round(_ari_score,2), round(_cli_score,2), round(_fres,2), round(_grade_score,2), s)
        else:
            if debug:
                print('Overall FRES is good! (>=60)')

        # Fixing Negative Grade Scores.
        if grade_score < 0:
            grade_score = 0

        # Response.
        scores = {'ari_score': round(ari_score,2),
                  'cli_score': round(cli_score,2),
                  'fres': round(fres, 2),
                  'remark': remark_computed,
                  'grade_score': round(grade_score, 2)}

        return scores, stats

class Translate(object):
    error_codes = {
        501: "ERR_SERVICE_NOT_AVAIBLE_TRY_AGAIN_OR_CHANGE_ENGINE",
        503: "ERR_VALUE_ERROR",
    }
    def __init__(self, engine='', source_lang='', target_lang='en', results_mode='insert', show_popup=False):
        self.cache = {
            'languages': None, 
        }
        self.api_urls = {
            'google':   'https://translate.googleapis.com/translate_a/single?client=gtx', #&ie=UTF-8&oe=UTF-8
            'googlehk': 'https://translate.google.com.hk/translate_a/single?client=gtx', #&ie=UTF-8&oe=UTF-8
            'bing':     'https://www.bing.com/ttranslatev3?isVertical=1', 
        }

        if not engine in ['google', 'googlehk', 'bing']:
            engine = 'google'
        self.engine = engine
        if not source_lang:
            if engine in ['google', 'googlehk']:
                source_lang = 'auto'
            elif engine == 'bing':
                source_lang = 'auto-detect'
            else: # TODO process autodetect/default for new engines
                source_lang = 'auto'
        if not target_lang:
            target_lang = 'en'
        if not results_mode in ['insert', 'replace', 'to_buffer']:
            results_mode = 'insert'    
        if not show_popup in [False, True]:
            show_popup = False    
        self.source = source_lang
        self.target = target_lang
        self.results_mode = results_mode
        self.show_popup = show_popup
        # extra initializations
        if engine=='bing':
            self.session = self._get_bing_session()

    @property
    def langs(self, cache=True):
        try:
            if not self.cache['languages'] and cache:
                # TODO Update engine related languages list
                if self.engine in ['google', 'googlehk']:
                    if DEBUG_TEST: # outside Sublime
                        with open(PLUGINPATH+'/google_languages.json') as f:
                          _data = f.read()
                    else: # inside Sublime
                        _locations = sublime.find_resources('google_languages.json')
                        if _locations:
                            _data = sublime.load_resource(_locations[0])                    
                    _languages = json.loads(_data, object_pairs_hook=OrderedDict)
                elif self.engine == 'bing':
                    if DEBUG_TEST: # outside Sublime
                        with open(PLUGINPATH+'/bing_languages.json') as f:
                          _data = f.read()
                    else: # inside Sublime
                        _locations = sublime.find_resources('bing_languages.json')
                        if _locations:
                            _data = sublime.load_resource(_locations[0])                    
                    _languages = json.loads(_data, object_pairs_hook=OrderedDict)
                else:
                    _languages = ['Please, check engine website.']
                print('[{0}] translate, supported {1} languages.'.format(self.engine, len(_languages)))
                self.cache['languages'] = _languages
        except IOError:
            raise TranslatorError(self.error_codes[501])
        except ValueError:
            raise TranslatorError(self.error_codes[503])
        return self.cache['languages']

    def GoogleTranslate(self, text, source_lang='', target_lang=''):
        if not source_lang:
            source_lang = self.source
        if not target_lang:
            target_lang = self.target
        API_URL = self.api_urls[self.engine]
        _text = parse.quote(text.encode("utf-8"))
        _url  = "{0}&sl={1}&tl={2}&dt=t&q={3}".format(API_URL, source_lang, target_lang, _text)
        # print('GoogleTranslate: sl {0}, tl {1}, url {2}'.format(source_lang, target_lang, _url))
        try:
            _data = request.urlopen(_url).read()
            _obj = json.loads(str(_data,'utf-8'))
            result = []
            for s in _obj[0]:
                result.append(s[0])
            return "".join(result)
        except Exception as e:
            print("Google translate error: {}".format(e))
            return 'Google translate error'

    # BingTranslator:
    # https://www.microsoft.com/en-us/translator/languages/
    def _get_bing_session(self):
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Referer': 'https://www.bing.com/translator'
        }
        session.headers.update(headers)
        _response = session.get('https://www.bing.com/translator')
        _pattern = re.compile(r'params_AbusePreventionHelper\s*=\s*(\[.*?\]);', re.DOTALL)
        _match = _pattern.search(_response.text)
        if _match:
            _params = _match.group(1)
            key, token, time = [p.strip('"').replace('[', '').replace(']', '') for p in _params.split(',')]
            session.headers.update({'key': key, 'token': token})
        _match = re.search(r'IG:"(\w+)"', _response.text)
        if _match:
            ig_value = _match.group(1)
            session.headers.update({'IG': ig_value})
        return session

    def BingTranslate(self, text, source_lang='', target_lang=''):
        if not source_lang:
            source_lang = self.source
        if not target_lang:
            target_lang = self.target
        API_URL = self.api_urls[self.engine]
        # TODO cut to 1000?
        _text = text.encode("utf-8")
        _url  = "{0}&IG={1}&IID=translator.{2}.{3}".format(API_URL, self.session.headers.get("IG"), random.randint(5019, 5026), random.randint(1, 3))
        _data = {'': '', 'fromLang': source_lang, 'to': target_lang, 'text': _text, 'token': self.session.headers.get('token'), 'key': self.session.headers.get('key')}
        try:
            response = self.session.post(_url, data=_data).json()
            if type(response) is dict:
                if 'ShowCaptcha' in response.keys():
                    self.session = self._get_bing_session()
                    return self.BingTranslate(_text, source_lang, target_lang)
                elif 'statusCode' in response.keys():
                    if response['statusCode'] == 400:
                        response['errorMessage'] = '1000 characters limit! You send {} characters.'.format(len(_text))
                else:
                    return response['translations'][0]['text']
            else:
                return response[0]['translations'][0]['text']
        except Exception as e:
            print("Bing translate error: {}".format(e))
            return 'Bing translate error'

    def translate(self, text, source_lang='', target_lang=''):
        if self.engine in ['google', 'googlehk']:
            return self.GoogleTranslate(text, source_lang, target_lang)
        elif self.engine == 'bing':
            return self.BingTranslate(text, source_lang, target_lang)
        else: # TODO update with new engines
            return "[{}] is not supported yet. Change engine in settings.".format(self.engine)

## Quick translation test 
## works outside SublimeText where sublime modules not available 
if __name__ == "__main__":

    test_text = """Hey aaa@bbb.com! Can you do me a quick favor?
                If you get this cheat sheet after clicking on the download button, respond to this email with the words "Got the cheat sheet!" 
                That's how I know things are working fine here.
                Talk to you soon!
                P.S. If you have any questions, feel free to ask me on LinkedIn, Twitter, or Discord (those are the places where I'm more active)."""
    analysis = TextAnalysis()
    print('Example #1')
    print(analysis.calculate_scores(test_text, debug=DEBUG_TEST))
    # exit()

    try:
        print('\nGoogle translate test')
        translate = Translate('google', 'uk', 'en')
        langs = translate.langs
        print(translate.translate('Слава Україні!'))

        print('\nGoogle translate HK test')
        translate = Translate('googlehk', 'uk', 'en')
        langs = translate.langs
        print(translate.translate('Слава Україні!'))
    except Exception as e:
        print('GoogleTranslate error: {}'.format(e))

    try:
        print('\nBing translation test')
        translate = Translate('bing', 'uk', 'en')
        langs = translate.langs
        print(translate.translate('Слава Україні!'))
    except Exception as e:
        print('BingTranslate error: {}'.format(e))

    print('\nChinese translation test...')
    wyw_text = '季姬寂，集鸡，鸡即棘鸡。棘鸡饥叽，季姬及箕稷济鸡。'
    eng_text = '7 most powerful benefits of journaling.'
    try:
        translate = Translate('googlehk', '', 'uk')
        print(translate.translate(wyw_text))
        print(translate.translate(eng_text, 'en', 'zh-CN'))
    except Exception as e:
        print('GoogleTranslate error: {}'.format(e))
    try:
        translate = Translate('bing', '', 'uk')
        print(translate.translate(wyw_text))
        print(translate.translate(eng_text, 'en', 'zh-Hans'))
    except Exception as e:
        print('BingTranslate error: {}'.format(e))
    # exit to prevent Sublime Plugin specific code errors - it works only inside Sublime
    exit()

## Sublime Plugin specific code
import sublime, sublime_plugin
settings = sublime.load_settings("Translator.sublime-settings")

class TranslatorError(Exception):
    sublime.status_message('Translation error. Check console.')
    def __init__(self, exception):
        _e = str(exception)[:200].split("\n")[0]
        print('---\nTranslator error: {}\n---'.format(_e))
        sublime.active_window().run_command("show_panel", {"panel": "console"})

class translatorCommand(sublime_plugin.TextCommand):

    def run(self, edit, source_language='', target_language='', source_text=''):
        #print('st: '+source_text)
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get('engine')
        if not source_language:
            source_language = settings.get("source_language")
        if not target_language:
            target_language = settings.get("target_language")

        # print('engine: {0}, source_language {1}, target_language {2}'.format(engine, source_language, target_language))
        translate = Translate(engine=engine, source_lang=source_language, target_lang=target_language)

        v = self.view
        for region in self.view.sel():
            if source_text=='buffer':
                selection = sublime.get_clipboard(10000).strip() # limit to prevent issues
                #print('cl selection: {0} {1}'.format(selection, region))
            elif not region.empty(): # some text selected
                selection = v.substr(region)
                #print('selection: {0}'.format(selection))
            elif not self.view.word(region).empty(): # current word as selection
                selection = v.substr(self.view.word(region))
                #print('w selection: {0}'.format(selection))
            else:
                selection = ''

            if len(selection):
                if settings.get("replace_linebreaks", False):
                    replacement = settings.get("linebreak_replacement", ' ')
                    selection = selection.replace('"\n"', replacement)
                    selection = selection.replace('\n', replacement)
                    #print(selection)
                if not target_language:
                    self.view.run_command("translator_to")
                    return                          
                else:
                    # result = translate.GoogleTranslate(selection, source_language, target_language)
                    if engine in ['google','googlehk','bing']: 
                        result = translate.translate(selection, source_language, target_language)
                    # else: TODO process new engines
                    #     tss = TranslatorsServer()
                    #     # print("Available engines: {}\nCurrent engine: {}".format(tss.translators_pool, engine))
                    #     result = tss.translate_text(selection, translator=engine, from_language=source_language, to_language=target_language)

                # print('result: {0}'.format(result))
                results_mode = settings.get('results_mode')
                if settings.get('show_popup')==True:
                    # TODO ?limit result length?
                    confirmation = sublime.ok_cancel_dialog(result, results_mode.upper())
                    if not confirmation:
                        continue

                if results_mode=='replace':
                    if not region.empty(): # selected text
                        v.replace(edit, region, result)
                    else: # current word
                        _word = v.substr(v.word(region))
                        #print('w selection: ->{0}<-'.format(_word))
                        if _word.strip()=='': 
                            _shift = 0 if len(_word)==0 else 1
                            v.insert(edit, v.word(region).begin()+_shift, "{0}".format(result)) # insert to current View window
                        elif _word[:2] in ['""','" ',"''","' ",'<>','< ','()','( ','[]','[ ','{}','{ ']: #  and source_text=='buffer' 
                            # let's put translation inside the quotes/brackets/etc
                            v.insert(edit, v.word(region).begin()+1, "{0}".format(result)) # insert to current View window
                        else:
                            pos = (v.word(region)).begin() # beginning of current word
                            v.replace(edit, v.word(region), result)
                            v.sel().clear()
                            v.sel().add(sublime.Region(pos)) # move cursor at the beginning of word
                elif results_mode=='insert':
                    if not region.empty(): # selected text
                        v.insert(edit, v.sel()[0].end(), " {0}".format(result)) # insert to current View window
                    else: # current word
                        #print('w selection: {0}'.format(v.substr(v.word(region))))
                        if v.substr(v.word(region))[:2] in ['""','" ',"''","' ",'<>','< ','()','( ','[]','[ ','{}','{ ']: 
                            # let's put translation inside the quotes/brackets/etc
                            v.insert(edit, v.word(region).begin()+1, "{0}".format(result)) # insert to current View window
                        else:
                            # insert after
                            v.insert(edit, v.word(region).end(), " {0}".format(result)) # insert to current View window
                else: # 'to_buffer'
                    sublime.set_clipboard(result)

                if not source_language:
                    detected = 'Auto'
                else:
                    detected = source_language
                sublime.status_message(u'Done! (translate '+detected+' --> '+target_language+' --> '+results_mode+')')

    def is_visible(self):
        for region in self.view.sel():
            if not self.view.word(region).empty(): #region.empty():
                return True
        return False


class translatorToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get("engine")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        translate = Translate(engine, source_language, target_language)

        langs = translate.langs
        lkey = []
        ltrasl = []

        for (slug, title) in langs.items():
            lkey.append(slug)
            ltrasl.append(title+' ['+slug+']')

        def on_done(index):
            if index >= 0:
                self.view.run_command("translator", {"target_language": lkey[index]})

        self.view.window().show_quick_panel(ltrasl, on_done)

    def is_visible(self):
        for region in self.view.sel():
            if not self.view.word(region).empty(): #region.empty():
                return True
        return False


class translatorFromBufferCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get("engine")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")
        translate = Translate(engine, source_language, target_language)

        # def on_done(buffer):
        #     #print('translatorFromBufferCommand on_done')
        #     if len(buffer):
        #         #print('translatorFromBufferCommand executing')
        #         print('cl: '+buffer)
        #         self.view.run_command("translator", {"source_text": 'buffer'}) # doesn't call ?!
        #     else:
        #         print('Clipboard size is too big (>10000). Please select shorter text.')

        buffer = sublime.get_clipboard(10000) #_async(on_done, 10000)
        if len(buffer):
            self.view.run_command("translator", {"source_text": 'buffer'})
        else:
            notification = 'Clipboard size is too big (>10000). Please select shorter text.'
            sublime.status_message('ERROR! Check console: {0}'.format(notification))
            print(notification)

    def is_visible(self):
        settings = sublime.load_settings("Translator.sublime-settings")
        if settings.get('engine') in ['google','googlehk','bing']: 
            return True
        # else: TODO process new engines
        return False


class translatorInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get("engine")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = Translate(engine, source_language, target_language)
        # print(translate.langs)
        text = (json.dumps(translate.langs, ensure_ascii = False, indent = 2))

        print("{0}".format(text)) 
        notification = 'Translator {0}: [{1}] translate, supported {2} languages.'.format(__version__, engine, len(translate.langs))
        sublime.status_message('{0} Check console.'.format(notification))
        sublime.active_window().run_command("show_panel", {"panel": "console"})
        
    def is_visible(self):
        settings = sublime.load_settings("Translator.sublime-settings")
        if settings.get('engine') in ['google','googlehk','bing']: 
            return True
        # else: TODO process new engines
        return False

class translatorTextAnalysisCommand(sublime_plugin.TextCommand):

    def run(self, edit, source_text=''):

        def add_highlight_region(region_key, regions, annotation): #problem
            vw = self.view
            highlight_scope = "region.yellowish" # "region.redish" "region.orangish" "region.yellowish"
            gutter_icon = "circle" # Standard icon names are "dot", "circle"` and ``"bookmark"

            self.view.add_regions(region_key, regions, highlight_scope, gutter_icon,
                                  sublime.DRAW_STIPPLED_UNDERLINE)
            global REGIONS_ON
            REGIONS_ON = True

        settings = sublime.load_settings("Translator.sublime-settings")
        language = settings.get('analysis_language', 'en')

        analysis = TextAnalysis(language)
        notification = ''

        v = self.view
        for region in self.view.sel():
            if source_text=='buffer':
                selection = sublime.get_clipboard(10000).strip() # limit to prevent issues
                #print('cl selection: {0}'.format(selection))
            elif not region.empty(): # some text selected
                selection = v.substr(region)
                #print('selection: {0}'.format(selection))
            else:
                selection = ''

            _region_key = 'TextAnalysis'
            v.erase_regions(_region_key)
            global REGIONS_ON
            REGIONS_ON = False

            if len(selection):
                # READABILITY checks by paragraph & sentence length
                stats, check, sentences = analysis.calculate_statistics(selection) # , debug=True
                need_attention = check['need_attention_p']+check['need_attention_s']
                fragments = check['long_sentences']
                words = check['long_sentences_words']
                #print("\n\nAnalyze readability:\n", need_attention)
                if len(fragments):
                    #print('->>>', fragments)
                    need_attention += "\n {} sentence(s) to pay attention to:".format(len(fragments))
                    _ = 0
                    # TODO: break it into paragraphs -> check p.length and annotate 
                    _regions = []
                    for fragment in fragments:
                        _region = v.find(fragment, region.begin())
                        _pos = selection.find(fragment)
                        _words = words[_]
                        _ += 1
                        if True: #debug:
                            #print("found:", _pos, offset, _region, fragment)
                            need_attention += "\n {0:3d}: {1} [{2}w]".format(_, fragment, _words)
                        if _pos<0: # shouldn't be, just in case
                            # TODO FIX it cannot be found if fragment was transformed while sent_tokenize, for example double spaces
                            _pos = selection.find(fragment[:25]) # dirty fix
                            if _pos<0:
                                #print('Not found!', fragment)
                                continue
                        offset = region.begin()+_pos
                        length = len(fragment)
                        _regions.append(sublime.Region(offset, offset + length))
                    if _regions:
                        add_highlight_region(_region_key, _regions, "Length is >20 words") # +str(offset) "Length is >20 ({})".format(_words)
                        #print(v.get_regions(_region_key))

                scores, stats = analysis.calculate_scores(selection)
                # 'total_syllables': total_syllables,
                notification = "\nStatistics: {0} paragraph(s), {1} sentence(s), {2} words, {3} letters.".format(stats['total_paragraphs'], stats['total_sentences'], stats['total_words'], stats['total_letters'])

                notification += "\nAutomated Readability Index {0}, Coleman-Liau Index {1}".format(scores['ari_score'], scores['cli_score'])
                # notification += "\n FRES {0}: {1}".format(scores['fres'], scores['remark'])

                notification += "\n\nText Readability analysis:\n{}".format(need_attention)

        sublime.status_message('{0} // Check console.'.format(notification))
        print(notification)
        sublime.active_window().run_command("show_panel", {"panel": "console"})

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

class translatorClearAnalysisCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = sublime.active_window().active_view() #view
        _region_key = 'TextAnalysis'
        try:
            v.erase_regions(_region_key)
            v.sel().clear()
        except:
            pass
        global REGIONS_ON
        REGIONS_ON = False

    def is_visible(self):
        return REGIONS_ON

def plugin_loaded():
    global settings
    settings = sublime.load_settings("Translator.sublime-settings")
    # engine = settings.get('engine')
    # print('Translator loaded. Current engine: {}'.format(engine))
