import os
import re
import csv
import webview
import argparse

import_file = None
save_root = None

def open_import_file(win):
    file_types = ('WebScraper Data (*.csv)', 'All files (*.*)')
    global import_file 
    import_file = win.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
    win.destroy()

def open_export_file(win):
    global save_root 
    save_root = win.create_file_dialog(webview.FOLDER_DIALOG)
    win.destroy()

def getExport(file):
    logger.debug("opening export file")
    reader = csv.DictReader(file, delimiter=',')
    exportData = []
    for row in reader:
        exportData.append(row)
    return exportData

def createHTML(data):
    tab = '\t'
    output = f"""
    <div itemscope itemtype="https://schema.org/Recipe">
        <span itemprop="name">{data['recipieNamePrefix'] + data['recipieName']}</span>
        <img itemprop="image" src="{data['recipieImage']}" />
        <span itemprop="recipeYield">{data['recipeYield']}</span>
        <span itemprop="description">{data['recipieNotes']}</span>

        <div itemprop="nutrition" itemscope itemtype="https://schema.org/NutritionInformation">
            <span itemprop="calories"> {data['calories']}</span>
            <span itemprop="fatContent"> {data['fatContent']}</span>
            <span itemprop="saturatedFatContent"> {data['saturatedFatContent']}</span>
            <span itemprop="cholesterolContent">{data['cholesterolContent']}</span>
            <span itemprop="sodiumContent"> {data['sodiumContent']}</span>
            <span itemprop="carbohydrateContent">{data['carbohydrateContent']}</span>
            <span itemprop="fiberContent"> {data['fiberContent']}</span>
            <span itemprop="sugarContent"> {data['sugarContent']}</span>
            <span itemprop="proteinContent"> {data['proteinContent']}</span>
        </div>

        <ol>
{os.linesep.join(f'{tab*3}<li itemprop="recipeIngredient">{ingredient}</li>' for ingredient in data['recipieIngredients'])}
        </ol>
        <div>
{''.join(data['recipeInstructions'])}
        </div>
    </div>
    """ 
    return output

def createIndexHTML(data):
    tab = '\t'
    output = f"""
    <HTML>
    <Head></Head>
    <Body>
        <ul>
            {os.linesep.join(f'{tab*3}<li><a href="./{value["saveFileName"]}.html">{key}{tab}{value["recipieName"]}</a></li>' for key,value in mealplan.items())}
        </ul>
    </Body>
    """ 
    return output

def save_file(recipie, filename = None):
    if filename is None:
        filename = recipie['saveFileName']
    
    fullpath = save_root / filename
    with open(fullpath.with_suffix(".html") , 'w')as f:
        f.write(recipie['outputHtml'])
        

import pathlib
import logging


if __name__ == '__main__':

    logging.basicConfig()
    global logger 
    logger = logging.getLogger()

    def verbose(lvl):
        logger.setLevel(lvl)
        return lvl

    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

    parser.add_argument('-i', '--in', type=argparse.FileType(), required=False, dest="import_file", default=None)     
    parser.add_argument('-o', '--out', type=pathlib.Path, required=False, dest="save_root")
    parser.add_argument('-v', '--verbose', type=verbose, required=False, default="WARNING")
    parser.add_argument('-a', '--archive', default=False, action='store_true')

    args = parser.parse_args()

    import_file = args.import_file
    save_root = args.save_root

    logger.debug("Args Parsed: %s %s %s", str(import_file), str(save_root), str(args.archive))

    logger.debug(import_file)
    if import_file is None:
        window = webview.create_window('Open file dialog example', 'https://pywebview.flowrl.com/hello', hidden=True)
        webview.start(open_import_file, window)
        if import_file is None:
            logger.error("No input file selected")
            exit()
        import_file = open(import_file[0])
        logger.debug(import_file)

    logger.debug(save_root)
    if save_root is None:
        window = webview.create_window('Open file dialog example', 'https://pywebview.flowrl.com/hello', hidden=True, focus=True, on_top=True)
        webview.start(open_export_file, window)
        if save_root is None:
            logger.error("No output directory selected")
            exit()
        save_root = pathlib.Path(save_root[0])
        logger.debug(save_root)

    if import_file is not None and save_root is not None:
        exportData = getExport(import_file)
    
    if args.archive:
        import shutil
        dest = str(save_root)[::-1].replace("Active"[::-1], "Archive"[::-1])[::-1]
        for file in os.listdir(save_root):
            if file != 'index.html':
                file_path = os.path.join(dest, file)
                shutil.move(os.path.join(save_root,file), os.path.join(dest, file))

    # Time to map
        mealplan = {}
        for recipie in exportData:

            recipie['saveFileName'] = ''.join(c for c in str.lower(recipie['recipieName']) if c.islower())

            mealplan[recipie['Date']+'-'+recipie['MealType']] = {'recipieName':recipie['recipieName'], 'saveFileName':recipie['saveFileName']}

            if recipie['recipieName'].startswith('Leftover'):
                next

            recipie['recipieNamePrefix'] = "[MCD]"
            recipie['recipieNotes'] = "Exported from mayoclinicdiet"
            recipie['recipieImage'] = re.findall(r'(https:.*)\"', recipie['recipieImage'])[0] 
            # 'NutritionInfo
            recipie['calories'] = "TO BE MAPPED"
            recipie['fatContent'] = "TO BE MAPPED"
            recipie['saturatedFatContent'] = "TO BE MAPPED"
            recipie['cholesterolContent'] = "TO BE MAPPED"
            recipie['sodiumContent'] = "TO BE MAPPED"
            recipie['carbohydrateContent'] = "TO BE MAPPED"
            recipie['fiberContent'] = "TO BE MAPPED"
            recipie['sugarContent'] = "TO BE MAPPED"
            recipie['proteinContent'] = "TO BE MAPPED"
            
            recipie['recipeIngredients'] = re.findall('>(.+?)</li>', recipie['recipeIngredients'])

            fixedIngredients = []
            for ingredient in recipie['recipeIngredients']:
                logger.debug(ingredient)   
                fixedIngredients.append(re.sub(r'(.*)\,(.*)', r'\2\1', ingredient))
                logger.debug(fixedIngredients[-1])
         
            recipie['recipieIngredients'] = fixedIngredients
            recipie['recipeInstructions'] = re.sub(r'<p>','\t\t\t<p  itemprop="recipeInstructions">', recipie['recipeInstructions']) 

            # Create HTML
            recipie['outputHtml'] = createHTML(recipie)
            # logger.debug(recipie['outputHtml'])

            save_file(recipie)

    indexHTML = {}
    indexHTML['outputHtml'] = createIndexHTML(mealplan)
    save_file(indexHTML, "index.html")
    print(indexHTML)