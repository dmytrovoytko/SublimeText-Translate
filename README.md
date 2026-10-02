[![Support Ukraine](https://img.shields.io/badge/Support-Ukraine-FFD500?style=flat&labelColor=005BBB)](https://war.ukraine.ua/support-ukraine/) [![Downloads](https://img.shields.io/packagecontrol/dt/Translator)](https://packagecontrol.io/packages/Translator) ![Maintenance](https://img.shields.io/maintenance/yes/2026?style=flat-square)


Translator Plugin (Google, Bing) for SublimeText 3/4
====================================================

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://stand-with-ukraine.pp.ua)

**Version:** 3.5.0, **[Google] & [Bing] translate**, supported **194+** languages.

This plugin uses the public Google/Bing web endpoints, so no API key is needed and it works fast. These endpoints are unofficial and can break if Google/Bing change their URL schema or page markup.

This version includes Google & Bing translate, text readability analysis and statistics.

> [!IMPORTANT]  
> Please remember, both (unofficial) APIs have internal limitations, like text no longer than 1000 chars, or requests frequency. Don't overuse it, otherwise you easily get HttpError 4xx like `HTTP Error 429: Too Many Requests` or even temporary ban as they might treat you as a robot. If you get such errors take a pause, for an hour or more. See [Troubleshooting](#troubleshooting).

🎯 Features:
------------

* 194+ languages supported 
* SublimeText 3 & 4 supported (4215 tested)
* Autodetect source language
* Ability to specify source & target languages in settings
* Ability to choose the target language in context menu
* Works without VPN/proxies in China (choose 'bingcn' engine)
* 3 work modes: 
    - **replace** selected text with translation, 
    - **insert** translation after it (default)
    - **to_buffer** - translation goes to clipboard (without changing the text)
* Ability to show translation in popup without changing original text
* Ability to translate your clipboard / current word if no text selected
* In-memory translation cache, should help reduce the frequency of HTTP 429 errors
* Ability to replace line breaks inside text while translating (with space, comma, etc), useful to translate .po files
* Ability to analyze text readability and statistics (including Automated Readability Index, Coleman-Liau Index) to improve your documentation or SEO texts.

## 🚀 How to Use

### Translate

1. Select some text in the editor (or place the cursor on a word).
2. Run **Translate selected text** command:
- via `Tools ➡️ Translator ➡️ Translate selected text`
- via Command Palette, Ctrl+Shift+P (⌘Cmd+Shift+P in OSX) > `Translate selected text`
- via hotkey (disabled by default, see Key Bindings below)
3. If you want translation to replace the original text, change **results_mode** to `replace` in settings.
4. If you just want to see translation without changing your text, set **show_popup** to `true` in settings.
5. To change the default target language, change **target_language** in settings.
6. Additional commands:
- you can choose target language and then translate via `Tools ➡️ Translator ➡️ Translate selected to...`
- you can translate clipboard via `Tools ➡️ Translator ➡️ Translate clipboard`
7. Find supported languages via `Tools ➡️ Translator ➡️ Print supported languages to console`

### Check readability

1. Select some text in the editor.
2. Run **Analyze text** command:
- via `Tools ➡️ Translator ➡️ Analyze text`
- via Command Palette, Ctrl+Shift+P (⌘Cmd+Shift+P in OSX) > `Analyze text`
- via hotkey (disabled by default, see Key Bindings below)
3. To clear highlights, use `Tools ➡️ Translator ➡️ Clear Analysis highlights`.

### Key Bindings (optional)

No hotkeys are enabled by default. To enable them, go to `Preferences ➡️ Package Settings ➡️ Translator ➡️ Key Bindings` and remove `//` or add, for example:

```json
[
    {"keys": ["ctrl+alt+g"], "command": "translator"},
    {"keys": ["ctrl+shift+alt+g"], "command": "translator_to"},
    {"keys": ["ctrl+alt+b"], "command": "translator_from_buffer"},
    {"keys": ["ctrl+alt+a"], "command": "translator_text_analysis"}
]
```

### 🛠️ Commands
- **Translate selected text** - translates selected text based on your settings
- **Translate selected to...** - you choose the target language before translation
- **Translate clipboard** - translates text of your clipboard based on your settings
- **Translator: Print supported languages to console** - to see available languages for changing translation settings
- **Analyze text** - to see text statistics, readability checks and highlights
- **Clear Analysis highlights** - to clear text analysis highlights

## Installation

### Via Package Control (recommended)

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
        "translation_cache": true,    // false or true, if not set default = true
        "translation_cache_size": 200,// if not set default = 200
        "replace_linebreaks": false,  // false or true
        "linebreak_replacement": " ", // could be a space, comma, semicolon, etc
        "analysis_language": "en"     // Text Analysis: "en", "uk" (other values fall back to "en")
    }


## Troubleshooting

* `HTTP Error 429` / temporary ban / captcha: pause for an hour or more, then retry with fewer requests. Also opening https://translate.google.com / https://www.bing.com/translator (after a pause) may help (check captcha) - to show you're not a robot.
* `!!Google translate error!!` / `!!Bing translate error!!`: switch `engine` (`google` <-> `bing`), shorten the text (limit is ~1000 chars), and check console (`View ➡️ Show Console`).
* Bing `Max retries exceeded` / session errors: the plugin reuses one session per engine setup (captcha refreshes it automatically); if Bing hard-blocks you, switch engine or pause before retrying.
* Just installed and nothing works: restart Sublime Text so `requests` / `regex` dependencies finish installing, then retry.
* Wrong target language or empty output: confirm `target_language` is set, and `source_language` is empty for auto-detect.


## 📦️ Plugin repository at GitHub

[Translation plugin (multi-engine, fast) for SublimeText 3 & 4](https://github.com/dmytrovoytko/sublimetext-translate)

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko

If you find Translator package helpful, please ⭐️star⭐️ my repo https://github.com/dmytrovoytko/SublimeText-Translate/ to help other people discover it 🙏

## Support

* Your issues, feedback and suggestions regarding Translator plugin are welcome, feel free to report [here](https://github.com/dmytrovoytko/SublimeText-Translate/issues).
* Feel free to fork and submit pull requests.

## 📄 License

MIT

## Credits

* Inspired by old [Inline Google Translate](https://github.com/MTMGroup/SublimeText-Google-Translate-Plugin) package (by MTMGroup) stopped working as Google changed API.
* Used [Bing translate API](https://github.com/plainheart/bing-translate-api) approach, 谢谢! 
* Used [Sentence-splitter](https://github.com/mediacloud/sentence-splitter) for text analysis
