Translate Plugin for SublimeText 3 & 4
======================================

**Version:** 1.0.0, **[Google] translate**, supported **133** languages.

This plugin uses a standard Google translate page results instead of the Google API. As API key isn't required it makes pluging very easy to use and very quick. However it isn't 100% officially supported, so if Google change their URL schema it could break the plugin.

First version includes Google translate, adding other translators is in development.

🎯 Features:
============

* 133 languages supported 
* SublimeText 3 & 4 supported
* Autodetect of source language
* Ability to specify source & target languages in settings
* Ability to choose the target language in context menu
* Ability to replace selected text with translation or insert translation after it

## How to Use (very easy) ##

1. Select some text in the editor
2. Run **[Google] Translate selected text** command. 
You can do it in 3 ways:
- via hotkey Ctrl+Alt+G (Command+Alt+G in OSX)
- via mouse right-click context menu > [Google] Translate selected text
- via Command Pallet, Ctrl+Shist+P (Command+Shift+P in OSX) > [Google] Translate selected text

### Commands
- **[Google] Translate selected text** - translates selected text baesd on settings
- **[Google] Translate selected to...** - you choose the target language before translation
- **[Google] Translate: Print supported languages to console** - to see available options for changing settings

## 🧰 Settings ##

    {
        "source_language": "",          // If empty will be Auto detected
        "target_language": "en",        // Must be specified    
        "results_mode": "insert",       // "insert" or "replace" 
        "engine": "google"              // "google", soon "alibaba" and some others   
    }

![Translate Plugin for SublimeText](https://github.com/dmytrovoytko/sublimetext-translate)

License:
========

MIT

Credits:
========

Inspired by old "Inline Google Translate" plugin that doesn\'t work anymore.