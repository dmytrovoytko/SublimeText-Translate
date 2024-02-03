[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://stand-with-ukraine.pp.ua)
[![Support Ukraine](https://img.shields.io/badge/Support-Ukraine-FFD500?style=flat&labelColor=005BBB)](https://war.ukraine.ua/support-ukraine/) [![Downloads](https://img.shields.io/packagecontrol/dt/Translator)](https://packagecontrol.io/packages/Translator) ![Maintenance](https://img.shields.io/maintenance/yes/2023?style=flat-square)


Translator Plugin (multi-engine) for SublimeText 3/4
====================================================

**Version:** 3.3.1, **[Google] & [Bing] translate**, supported **133+** languages.

This plugin uses a standard Google/Bing translate page results. It works fast! And as API keys are not required it makes plugin very easy to use. However it isn't 100% officially supported, so if Google/Bing change their URL schema it could break the plugin.

This version includes Google & Bing translate, text readability analysis and statistics.

🎯 Features:
------------

* 133+ languages supported 
* SublimeText 3 & 4 supported
* Autodetect of source language
* Ability to specify source & target languages in settings
* Ability to choose the target language in context menu
* 3 work modes: 
    - **replace** selected text with translation, 
    - **insert** translation after it (default)
    - **to_buffer** - translation goes to clipboard (without changing the text)
* Ability to show translation in popup without changing original text
* Ability to translate your clipboard / current word if no text selected
* Ability to replace line breaks inside text while translating (with space, comma, etc), useful to translate .po files
* Ability to analyze text readability and statistics (including Automated Readability Index, Coleman-Liau Index) to improve your documentation or SEO texts.

## 🚀 How to Use (easy)

1. Select some text in the editor
2. Run **Translate selected text** command. 
You can do it in 3 ways:
- via binding and using hotkey **Ctrl+Alt+G** (⌘Cmd+Alt+G in OSX)
- via `Tools ➡️ Translator ➡️ Translate seclected text`
- via Command Pallet, Ctrl+Shift+P (⌘Cmd+Shift+P in OSX) > `Translate selected text`
* you can also translate the text in your clipboard, or the current word if no text selected 
3. If you want to change translation to inline mode (when translation replaces original selected text), change **results_mode** in settings.
4. If you just want to see translation without changing your text, you can set **show_popup** in settings.
5. If you want to translate by default to different than English language, change **target_language** in settings.

💡 If you want to **check Readability**, select some text and run **Analyze text** command. 
You can do it in 3 ways:
* via binding and using hotkey **Ctrl+Alt+A** (⌘Cmd+Alt+A in OSX)
* via `Tools ➡️ Translator ➡️ Analyze text`
* via Command Pallet, Ctrl+Shift+P (⌘Cmd+Shift+P in OSX) > `Analyze text`
- to clear Analysis highlights use `Tools ➡️ Translator ➡️ Clear Analysis highlights`


### 🛠️ Commands
- **Translate selected text** - translates selected text based on your settings
- **Translate selected to...** - you choose the target language before translation
- **Translate clipboard** - translates text of your clipboard based on your settings
- **Translator: Print supported languages to console** - to see available languages for changing translation settings
- **Analyze text** - to see text statistics, readability checks and highlights
- **Clear Analysis highlights** - to clear text analysis highlights

## Installation (via Package Control)

* If you don't have Package Control, follow [this instruction](https://packagecontrol.io/installation)
* Open the Command Palette (Tools ➡️ Command Palette… )
* Search for and choose “Package Control: Install Package” (give it a few seconds to return a list of available packages)
* Search for “Translator” and install.

## 🧰 Settings

via Preferences ➡️ Package settings ➡️ Translator ➡️ Settings

    {
        "engine": "google",           // "google", "bing", 'bingcn' for cn.bing.com, 'googlehk' for google.com.hk 
        "source_language": "",        // Leave empty for Auto detection
        "target_language": "en",      // ! Must be specified    
        "results_mode": "insert",     // "insert", "replace" or "to_buffer" 
        "show_popup": false,          // false or true 
        "replace_linebreaks": false,  // false or true 
        "linebreak_replacement": " ", // could be a space, comma, semicolon, etc
        "analysis_language": "en"     // Language for Text Analysis: "en", "uk"
    }


## 📦️ Plugin repository at GitHub

[Translation plugin (multi-engine, fast) for SublimeText 3 & 4](https://github.com/dmytrovoytko/sublimetext-translate)

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko

If you find Translator package helpful, please ⭐️star⭐️ my repo https://github.com/dmytrovoytko/SublimeText-Translate/ to help other people discover it 🙏

## Support

* Your issues, feedback and suggestions regarding Translator plugin are welcome, feel free to report [here](https://github.com/dmytrovoytko/SublimeText-Translate/issues).
* Feel free to fork and submit pull requests.

📄 License:
===========

MIT

Credits:
========

* Inspired by old [Inline Google Translate](https://github.com/MTMGroup/SublimeText-Google-Translate-Plugin) package (by MTMGroup) that doesn't work since Google changed API.
* Used [Bing translate API](https://github.com/plainheart/bing-translate-api) approach, 谢谢! 
* Used [Sentence-splitter](https://github.com/mediacloud/sentence-splitter) for text analysis