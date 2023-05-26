import json
import os
import random
import shutil

import PyPDF2
import fitz
from fitz import TEXT_ALIGN_JUSTIFY, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT

from config import fonts, doc_templates, output_dir
from util import remove_exif

quotes_used = []


def pdf_book_gen(book_dict: dict) -> None:
    """

    Main book generation function. Creates output folder to store finished files.

    :param book_dict: Dictionary consisting of the gift details
    :return: None

    """

    remove_exif()
    if not os.path.isdir('temp'):
        os.mkdir('temp')  # Create temp dir
    if not os.path.isdir(f'{output_dir}/{book_dict["rec_name"]}'):  # Check if output dir already exists
        os.mkdir(f'{output_dir}/{book_dict["rec_name"]}')  # Create output dir

    pdf_cover(book_dict)  # Generate cover
    pdf_interior_gen(book_dict)  # Generate interior

    print('Cleaning up temp folder', end='')
    shutil.rmtree(r'temp')  # Remove temp folder
    print('...Done')


def pdf_cover(book_dict: dict) -> None:
    """

    This function creates the second page of the cover displaying the recipients name (:param name)
    Run only once per document

    :param book_dict: Dictionary consisting of the gift details
    :return: None

    """
    cover_doc = fitz.open(doc_templates['front'][book_dict['doc']['front']])  # Open cover PDF template
    cover = cover_doc[0]  # Select page
    name = book_dict['rec_name']  # Recipient name
    cover_name_rect = [850, 300, 1157, 362.5]  # XYWH Coordinates for the name field on the cover

    print('Creating book cover', end='')

    # INSERT NAME onto COVER
    cover.insert_textbox(cover_name_rect, 'Dear %s' % name, fontsize=fonts['cover']['font_size'],
                         fontname=fonts['cover']['font_name'], fontfile=fonts['cover']['font_path'], align=1,
                         render_mode=0, fill=(0, 0, 0))
    print('...Done')
    print('Saving cover', end='')
    cover_doc.save(f'{output_dir}/{book_dict["rec_name"]}/{name}_Cover.pdf')  # Save cover
    print('...Done')


def pdf_interior_gen(book_dict: dict) -> None:
    """

    Based on a dictionary (:param book_dict) this function will generate all the pages of the interior of the book.
    :param book_dict: Dictionary with all the book_dict
    :return: None

    """

    int_first_page = fitz.open('templates/pdf_templates/Inter_first_page.pdf')  # Open first page for the interior
    int_first_page.save('temp/inter_first.pdf')  # Save temp first page
    contributions = book_dict['messages']  # Select contributions from book_dict
    int_pdf_list = ['temp/inter_first.pdf']  # Temp PDF file list

    ix = 2  # Starting index

    # Loop over sorted contributions based on name
    for contribution in sorted(contributions.items(), key=lambda x: x[1]['name']):
        contribution = contribution[1]  # Details for current contributor
        name = contribution['name']  # Contributor name
        layout_id = contribution['layout_id']  # Layout ID
        doc = fitz.open(doc_templates['int_layouts'][layout_id])  # Open PDF template based on Layout ID

        print(f'Creating pages for {name}', end='')
        page_one = doc[0]  # First Page
        page_two = doc[1]  # Second Page
        if layout_id == 1:
            pdf_interior_layout_one(page_one, page_two, contribution, ix)  # Generate interior for current contributor
        elif layout_id == 2:
            pdf_interior_layout_two(page_one, page_two, contribution, ix)
        else:
            pdf_interior_layout_three(page_one, page_two, contribution, ix)
        page_two.set_rotation(0)  # Reset rotation to 0°
        doc.save(f'temp/{name}.pdf')  # Save temp file for current contributor
        int_pdf_list.append(f'temp/{name}.pdf')  # Add saved temp file to file list
        ix += 2  # Increment index by 2
        print('...Done')

    merger = PyPDF2.PdfMerger()  # Merge object to merge temp files
    print('Merging and saving book interior', end='')
    # Loop through pdf file list
    for file in int_pdf_list:
        merger.append(PyPDF2.PdfReader(file, 'rb'))  # Append file to merger object
    merger.write(
        f"{output_dir}/{book_dict['rec_name']}/{book_dict['rec_name']}_Interior.pdf")  # Save merged interior PDF
    print('...Done')
    # print('Compressing Interior PDF', end='')
    # reader = PyPDF2.PdfReader(f"{output_dir}/{book_dict['rec_name']}/{book_dict['rec_name']}_Interior_no_comp.pdf")
    # writer = PyPDF2.PdfWriter()
    #
    # for page in reader.pages:
    #     page.compress_content_streams()
    #     writer.add_page(page)
    # writer.add_metadata(reader.metadata)
    # writer.write(open(f"{output_dir}/{book_dict['rec_name']}/{book_dict['rec_name']}_Interior.pdf", 'wb'))
    # print('...Done')


