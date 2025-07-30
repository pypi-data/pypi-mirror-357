🧩 jinja_components
Reusable Jinja2 Components and Macros for Web Projects

jinja_components is a minimal and extensible library of reusable HTML components and Jinja2 macros, designed to speed up template development in Flask, Django, and static Jinja projects.

🚀 Features
✅ Ready-to-use macro components

🎨 Clean, customizable HTML structure

🔁 DRY (Don’t Repeat Yourself) templating

⚙️ Easy integration with Flask, Django, or Jinja-only projects

📁 Modular folder structure

---

## 📦 Installation
You can simply clone the repository and copy the components folder:

## 🚀 Usage

```bash
# Clone the repository
git clone https://github.com/TamerOnLine/jinja-ui.git
cd jinja-ui

# Create virtual environment
python -m venv venv  # or: py -m venv venv (on Windows)

# Activate virtual environment
# ▶ On Windows:
venv\Scripts\activate
# ▶ On Linux/macOS:
source venv/bin/activate

# Upgrade pip and install dependencies
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
jinja-ui/
├── components/          # Reusable HTML components
├── macros/              # Jinja2 macros for reusable UI elements
├── templates/           # Jinja2 templates


```

> **Note:** The folders `components/` and `macros/` are mentioned in the roadmap but are not yet created.

---

## 💡 Usage Example

### macros.html.j2
```jinja2
{% macro card(title, content) %}
  <div class="card">
    <h3>{{ title }}</h3>
    <p>{{ content }}</p>
  </div>
{% endmacro %}
```

### index.html.j2
```jinja2
{% import 'macros.html.j2' as ui %}

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{{ _("My Jinja Macro Demo") }}</title>
</head>
<body>
  {{ ui.card(_("Hello!"), _("This is the first card I made using a Jinja Macro.")) }}
</body>
</html>
```

---

## 🎨 Dynamic Styling

Customize the component styles using `style_injector.j2`:

```jinja2
{% set settings = {
  "bg_color": "#f9f9f9",
  "font_family": "Tahoma",
  "border_radius": "16px"
} %}
{% include 'style_injector.j2' %}
```

---

## ⚙️ Template Rendering

Use the included Python script to render `index.html.j2` and generate an HTML output:

**render_template.py**
```python
from jinja2 import Environment, FileSystemLoader

def identity(x):
    return x  # Placeholder for future i18n

def main():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('index.html.j2')
    output = template.render(_=identity)
    with open("output.html.j2", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    main()
```
### Run the script to render the template
You can run the script using the following command:

## 🚀 Usage

```bash
py -m render_template
```
This will generate an `output.html.j2` file with the rendered content.

---


# 🌍 Internationalization (i18n) Support

