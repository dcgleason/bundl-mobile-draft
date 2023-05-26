doc_templates = {"back": {'sage': 'templates/sage_back.pdf',
                          'maroon': 'templates/maroon_back.pdf',
                          'ivory': 'templates/ivory_back.pdf',
                          'beige': 'templates/beige_back.pdf'},
                 "front": {'default': r'templates\pdf_templates\Cover.pdf',
                           'alt': 'templates/alt_front.pdf'},
                 "int_layouts": {1:'templates/pdf_templates/Inter.pdf',
                                 2:'templates/pdf_templates/Inter.pdf',
                                 3:'templates/pdf_templates/Inter.pdf'}
                 }
color_dict = {'sage': '#b2ac88',
              'maroon': '#ab2f2c',
              'ivory': '#fbfbf1',
              'beige': '#e6cc9c'}

fonts = {'cover': {'font_path': "fonts/AlexBrush-Regular.ttf",
                   'font_name': "AlexBrush-regular",
                   'font_size': 49},
         'int_name': {'font_path': 'fonts/Minion Pro Regular.ttf',
                      'font_name': 'MinionPro',
                      'font_size': 30},
         'int_body': {'font_path': 'fonts/Yu Gothic Light.ttf',
                      'font_name': 'YuGothic-light',
                      'font_size': 11.5},
         'int_page_num': {'font_path': 'fonts/Yu Gothic Light.ttf',
                          'font_name': 'YuGothic-light',
                          'font_size': 11}
         }

output_dir = 'output/'