def pdf_interior_layout_one(page_one: fitz.Page, page_two: fitz.Page, contribution: dict, page_num: int) -> None:
    """

    This function creates the first type of layout (message on first page with centered image on the second) 
    It should be used in a loop iterating through a iterable passing a dict (:param contribution) to the function. 
    
    :param page_one: fitz.Page object of the PDF template for the first Page of the layout
    :param page_two: fitz.Page object of the PDF template for the second Page of the layout
    :param contribution: Dict type object holding details for a single contribution
    :param page_num: Page number of the given contribution
    :return: None 
    
    """

    interior_name_rect = [70, 75, 400, 112]  # XYWH Coordinates for the name field on page one
    interior_text_rect = [70, 140, 565, 160]  # XYWH Coordinates for the message body field on page one
    interior_page_num_rect = [550, 580, 570, 590]  # XYWH Coordinates for the page number field on page one
    interior_img_rect = [70, 70, 560, 540]  # XYWH Coordinates for the image field on page two

    # Pages dictionary containing the page object, y axis limit for last text box, and starting text box coordinates
    pages_dict = {'page1': {'page': page_one, 'y_limit': 550, 'start_rect': interior_text_rect}}

    # INSERT NAME onto PAGE
    page_one.insert_textbox(interior_name_rect, contribution['name'], fontsize=fonts['int_name']['font_size'],
                            fontname=fonts['int_name']['font_name'], fontfile=fonts['int_name']['font_path'], align=0,
                            render_mode=0, fill=(0, 0, 0))

    # INSERT BODY onto PAGE(S)
    pdf_body_gen(pages_dict, contribution['msg'], fontsize=fonts['int_body']['font_size'],
                 fontname=fonts['int_body']['font_name'], fontfile=fonts['int_body']['font_path'],
                 align=TEXT_ALIGN_JUSTIFY,
                 render_mode=0, fill=(0, 0, 0))

    # INSERT PAGE NUM onto PAGE
    page_one.insert_textbox(interior_page_num_rect, str(page_num), fontsize=fonts['int_page_num']['font_size'],
                            fontname=fonts['int_page_num']['font_name'], fontfile=fonts['int_page_num']['font_path'],
                            align=1,
                            render_mode=0, fill=(0, 0, 0))

    # INSERT IMAGE onto PAGE
    if contribution['img_file'] != '':
        page_two.insert_image(interior_img_rect, filename=contribution['img_file'])
    else:
        try:
            interior_img_rect = [70, 300, 560, 540]  # XYWH Coordinates for the image field on page two
            author, quote = add_quote_to_blank()
            quote_end = pdf_body_gen(
                pages={'page1': {'page': page_two, 'y_limit': 560, 'start_rect': [70, 300, 560, 320]}}, msg=quote,
                fontsize=20, fontname=fonts['int_body']['font_name'], fontfile=fonts['int_body']['font_path'],
                align=TEXT_ALIGN_CENTER,render_mode=0, fill=(0, 0, 0), line_spacing=23)
            page_two.insert_textbox([70, quote_end[1] + 25, 545, 540], author, fontsize=13,
                                    fontname=fonts['int_body']['font_name'], fontfile=fonts['int_body']['font_path'],
                                    align=TEXT_ALIGN_RIGHT,)
        except IndexError:
            pass


