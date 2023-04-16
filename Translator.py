# Written by Dmytro Voytko (https://github.com/dmytrovoytko)
# Largely inspired by the (outdated) "Inline Google Translate" plugin of MTimer 
#  and Bing translate API https://github.com/plainheart/bing-translate-api by Zhongxiang Wang

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

from os.path import dirname, realpath
PLUGINPATH = dirname(realpath(__file__))

__version__ = "3.0.0"
# + Bing translate engine

DEBUG_TEST = False
try:
    import sublime
except Exception as e:
    # Used for quick translation test outside SublineText before updating the plugin 
    DEBUG_TEST = True

class Translate(object):
    error_codes = {
        501: "ERR_SERVICE_NOT_AVAIBLE_TRY_AGAIN_OR_CHANGE_ENGINE",
        503: "ERR_VALUE_ERROR",
    }
    def __init__(self, engine='', source_lang='', target_lang='en', results_mode='insert'):
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
        if not results_mode in ['insert', 'replace']:
            results_mode = 'insert'    
        self.source = source_lang
        self.target = target_lang
        self.results_mode = results_mode
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
        _data = request.urlopen(_url).read()
        _obj = json.loads(str(_data,'utf-8'))
        result = []
        for s in _obj[0]:
            result.append(s[0])
        return "".join(result)

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
        # it should go here only in case of error
        print("Bing translate response: {}".format(response))
        return response

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
        print(translate.translate(eng_text, 'en', 'zh-Hans'))
    except Exception as e:
        print('GoogleTranslate error: {}'.format(e))
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

    def run(self, edit, source_language='', target_language=''):
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get('engine')
        if not source_language:
            source_language = settings.get("source_language")
        if not target_language:
            target_language = settings.get("target_language")

        # print('engine: {0}, source_language {1}, target_language {2}'.format(engine, source_language, target_language))
        translate = Translate(engine=engine, source_lang=source_language, target_lang=target_language)

        for region in self.view.sel():
            if not region.empty():

                v = self.view
                selection = v.substr(region)
                # print('selection: {0}'.format(selection))

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

                if settings.get('results_mode')=='replace':
                    v.replace(edit, region, result)
                else:
                    v.insert(edit, v.sel()[0].end(), " {0}".format(result)) # insert to current View window
                if not source_language:
                    detected = 'Auto'
                else:
                    detected = source_language
                sublime.status_message(u'Done! (translate '+detected+' --> '+target_language+')')

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False


class translatorToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Translator.sublime-settings")
        engine = settings.get("engine")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")

        v = self.view
        selection = v.substr(v.sel()[0])

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
            if not region.empty():
                return True
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
        notification = 'Translator: [{0}] translate, supported {1} languages.'.format(engine, len(translate.langs))
        sublime.status_message('{0} Check console.'.format(notification))
        sublime.active_window().run_command("show_panel", {"panel": "console"})
    def is_visible(self):
        settings = sublime.load_settings("Translator.sublime-settings")
        if settings.get('engine') in ['google','googlehk','bing']: 
            return True
        # else: TODO process new engines
        return False

def plugin_loaded():
    global settings
    settings = sublime.load_settings("Translator.sublime-settings")
    # engine = settings.get('engine')
    # print('Translator loaded. Current engine: {}'.format(engine))
