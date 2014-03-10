# What is UliPad

Ulipad is a wxPython powered, programmer oriented and flexible editor.
It has many features such as class browser,
code auto-complete, html viewer, directory browser, wizard and many
others. The most interesting
and distinctive feature is the use of mixin technique which makes
Ulipad an easy-to-extend
programming environment. You can write your own mixins, plugins or
simple scripts, and all of
them can be integrated in Ulipad in a seamless way.

# Why named it UliPad?

The name comes from Claudio Grondi (thank you!).

Claudio Grondi said:

> As we are on the way to make NewEdit THE programmer editor I think, that
> a new unique name will help here much (NewEdit is just cheap...).
>
> I suggest to use 'UliPad'.
>
> It has the shortcut of UnLImited.
> It tells it is a plain text editor (Pad).
> It tells something about the original author (LImodou).
>
> But the most important advantage is:
>
>    Google has no entry for 'UliPad' yet!
>
> Wonderful! It seems many people like it.

# Description

UliPad uses Mixin and Plugin technique as its architecture. Most of its classes can be extended via mixin and plugin components, and finally become an integrity class when creating the instance. So `UliPad` is very dynamic. You can write the new features in new files, and hardly need to modify the existing code. And if you want to extend the existing classes, you could write mixins and plugins, and this will be bound to the target class that I call "Slot Class". This technique will make the changes centralized and easily managed.

Requirements:

 * Python 2.6+
 * wxPython 2.8+ Unicode Version

Some plugins may have additional requirements, please read the readme information before installing them.

# Objective

Make a clean, powerful, flexible general editor, and even an application framework.  And adding extensions should be very easy.

Tasks:

* Mixin and Plugin framework
* Unicode support
* User defined plugin management
* User custom window integration
* User custom wizard function

# Change Log

You can see the `ChangeLog` to know the new changes of UliPad.

# Features

* **Cross platform**
    * based on wxPython, so it can run anywhere that wxPython works, such as: Windows, Linux.
    * Unicode support.
* **Most features of wxStyledTextCtrl(Scintilla)**
    * Syntax highlighting, support Python, c/c++, html, plain text
    * Folding
    * Brace Matching
    * ...
* **Extended selection**
    * Extended word selection -- You can press Ctrl+`MouseDoubleClick` to select a word including '.'
    * Matched selection -- Select text in quoted chars like: (), [], {}, `''`, `""`.

        For example: a string just like

        ```
        def func(self, 'This is a test'):
                   ^
        ```

        The '^' char represents caret position in above line. If you press Ctrl+E, you will select the whole text in (),
        i.e. "self, 'This is a test'". Something more in Selection Menu.
* **Other editing extension**
    * Duplicating text -- Just like Vim Ctrl+V, Ctrl+P, and more. You can duplicate above or below char, word, line which match the leading chars.
    * Quoting text -- Add some quoted chars before and after selected text, just as: `""`, `''`, (), [], {}, and customized string, etc.
    * Text convertion and view -- python -> html, reStructured Text -> html, textile -> html, and you can output or view the html text in message window, or html view window, or replace the selected text.
    * Utf-8 encoding auto detect
    * Changing document encoding
    * Auto backup
    * Last session support -- It'll save all the filenames as closed, and reopen the files as next started.
    * Smart judge the indent char -- It'll auto guess the indent char, and sets it.
    * Finding in files
    * Bookmark supports
* **Python support**
    * built-in python interactive window based on `PyShell`, support Unicode
    * Auto completion
    * Function syntax calltips
    * Run, run with argument, stop python source
    * Auto change current path
    * Python class browser
    * Syntax and PEP8 style checking，also supply a pylint plugin.
* **Code snippets**

    You can manage your code snippets with categories, and each category can have many items. Every item will represent a code snippet. You can insert an item just by double-clicking on it. It even supports importing and exporting.

* **Simple project support**

    Can create a special file `_project`, so every file and folder under the folder which has the `_project` can be considered as a whole project.

* **Extension mechanism**
    * Script -- You can write easy script to manipulate the all resource of UliPad, just like: text conversion, etc.
    * Plugin -- Customized function. More complex but more powerful. Can easily merge with UliPad, and can be managed via menu.
    * Shell command -- Add often used shell commands, and execute them.
* **Ftp support**

    You can edit remote files through ftp. You can add, rename, delete, upload, download file/directory.

* **Multilanguage support**

    Currently supports 4 languages: English, Spanish, Simplified Chinese and Traditional Chinese, which can be auto-detected.

* **Ships many plugins** (must be configed as used them before)
    * Django support plugin
    * Batch rename files plugin
    * Collaborative Programming support plugin, names as *pairprog*.
    * Mp3 player plugin
    * Spell check plugin
    * wizard plugin
    * Text to speech(windows only) plugin
    * ...
* **Shipped scripts**
    * You can find them in (`$UliPadInstalled`)/scripts.
* **Wizard**

    You can make your own wizard template. The wizard can input user data, combine with template, and output the result. And wizard also support code framework created. This feature will help you improving coding efficiency.

* **Direcotry Browser**

    Browse multiple directories, and you can really add, delete, rename directories and files. Double click will open the file in Editor window.

* **AutoComPlete(acp)**

    Suport user autocomplete file, it can help to input code very helpful and functional.

* **Column Editing Mode**

    You can select multilines, and then set a column mode region, so in any line of this region, if you enter a character, other lines will also add this character. If you want to deal with multilines as a similar mode, this functionality will be very handy.

* **Smart Navigation**

    UliPad can remember the visit order of your opened files, and you can go back or go forward in  these files.

* **Live regular expression searching**

    You can type some regular expression on the fly, and see the result dynamiclly.

* **Spell check plugin**

    Need to install `PyEnchant` module.

* **Collaborative Programming**

    Multi-user can modify some files at the same time. You should enable *pairprog* plugin.

* **Todo Supports**

    Auto finds todos and supports several kind of formats.

* **Multi-View Supports**

    User can open a document in multi views, for example in left pane or bottom pane.

* **Version Control Support**
    * svn support. Now you can use svn in `UliPad` to update, checkout, commit, etc.


# How to run

Just download the source code and extract to any folder, and then execute:

```
python ulipad.pyw
```

or

```
python ulipad.py
```

# License

UliPad is released under GPL license.