def pdf_interior_layout_two(page_one: fitz.Page, page_two: fitz.Page, contribution: dict, page_num: int) -> None:
    """

    This function creates the second type of layout (message on first page and until the middle of the second page
    with a smaller centered image on the second)
    It should be used in a loop iterating through a iterable passing a dict (:param contribution) to the function.

    :param page_one: fitz.Page object of the PDF template for the first Page of the layout
    :param page_two: fitz.Page object of the PDF template for the second Page of the layout
    :param contribution: Dict type object holding details for a single contribution
    :param page_num: Page number of the given contribution
    :return: None

    """

    interior_name_rect = [70, 75, 400, 112]  # XYWH Coordinates for the name field on page one
    interior_text_rect = [70, 140, 565, 160]  # XYWH Coordinates for the message body field on page one
    interior_page_num_rect = [550, 580, 570, 590]  # XYWH Coordinates for the page number field on page one

    # Pages dictionary containing the page object, y axis limit for last text box, and starting text box coordinates
    pages_dict = {'page1': {'page': page_one, 'y_limit': 550, 'start_rect': interior_text_rect},
                  'page2': {'page': page_two, 'y_limit': 300, 'start_rect': [70, 35, 565, 55]}}

    # INSERT NAME onto PAGE
    page_one.insert_textbox(interior_name_rect, contribution['name'], fontsize=fonts['int_name']['font_size'],
                            fontname=fonts['int_name']['font_name'], fontfile=fonts['int_name']['font_path'], align=0,
                            render_mode=0, fill=(0, 0, 0))

    # INSERT BODY onto PAGE(S)
    page_two_rect_text = pdf_body_gen(pages_dict, contribution['msg'], fontsize=fonts['int_body']['font_size'],
                                      fontname=fonts['int_body']['font_name'], fontfile=fonts['int_body']['font_path'],
                                      align=TEXT_ALIGN_JUSTIFY,
                                      render_mode=0, fill=(0, 0, 0))

    # INSERT PAGE NUM onto PAGE
    page_one.insert_textbox(interior_page_num_rect, str(page_num), fontsize=fonts['int_page_num']['font_size'],
                            fontname=fonts['int_page_num']['font_name'], fontfile=fonts['int_page_num']['font_path'],
                            align=1,
                            render_mode=0, fill=(0, 0, 0))

    # INSERT IMAGE onto PAGE
    if contribution['img_file'] != '':
        interior_img_rect = [120, page_two_rect_text[1] + 20, 510,
                             550]  # XYWH Coordinates for the image field on page two
        page_two.insert_image(interior_img_rect, filename=contribution['img_file'])


def pdf_interior_layout_three(page_one: fitz.Page, page_two: fitz.Page, contribution: dict, page_num: int) -> None:
    """

    This function creates the third type of layout (message on both sides of the page)
    It should be used in a loop iterating through a iterable passing a dict (:param contribution) to the function.

    :param page_one: fitz.Page object of the PDF template for the first Page of the layout
    :param page_two: fitz.Page object of the PDF template for the second Page of the layout
    :param contribution: Dict type object holding details for a single contribution
    :param page_num: Page number of the given contribution
    :return: None

    """

    interior_name_rect = [70, 75, 400, 112]  # XYWH Coordinates for the name field on page one
    interior_text_rect = [70, 140, 565, 160]  # XYWH Coordinates for the message body field on page one
    interior_page_num_rect = [550, 580, 570, 590]  # XYWH Coordinates for the page number field on page one

    # Pages dictionary containing the page object, y axis limit for last text box, and starting text box coordinates
    pages_dict = {'page1': {'page': page_one, 'y_limit': 550, 'start_rect': interior_text_rect},
                  'page2': {'page': page_two, 'y_limit': 550, 'start_rect': [70, 35, 565, 55]}}

    # INSERT NAME onto PAGE
    page_one.insert_textbox(interior_name_rect, contribution['name'], fontsize=fonts['int_name']['font_size'],
                            fontname=fonts['int_name']['font_name'], fontfile=fonts['int_name']['font_path'], align=0,
                            render_mode=0, fill=(0, 0, 0))

    # INSERT BODY onto PAGE(S)
    pdf_body_gen(pages_dict, contribution['msg'], fontsize=fonts['int_body']['font_size'],
                 fontname=fonts['int_body']['font_name'], fontfile=fonts['int_body']['font_path'],
                 align=TEXT_ALIGN_JUSTIFY,
                 render_mode=0, fill=(0, 0, 0))

    # INSERT PAGE NUM onto PAGE
    page_one.insert_textbox(interior_page_num_rect, str(page_num), fontsize=fonts['int_page_num']['font_size'],
                            fontname=fonts['int_page_num']['font_name'], fontfile=fonts['int_page_num']['font_path'],
                            align=1,
                            render_mode=0, fill=(0, 0, 0))


