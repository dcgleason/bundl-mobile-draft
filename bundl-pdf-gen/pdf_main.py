from pdf_gen import pdf_book_gen
import json


if __name__ == '__main__':
    contribution_dict = json.load(fp=open('mom-bundl.json', encoding='utf8'))
    print(f'Starting {contribution_dict["rec_name"]}\'s book creation\n')
    pdf_book_gen(contribution_dict)