This project includes built-in support for internationalization using [`pybabel`](https://babel.pocoo.org/). It allows you to:

- Extract translatable strings  
- Initialize language files  
- Auto-translate missing entries *(optional)*  
- Compile translations into `.mo` files  

---

## 🧾 Step 1: Create `babel.cfg`

Create a file named `babel.cfg` in the root directory with the following content:

```ini
[python: **.py]
[jinja2: **.j2]
```

This configuration tells `pybabel` to extract translatable strings from both Python and Jinja2 template files.

---

## 📁 Step 2: Create `translations/` Directory

Set up the following directory structure:

```
translations/
├── ar/
│   └── LC_MESSAGES/
│       └── messages.po
├── de/
│   └── LC_MESSAGES/
│       └── messages.po
├── en/
│   └── LC_MESSAGES/
│       └── messages.po
```

> You don’t need to manually create `.po` files — they will be initialized automatically by the script in Step 4.

---

## 📄 Step 3: (Optional) Create `messages.pot`

You can create an empty `messages.pot` file in advance, or let the script generate it:

```bash
touch messages.pot
```

---

## ⚙️ Step 4: Create `i18n_translations.py`

This script will:

- Extract translatable messages
- Initialize `.po` files for the specified languages
- Compile `.po` files into `.mo` files

```python
import os
import subprocess

PROJECT_DIR = os.path.abspath('.')
LOCALES_DIR = os.path.join(PROJECT_DIR, 'translations')
POT_FILE = os.path.join(PROJECT_DIR, 'messages.pot')
BABEL_CFG = os.path.join(PROJECT_DIR, 'babel.cfg')
LANGUAGES = ['ar', 'de']  # Add more languages if needed

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error:\n{result.stderr}")
    else:
        print(result.stdout)

def extract_messages():
    cmd = f"pybabel extract -F {BABEL_CFG} -o {POT_FILE} {PROJECT_DIR}"
    run_cmd(cmd)

def init_languages():
    for lang in LANGUAGES:
        lang_dir = os.path.join(LOCALES_DIR, lang)
        if not os.path.exists(lang_dir):
            print(f"Initializing language: {lang}")
            cmd = f"pybabel init -i {POT_FILE} -d {LOCALES_DIR} -l {lang}"
            run_cmd(cmd)
        else:
            print(f"Language {lang} already initialized.")

def compile_translations():
    cmd = f"pybabel compile -d {LOCALES_DIR}"
    run_cmd(cmd)

if __name__ == "__main__":
    extract_messages()
    init_languages()
    compile_translations()
    print("Done! Edit the .po files in translations/<lang>/LC_MESSAGES/messages.po")
```

## 🚀 Usage

```bash
py -m i18n_translations
```

This command will:

- Extract translatable strings into `messages.pot`
- Initialize `.po` files for each language in the `translations/` directory
- Compile `.po` files into `.mo` files used by the app at runtime

---

## 🤖 Automatic Translation of .po Files
Automate translation of untranslated strings in .po files using Google Translate:

**i18n_auto.py**
```python 
import os
import polib
from googletrans import Translator

def auto_translate_po(file_path, dest_lang='ar'):
    po = polib.pofile(file_path)
    translator = Translator()

    untranslated = [entry for entry in po if not entry.translated()]

    print(f"Found {len(untranslated)} untranslated entries in {file_path}.")

    for entry in untranslated:
        try:
            translated = translator.translate(entry.msgid, dest=dest_lang)
            entry.msgstr = translated.text
            print(f'Translated "{entry.msgid}" to "{entry.msgstr}"')
        except Exception as e:
            print(f"Error translating '{entry.msgid}': {e}")

    po.save(file_path)
    print(f"Translations saved to {file_path}")

def translate_all_po_files(translations_dir='translations'):
    for root, dirs, files in os.walk(translations_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                parts = po_path.split(os.sep)
                try:
                    lang = parts[parts.index('translations') + 1]
                except (ValueError, IndexError):
                    lang = 'en'
                print(f"Translating file {po_path} to language '{lang}'")
                auto_translate_po(po_path, dest_lang=lang)

if __name__ == "__main__":
    translations_folder = 'translations'
    translate_all_po_files(translations_folder)
```

🚀 **Usage**:

```bash
py -m i18n_auto
```

---
## ⚙️ Compile .po to .mo Files
This script compiles all `.po` files in the `translations` directory to `.mo` files, which are used by Jinja2 for translations.

**i18n_compile.py**


```python

import os
import subprocess

def compile_translations(translations_dir='translations'):
    for root, dirs, files in os.walk(translations_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                # Compile .po to .mo
                cmd = f"pybabel compile -i \"{po_path}\" -o \"{po_path[:-3]}.mo\""
                print(f"Compiling {po_path} ...")
                subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    compile_translations()
    print("All .po files compiled to .mo files.")
```

🚀 **Usage**:

```bash
py -m i18n_compile
```

---

## 🧠 Script Overview – i18n_main.py:
This script orchestrates the entire internationalization process by calling the functions from the above modules in a clean and modular way. It extracts messages, initializes languages, translates .po files, compiles translations, and cleans up the generated .pot file.

```python
import os
import i18n_translations         # Contains extract_messages(), init_languages()
import i18n_auto                 # Contains translate_all_po_files()
import i18n_compile              # Contains compile_translations()

def delete_pot_file():
    pot_file = os.path.join(os.path.abspath('.'), 'messages.pot')
    if os.path.exists(pot_file):
        os.remove(pot_file)
        print("✅ messages.pot has been deleted.")

if __name__ == "__main__":
    i18n_translations.extract_messages()
    i18n_translations.init_languages()
    i18n_auto.translate_all_po_files()
    i18n_compile.compile_translations()
    delete_pot_file()
    print("\n✅ All steps completed successfully.")
```

✅ Benefits:
Keeps logic modular and reusable.
Easier to debug and maintain.
Avoids repeating code or merging all logic in one place.
Fully automates your translation pipeline with a single command.

🚀 **Usage**:

```bash
py -m i18n_main
```
The script will automatically:
- Extract messages
- Initialize missing translation folders
- Translate all .po files
- Compile translations
- Clean up

---

## 📌 Roadmap

- [ ] Add more components (badges, alerts, navbars...)  
- [ ] Add unit tests  
- [ ] Add real-time theme switcher (dark/light)  
- [ ] Publish on PyPI (jinja-components)  

---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

**Tamer Hamad Faour**  
[GitHub @TamerOnLine](https://github.com/TamerOnLine)