def pdf_body_gen(pages: dict, msg: str, fontsize: int, fontname: str, fontfile: str, align: any, render_mode: int,
                 fill: tuple, line_spacing: int = 19) -> list:
    """

    A function to generate the message portion of the contribution. In order to have more flexibility, an addition of
    line spacing was added, this means the each line of the message is inserted one by one. Change the LINE_SPACING
    constant to increase or decrease spacing between lines. By default it is set to 20px

    :param pages: Page to insert message on
    :param msg: Message string to parse into text boxes
    :param fontsize: Font size to use
    :param fontname: Font name to use
    :param fontfile: Location of custom font
    :param align: Alignment of the text
    :param render_mode: Render mode of the text
    :param fill: Fill color of the text
    :param line_spacing: Spacing between each line of text
    :return: final rect_init values
    """

    def check_page_end(rect: list, y_limit: int) -> bool:
        """
        Check if current rectangle has reached the end of the pre-specified end of the current page
        :param rect: Text box rectangle
        :param y_limit: Y axis limit signifying the end of the page
        :return: Bool whether bottom of page was reached
        """

        if rect[3] > y_limit:
            return True
        else:
            return False

    LINE_SPACING = line_spacing  # Line spacing in px
    current_page = pages['page1']  # Initializing current page to page one
    rect_init = current_page['start_rect']  # Initializing starting rectangle
    WIDTH = rect_init[2] - rect_init[0]  # Text box width
    font = fitz.Font(fontname=fontname, fontfile=fontfile)  # Font to use for the text
    msg_list = msg.split('\n')  # Split message string by line break, creating a list

    # Loop through split message
    for ls in msg_list:
        if check_page_end(rect_init, y_limit=current_page['y_limit']):  # check if text box reached and of page
            if len(pages) > 1 and current_page != pages['page2']:  # check if any more pages are available
                current_page = pages['page2']  # Switch to page 2
                del rect_init
                rect_init = current_page['start_rect']  # re initialize starting rectangle
            else:
                break
        current_str = ''  # Current portion of the message to insert onto the page
        # Loop through each word of the current list, split by spaces
        for word in ls.split(' '):
            # Based on the font used, length of the current portion of the message is calculated
            # If the length plus the next word exceeds the width of the text box
            # The string will be inserted onto the page, else the word will be added to the string
            if font.text_length(current_str + ' ' + word, fontsize) >= WIDTH:
                current_page['page'].insert_textbox(rect_init, current_str, fontsize=fontsize, fontname=fontname,
                                                    fontfile=fontfile,
                                                    render_mode=render_mode, align=align, fill=fill)
                if check_page_end(rect_init, y_limit=current_page['y_limit']):  # check if text box reached and of page
                    if len(pages) > 1 and current_page != pages['page2']:  # check if any more pages are available
                        current_page = pages['page2']  # Switch to page 2
                        del rect_init
                        rect_init = current_page['start_rect']  # re initialize starting rectangle
                    else:
                        break
                current_str = word + ' '  # Reset current string after a line was inserted
                rect_init[1] += LINE_SPACING  # Increase the rec values to shift the next line by the line space value
                rect_init[3] += LINE_SPACING  # Increase the rec values to shift the next line by the line space value
            else:
                current_str += word + ' '
        current_page['page'].insert_textbox(rect_init, current_str, fontsize=fontsize, fontname=fontname,
                                            fontfile=fontfile,
                                            render_mode=render_mode, align=align, fill=fill)
        rect_init[1] += LINE_SPACING  # Increase the rec values to shift the next line by the line space value
        rect_init[3] += LINE_SPACING  # Increase the rec values to shift the next line by the line space value

    return rect_init


def add_quote_to_blank():
    """

    :return:
    """
    with open('templates/quotes/quotes.json') as file:
        quotes = json.load(file)
    quotes = {f"{i}": x for i, x in enumerate(quotes)}
    available_quotes = [x for x in quotes.keys() if x not in list(set(quotes_used))]
    chosen_quote = random.randint(0, len(set(available_quotes)))
    author = quotes[available_quotes[chosen_quote]]['author']
    quote = quotes[available_quotes[chosen_quote]]['quote']
    quotes_used.append(available_quotes[chosen_quote])
    return author, quote
