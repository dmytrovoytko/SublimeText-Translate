[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://stand-with-ukraine.pp.ua)

Translator Plugin (multi-engine) for SublimeText 3 & 4
======================================================

**Version:** 3.1.0, **[Google] & [Bing] translate**, supported **133+** languages.

This plugin uses a standard Google/Bing translate page results. It works fast! And as API keys are not required it makes plugin very easy to use. However it isn't 100% officially supported, so if Google/Bing change their URL schema it could break the plugin.

This version includes Google & Bing translate, adding other translators is in development.

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
* Ability to translate current word if no text selected

## 🚀 How to Use (easy)

1. Select some text in the editor
2. Run **Translate selected text** command. 
You can do it in 3 ways:
- via binding and using hotkey **Ctrl+Alt+G** (⌘Cmd+Alt+G in OSX)
- via Tools ➡️ Translator ➡️ Translate seclected text
- via Command Pallet, Ctrl+Shift+P (⌘Cmd+Shift+P in OSX) > Translate selected text
3. If you want to change translation to inline mode (when translation replaces original selected text), change **results_mode** in settings.
4. If you just want to see translation without changing your text, you can set **show_popup** in settings.
5. If you want to translate by default to different than English language, change **target_language** in settings.

### 🛠️ Commands
- **Translate selected text** - translates selected text baesd on settings
- **Translate selected to...** - you choose the target language before translation
- **Translator: Print supported languages to console** - to see available languages for changing translation settings

## Installation (via Package Control)

* If you don't have Package Control follow [this instruction](https://packagecontrol.io/installation)
* Open the Command Palette (Tools ➡️ Command Palette… )
* Search for and choose “Package Control: Install Package” (give it a few seconds to return a list of available packages)
* Search for “Translator” and install.

## 🧰 Settings

via Preferences ➡️ Package settings ➡️ Translator ➡️ Settings

    {
        "source_language": "",      // Leave empty for Auto detection
        "target_language": "en",    // ! Must be specified  
        "results_mode": "insert",   // "insert", "replace" or "to_buffer"
        "show_popup": false,        // false or true 
        "engine": "google"          // "google", "bing", try 'googlehk' for google.com.hk  
    }


## 📦️ Plugin repository at GitHub

[Translation plugin (multi-engine, fast) for SublimeText 3 & 4](https://github.com/dmytrovoytko/sublimetext-translate)

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko

If you find Translator package helpful, please ⭐️star⭐️ my repo https://github.com/dmytrovoytko/SublimeText-Translate/ 🙏

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