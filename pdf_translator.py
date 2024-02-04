import os
import time
import subprocess
from bs4 import BeautifulSoup as bs
from pyhtml2pdf import converter
from googletrans import Translator


start = time.time()

def create_directory(directory):
    os.makedirs(directory, exist_ok=True)

def html2pdf_and_save(html_filename):
    create_directory('./output')
    output_filename = f"./output/{html_filename.split('/')[-1].split('.')[0]}_{input_to_language}_processed.pdf"
    output_path = os.path.abspath(html_filename)
    # print_options = {
    #     'paperHeight': 11.69,
    #     'paperWidth': 8.27,
    #     'printBackground': True
    # }

    converter.convert(f'file:///{output_path}', output_filename)
    print(f"done! The output file is saved in {output_filename}")

def translate_text(text, target_language):
    translator = Translator()
    try:
        translated_text = translator.translate(text, dest=target_language).text
    except:
        translated_text = text
    return translated_text

def process_multiclass(multidiv, soup,target):
    if multidiv.find('span'):
        spans = multidiv.find_all('span')
        for span in spans:
            if len(span.get('class')) >= 4:
                saved_span = soup.new_tag(name='span', attrs={'class': span.get('class')})
                saved_span.string = " "
                multidiv.string = translate_text(multidiv.get_text())
                multidiv.append(saved_span)
                return
        multidiv.string = translate_text(multidiv.get_text(),target)
    else:
        multidiv.string = translate_text(multidiv.get_text(),target)

def html_parser(html_filename,to_language='en'):
    
    with open(html_filename, "r", encoding='utf-8') as file:
        html_content = file.read()

    soup = bs(html_content, 'html.parser')
    container = soup.find("div", {"id": "page-container"})
    pages = container.find_all("div", recursive=False)
    total_no_pages = len(pages)
    for current_page_no, page in enumerate(pages, start=1):
        page = page.find('div')
        for list_of_div in page.find_all('div', recursive=False):
            if not list_of_div.text.strip():
                continue
            if len(list_of_div.get('class')) > 5:
                process_multiclass(list_of_div, soup,to_language)
            else:
                for subdiv in list_of_div.find_all('div', recursive=False):
                    process_multiclass(subdiv, soup,to_language)
        print(f"\rTranslated({current_page_no},{total_no_pages})  {time.time() - start:.2f}", end='', flush=True)
    create_directory('./temp')
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print("\nsaving translated file")
    html2pdf_and_save(html_filename)

input_filename = input("Enter the file name :")
input_to_language = input("Enter the language to translate (ex: 'en' for English, 'fr' for French, 'ta' for Tamil)")

def docker_init(input_filename):

    subprocess.run(["powershell.exe", f"mkdir temp"], capture_output=True, text=True)
    subprocess.run(["powershell.exe", f"cp {input_filename} temp"], capture_output=True, text=True)
    cmd = "docker run -ti --rm -v ${PWD}/temp:/pdf pdf2htmlex/pdf2htmlex:0.18.8.rc2-master-20200820-ubuntu-20.04-x86_64 ./"
    result = subprocess.run(["powershell.exe", f"{cmd}{input_filename}"], capture_output=True, text=True)


print("preprocessing is started")
docker_init(input_filename)
print("translating is started")
html_filename = f"./temp/{input_filename.split('.')[0]}.html"
html_parser(html_filename,input_to_language)     


print(f"Translation completed in {time.time() - start:.2f}s")
