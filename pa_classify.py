from pa_classifier import judge
from pa_classifier import classifier
import os
from utils.filtrate import check_and_move_folders

use_translate = False


def main(k, path):
    print(f'The image path is {path}.')
    print("================>start to judge P&&A<================")
    ispa, judge_result = judge.is_PA(k, path)
    print(judge_result)
    result_path = os.path.join(path, "output.txt")
    text_file = open(result_path, "w")
    text_file.write(judge_result+"\n")

    if ispa:
        print("================>start to classify it<================")
        pred = classifier.test(k, path)
        string = f"According to inat21 dataset, the image is most likely to be {pred['name']}," \
                 f" common name: {pred['common_name']}, supercategory: {pred['supercategory']}."
        print(string)
        text_file.write(string)
        if use_translate:
            # pip install translate, 
            from translate import Translator
            chinese = Translator(from_lang="English", to_lang="Chinese").translate(pred['common_name'])
            print(chinese)
            text_file.write(chinese)
    text_file.close()


if __name__ == '__main__':
    topk = 5
    base_path = './rendered_data'
    for item in os.scandir(base_path):
        if item.is_dir():
            main(topk, item.path)
    check_and_move_folders(base_path)
