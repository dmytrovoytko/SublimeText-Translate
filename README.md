Translator Plugin (multi-engine) for SublimeText 3 & 4
======================================================

**Version:** 3.0.0, **[Google] & [Bing] translate**, supported **133+** languages.

This plugin uses a standard Google/Bing translate page results. It works fast! And as API keys are not required it makes plugin very easy to use. However it isn't 100% officially supported, so if Google/Bing change their URL schema it could break the plugin.

This version includes Google & Bing translate, adding other translators is in development.

🎯 Features:
============

* 133+ languages supported 
* SublimeText 3 & 4 supported
* Autodetect of source language
* Ability to specify source & target languages in settings
* Ability to choose the target language in context menu
* 2 modes: **replace** selected text with translation, or **insert** translation after it

## 🚀 How to Use (very easy)

1. Select some text in the editor
2. Run **Translate selected text** command. 
You can do it in 3 ways:
- via binding and using hotkey **Ctrl+Alt+G** (⌘Cmd+Alt+G in OSX)
- via Tools ➡️ Translator ➡️ Translate seclected text
- via Command Pallet, Ctrl+Shist+P (⌘Cmd+Shift+P in OSX) > Translate selected text
3. If you want to change translation to inline mode (when translation replaces original selected text), change **results_mode** in settings.
4. If you want to translate by default to different than English language, change **target_language** in settings.

### 🛠️ Commands
- **Translate selected text** - translates selected text baesd on settings
- **Translate selected to...** - you choose the target language before translation
- **Translator: Print supported languages to console** - to see available languages for changing translation settings

## 🧰 Settings

    {
        "source_language": "",      // Leave empty for Auto detection
        "target_language": "en",    // ! Must be specified  
        "results_mode": "insert",   // "insert" or "replace" 
        "engine": "google"          // "google", "bing", try 'googlehk' for google.com.hk  
    }

## 📦️ Plugin repository at GitHub

[Translation plugin (multi-engine, fast) for SublimeText 3 & 4](https://github.com/dmytrovoytko/sublimetext-translate)

Your feedback and suggestions are welcome.
Made with ❤️ in Ukraine 🇺🇦

📄 License:
===========

MIT

Credits:
========

* Inspired by old [Inline Google Translate](https://packagecontrol.io/packages/Inline%20Google%20Translate) package (by MTMGroup) that doesn't work since Google changed API.
* Used [Bing translate API](https://github.com/plainheart/bing-translate-api) approach, 谢谢! 