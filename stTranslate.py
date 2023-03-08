import json
from urllib import parse, request
from collections import OrderedDict

from os.path import dirname, realpath
PLUGINPATH = dirname(realpath(__file__))

__version__ = "1.0.0"

class Translate(object):
    error_codes = {
        501: "ERR_SERVICE_NOT_AVAIBLE_TRY_AGAIN_OR_USE_PROXY",
        503: "ERR_VALUE_ERROR",
        504: "ERR_PROXY_NOT_SPECIFIED",
    }
    def __init__(self, source_lang='auto', target_lang='en', results_mode='insert'):
        self.cache = {
            'languages': None, 
        }
        self.api_urls = {
            'translate': 'https://translate.googleapis.com/translate_a/single?client=gtx', #&ie=UTF-8&oe=UTF-8
        }
        if not source_lang:
            source_lang = 'auto'
        if not target_lang:
            target_lang = 'en'
        if not results_mode in ['insert', 'replace']:
            results_mode = 'insert'    
        self.source = source_lang
        self.target = target_lang
        self.results_mode = results_mode

    @property
    def langs(self, cache=True):
        try:
            if not self.cache['languages'] and cache:
                with open(PLUGINPATH+'/supported_languages.json') as f:
                  _data = f.read()
                _languages = json.loads(_data, object_pairs_hook=OrderedDict)
                print('[Google] translate, supported {0} languages.'.format(len(_languages)))
                self.cache['languages'] = _languages
        except IOError:
            raise GoogleTranslateException(self.error_codes[501])
        except ValueError:
            raise GoogleTranslateException(self.error_codes[503])
        return self.cache['languages']

    def GoogleTranslate(self, text, source_lang='', target_lang=''):
        if not source_lang:
            source_lang = self.source
        if not target_lang:
            target_lang = self.target
        API_URL = self.api_urls['translate']
        _text = parse.quote(text.encode("utf-8"))
        _url  = "{0}&sl={1}&tl={2}&dt=t&q={3}".format(API_URL, source_lang, target_lang, _text)
        # print('GoogleTranslate: sl {0}, tl {1}, url {2}'.format(source_lang, target_lang, _url))
        _data = request.urlopen(_url).read()
        _obj = json.loads(str(_data,'utf-8'))
        result = []
        for s in _obj[0]:
            result.append(s[0])
        return "".join(result)


## Quick translation test ## 
## works outside SublimeText where sublime modules not available 
if __name__ == "__main__":
    translate = Translate('auto', 'en')
    print(translate.GoogleTranslate('Слава Україні!'))
    exit()

## Sublime Plugin specific code
import sublime, sublime_plugin
settings = sublime.load_settings("stTranslate.sublime-settings")

class GoogleTranslateException(object):
    sublime.status_message('Translation error. Check console.')
    def __init__(self, exception):
        print(exception)
        sublime.active_window().run_command("show_panel", {"panel": "console"})

class stTranslateCommand(sublime_plugin.TextCommand):

    def run(self, edit, source_language='', target_language=''):
        settings = sublime.load_settings("stTranslate.sublime-settings")
        if not source_language:
            source_language = settings.get("source_language")
        if not source_language:
            source_language = 'auto'
        if not target_language:
            target_language = settings.get("target_language")

        # print('source_language {0}, target_language {1}'.format(source_language, target_language))

        for region in self.view.sel():
            if not region.empty():

                v = self.view
                selection = v.substr(region)
                # print('selection: {0}'.format(selection))
                translate = Translate(source_language, target_language)

                if not target_language:
                    self.view.run_command("go_translate_to")
                    return                          
                else:
                    result = translate.GoogleTranslate(selection, source_language, target_language)

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


class stTranslateToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("stTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = Translate(source_language, target_language)

        langs = translate.langs
        lkey = []
        ltrasl = []

        for (slug, title) in langs.items():
            lkey.append(slug)
            ltrasl.append(title+' ['+slug+']')

        def on_done(index):
            if index >= 0:
                self.view.run_command("st_translate", {"target_language": lkey[index]})

        self.view.window().show_quick_panel(ltrasl, on_done)

    def is_visible(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False


class stTranslateInfoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("stTranslate.sublime-settings")
        source_language = settings.get("source_language")
        target_language = settings.get("target_language")

        v = self.view
        selection = v.substr(v.sel()[0])

        translate = Translate(source_language, target_language)
        # print(translate.langs)
        text = (json.dumps(translate.langs, ensure_ascii = False, indent = 2))

        print("{0}".format(text)) 
        notification = '[Google] translate, supported {0} languages.'.format(len(translate.langs))
        sublime.status_message('{0} Check console.'.format(notification))
        sublime.active_window().run_command("show_panel", {"panel": "console"})

def plugin_loaded():
    global settings
    settings = sublime.load_settings("stTranslate.sublime-settings")