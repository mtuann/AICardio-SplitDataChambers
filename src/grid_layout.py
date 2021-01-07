import math
import io
import cv2
import numpy as np
import PySimpleGUI as sg
import os
import tqdm


from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from config import GRID_PREFIX


def encode_img(img):
    ## cv2 img (BGR)
    img = img[..., ::-1]  # to RGB
    buf = io.BytesIO()
    img = Image.fromarray(img).save(buf, format='gif')
    img = buf.getvalue()
    return img

class GridLayout:
    BUTTON_WIDTH = 128
    BUTTON_HEIGHT = 128
    NUM_COLS = 4
    MAX_HEIGHT = 720

    def __init__(self, case_data):
        self.case_data = case_data
        self.loadingImageNumber =  0

        self.__reset(case_data)
        self.__init_layout()

    def __reset(self, case_data):
        self.num_buttons = len(case_data)
        self.case_data = case_data
        self.file_index = -1

        def read_img(file_data):
            # self.loadingImageNumber += 1

            # print("Loading done: {} / {}".format(self.loadingImageNumber, len(case_data)))

            img = cv2.imread(file_data[2])
            img = cv2.resize(img, (self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
            img = cv2.putText(img, f'{file_data[1]}', (20, 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
            img = cv2.putText(img, f' {file_data[6]}', (20, 40),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
            img = encode_img(img)
            return img
        #self.images = [read_img(file_data) for file_data in self.case_data]
        with ThreadPoolExecutor(8) as pool:
            # self.images = list(pool.map(read_img, self.case_data))
            # r = list(tqdm.tqdm(p.imap(_foo, range(30)), total=30))
            self.images = list(tqdm.tqdm(pool.map(read_img, self.case_data), total=len(case_data)))

    def __init_layout(self):
        self.NUM_ROWS = math.ceil(self.num_buttons / self.NUM_COLS)
        self.button_layout = [[self.__get_button(i, j)
                               for j in range(self.NUM_COLS)]
                                   for i in range(self.NUM_ROWS)]
        padding = 15
        layout_width = self.NUM_COLS * (self.BUTTON_WIDTH + padding) + 25
        layout_height = min(self.MAX_HEIGHT, self.NUM_ROWS * (self.BUTTON_HEIGHT + padding))
        self.layout = sg.Column(self.button_layout,
                                size=(layout_width, layout_height),
                                pad=(5, 5),
                                scrollable=True,
                                #justification='center',
                                vertical_scroll_only=True,
                                element_justification='center',
                                vertical_alignment='top',
                                key='GRID_LAYOUT',
                                )

    def __get_button(self, i, j):
        button_key = f'{GRID_PREFIX}-{i}-{j}'
        visible = (i*self.NUM_COLS + j) < self.num_buttons
        if visible:
            button_image = self.images[i*self.NUM_COLS + j]
        else:
            button_image = None

        button = sg.Button('',
                           image_data=button_image,
                           visible=visible,
                           button_color=('yellow', 'white'),
                           key=button_key)
        return button

    def get_layout(self):
        return self.layout

    def update_event(self, event):
        i, j = list(map(int, event.split('-')[-2:]))
        self.file_index = i*self.NUM_COLS + j
        self.old_i = i
        self.old_j = j
        for row in self.button_layout:
            for button in row:
                button.update(button_color=('yellow', 'white'))
        self.button_layout[i][j].update(button_color=('red', 'red'))
        return self.case_data[self.file_index]

    def update_chamber(self, c_value):
        if self.file_index == -1:
            return
        self.case_data[self.file_index][6] = c_value
        file_data = self.case_data[self.file_index]
        img = cv2.imread(file_data[2])
        img = cv2.resize(img, (self.BUTTON_WIDTH, self.BUTTON_HEIGHT))
        img = cv2.putText(img, f'{file_data[1]}', (20, 20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        img = cv2.putText(img, f' {file_data[6]}', (20, 40),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        img = encode_img(img)
        self.images[self.file_index] = img
        self.button_layout[self.old_i][self.old_j].update(image_data=img)

    def on_change(self, case_data):
        self.__reset(case_data)
