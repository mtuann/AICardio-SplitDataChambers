import math
import time
import cv2
import numpy as np
import PySimpleGUI as sg
import os


from config import *


class ButtonLayout:
    # mapping = {99: "not_view", 5: "other", 6: "no_chamber", 2: "bad", 3:"vinif", 4:"kc", 7: "3d"}
    mapping = {99: "not_view", 5: "other", 2: "bad", 3:"good"}
    
    rev_mapping = {value: key for key, value in mapping.items()}

    def __init__(self, case_notification, annotation):
        self.nofitication = case_notification
        if annotation is not None:
            #print("LOADING annotation: {}".format(annotation))
            self.cur_case_type = self.rev_mapping.get(annotation.get("TypeData", "get_type_data_fail"), "not_view")
            self.cur_case_comments = annotation.get("Comments", "")
            self.cur_case_chambers = annotation.get("Diagnosis", {})
        else:
            self.cur_case_type = 99
            self.cur_case_comments = ""
            self.cur_case_chambers = []

        self.__init_layout()

    def __init_layout(self):
        self.choose_case_button = self.__get_choose_case_button()
        self.checkbox_button = self.__get_checkbox_button()
        self.chambers = self.__get_dropdown_chamber()
        self.comment = self.__get_comment_section()

        self.save_button = self.__get_save_button()
        self.not_review_button = self.__get_not_review_button()

        layout = [
            self.choose_case_button,
            [sg.HorizontalSeparator(color="blue")],
            #self.chambers,
            self.comment,
            self.checkbox_button,
            # self.save_button,
            #self.not_review_button
        ]
        self.layout = sg.Column(layout, element_justification='center')

    def get_layout(self):
        return self.layout

    def update_saved(self):
        print('Saved')
        self.save_button[0].update(text='SAVED', button_color=("blue", "yellow"))

    def __get_dropdown_chamber(self):
        # multiple
        # return [sg.Listbox(values=['2C-3C-4C-PTS_S-PTS_L', '2C-3C-4C', '2C-4C', '2C', '4C', '3C', 'PTS_S', 'PTS_L', 'PW', 'CW', 'TDI_PW', "CLIP_COLOR"], 
        # "Normal", "YES", "LBBB", "Other", "Later_Check", "Postsystolic"],
        return [sg.Listbox(values=["Normal", "YES"], 
            select_mode='single', 
            default_values=self.cur_case_chambers,
            size=(30, 4), 
            enable_events=True, 
            key=f'{DROP_DOWN_CHAMBER}')]



    def get_all_annotation(self, values):
        case_type = "not_view"
        comments = ""
        chambers = []
        for key, value in values.items():
            if CHECKBOX_PREFIX in key:
                if value:
                    index = int(key.split('-')[-1])
                    case_type = self.mapping[index]
            elif COMMENT_PREFIX in key:
                comments = value
            elif DROP_DOWN_CHAMBER in key:
                chambers = value
        # print(case_type, comments)
        return case_type, comments, chambers

    def __get_not_review_button(self):
        button_config = {
            "border_width": 4,
            "button_color": ("red", "yellow"),
            "font": ("Arial", 13, "bold"),
            "enable_events": True,
            #"tooltip": "Click to save changes"
        }
        not_review_button = [
            sg.Button("NEXT",
                      key=f'{NOT_REVIEW_PREFIX}',
                      **button_config)
        ]
        return not_review_button

    def __get_save_button(self):
        button_config = {
            "border_width": 3,
            "button_color": ("red", "yellow"),
            "font": ("Arial", 13, "bold"),
            "enable_events": True,
            #"tooltip": "Click to save changes"
        }
        save_button = [
            sg.Button("SAVE ALL",
                      key=f'{SAVE_ALL_PREFIX}',
                      **button_config)
        ]
        return save_button

    def __get_comment_section(self):
        comment = [
            sg.Multiline(default_text=self.cur_case_comments,
                         size=(60, 5), 
                         font=("Arial", 12),
                         #enable_events=True,
                         key=COMMENT_PREFIX),
        ]
        return comment

    def __get_checkbox_button(self):
        radio_config = {
            "auto_size_text": True,
            "font": ("Arial", 12, "bold"),
            "pad": (3, 3),
            "text_color": "pink",
        }
        checkbox = [
            sg.Radio(f'{value}', "checkbox", default=key==self.cur_case_type,
                     key=f'{CHECKBOX_PREFIX}-{key}', **radio_config)
                for key, value in self.mapping.items()
        ]
        return checkbox

    def __get_choose_case_button(self):
        choose_case_button_config = {
            "border_width": 3,
            "button_color": ("red", "white"),
            "font": ("Arial", 13, "bold"),
            "enable_events": True,
        }

        choose_case_button = [
            sg.Button("PREV", key=f'{CHOOSE_CASE_PREFIX}-PREV', **choose_case_button_config),
            sg.Text(self.nofitication, size=(35, 1), font=("Arial", 15)),
            sg.Button("NEXT", key=f'{CHOOSE_CASE_PREFIX}-NEXT', **choose_case_button_config)
        ]

        return choose_case_button
