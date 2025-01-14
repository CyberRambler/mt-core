import argparse
import os

import jieba
from bs4 import BeautifulSoup, Comment
from yimt.api.utils import detect_lang

html_progress = ""
def too_shor(txt, lang):
    if len(txt.strip()) == 0:
        return True

    if lang == "en" and len(txt.strip().split()) < 3:
        return True

    if lang == "zh" and len(list(jieba.cut(txt))) < 3:
        return True

    return False


def translate_ml_auto(in_fn, source_lang="auto", target_lang="zh", translation_file=None):
    if translation_file is None:
        paths = os.path.splitext(in_fn)
        translated_fn = paths[0] + "-translated" + paths[1]
    else:
        translated_fn = translation_file

    in_fn = in_fn.lower()
    html_txt = open(in_file, encoding="utf-8").read()
    if in_fn.endswith(".html") or in_fn.endswith(".xhtml") or in_fn.endswith(".htm"):
        soup = BeautifulSoup(html_txt, "html.parser")
    elif in_file.endswith(".xml") or in_fn.endswith(".sgml"):
        soup = BeautifulSoup(html_txt, "xml")

    body = soup

    to_translated_elements = []
    to_translated_txt = []
    for element in body.findAll(text=True):
        if not element.parent.name in ['style', 'script', 'head', 'meta', 'link']:
            if type(element.string) == Comment:
                continue

            t = element.string
            # if too_shor(t, translator.from_lang):
            #     continue

            to_translated_elements.append(element)
            to_translated_txt.append(element.string)

    if source_lang == "auto":
        source_lang = detect_lang(t)

    from yimt.api.translators import Translators
    translator = Translators().get_translator(source_lang, target_lang)
    global html_progress
    html_progress = ""
    translations = []
    batch_size = 100
    for i in range(0, len(to_translated_txt) // batch_size + 1):
        batch = to_translated_txt[i * batch_size: i * batch_size + batch_size]
        # print(batch) # 测试用
        translation = translator.translate_list(batch)
        translations += translation
        html_progress += "#"
        print("html_progress:" + html_progress)  # 测试用
    # translations = translator.translate_list(to_translated_txt)

    for e, t in zip(to_translated_elements, translations):
        e.replaceWith(t)

    out_f = open(translated_fn, "w", encoding="utf-8")
    out_f.write(soup.prettify())
    out_f.close()
    html_progress = ""
    return translated_fn


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("HTML/XML File Translator")
    arg_parser.add_argument("--to_lang", type=str, default="zh", help="target language")
    arg_parser.add_argument("--input_file", type=str, required=True, help="file to be translated")
    arg_parser.add_argument("--output_file", type=str, default=None, help="translation file")
    args = arg_parser.parse_args()

    to_lang = args.to_lang
    in_file = args.input_file
    out_file = args.output_file

    translated_fn = translate_ml_auto(in_file, target_lang=to_lang, translation_file=out_file)

    import webbrowser

    webbrowser.open(in_file)
    webbrowser.open(translated_fn)
