import PySimpleGUI as sg
import time
import io
import os
import imageio
import json
import imageio
import cv2
import numpy as np

from PIL import Image, ImageSequence
from config import PLAY_PAUSE_PREFIX, CHAMBER_ANNOTATION_PREFIX, OUT_JSON_CHAMBER_PATH
from concurrent.futures import ThreadPoolExecutor


class VideoLayout:
    WIDTH = 640
    HEIGHT = 480

    def __init__(self):
        self.file_data = None
        self.is_playing = False

        self.chamber_mapping = {0:'None/Other', 1:'2C', 2:'3C', 3:'4C'}
        self.inv_chamber_mapping = {value: key for key, value in self.chamber_mapping.items()}
        self.chamber_viewer = [
            sg.B(value, enable_events=True,
                 font=('Helvetica', 10, 'bold'),
                 button_color=('blue', 'white'),
                 key=CHAMBER_ANNOTATION_PREFIX+'-'+str(key),
                 border_width=3)
                for key, value in self.chamber_mapping.items()
        ]

        self.viewer = sg.Image(size=(self.WIDTH, self.HEIGHT),
                               background_color='black',)

        self.frame_text = sg.Text(size=(30, 1),
                                  text_color='yellow',
                                  justification='center',
                                  font=('Helvetica', 13))

        self.play_button = sg.B('PAUSE', enable_events=True,
                                border_width=3,
                                key=PLAY_PAUSE_PREFIX+'-PLAY',
                                font=('Helvetica', 10, "bold"),
                                button_color=('red', None))

        self.layout = [
                self.chamber_viewer,
                [self.viewer],
                [self.frame_text],
                [
                    sg.B('PREV', enable_events=True,
                         font=('Helvetica', 10),
                         key=PLAY_PAUSE_PREFIX+'-PREV',
                         border_width=3),
                    self.play_button,
                    sg.B('NEXT', enable_events=True,
                         font=('Helvetica', 10),
                         key=PLAY_PAUSE_PREFIX+'-NEXT',
                         border_width=3), 
                ],
        ]

        self.fviewer = sg.Frame('Video Player',
                            layout=self.layout,
                            title_color='blue',
                            font=('Helvetica', 15),
                            border_width=5,
                            vertical_alignment='top',
                            element_justification='center',)

    def get_layout(self):
        return self.fviewer

    def __encode_video(self, mp4):
        def encode(img):
            img = img[..., ::-1]
            buf = io.BytesIO()
            img = Image.fromarray(np.array(img)).save(buf, format='gif')
            return buf.getvalue()
        with ThreadPoolExecutor(8) as pool:
            frames = list(pool.map(encode, mp4))
        return frames

    def on_change(self, file_data):
        if self.file_data is not None and self.file_data[0] == file_data[0]:
            return

        self.file_data = file_data
        self.mp4 = imageio.get_reader(file_data[3], 'ffmpeg')
        self.frames = self.__encode_video(self.mp4)

        self.__reset()

    def __reset(self):
        self.is_playing = True
        self.frame_index = 0
        self.num_frame = len(self.frames)

        self.chamber = self.__get_chamber()
        if self.chamber != -1:
            event = f'chamber-{self.chamber}'
            self.update_chamber(event, None, is_init=False)
        else:
            for chamber_button in self.chamber_viewer:
                chamber_button.update(button_color=('blue', 'white'))

    def __get_chamber(self):
        case_id = self.file_data[4]
        rel_path = self.file_data[0]
        try:
            with open(OUT_JSON_CHAMBER_PATH, 'r') as f:
                data = json.load(f)
                chamber_dict = data.get(case_id, {}).get('chambers', {})
                chamber = chamber_dict.get(rel_path, -1)
                if chamber != -1:
                    chamber = self.inv_chamber_mapping[chamber]
        except Exception as e:
            print('error  here')
            print(e)
            return -1
        return chamber

    def __update(self):
        if self.file_data is None:
            return
        if self.is_playing is True:
            self.frame_index = (self.frame_index + 1) % self.num_frame

        self.frame_text.update(value=f'Frame {self.frame_index+1}')
        data = self.frames[self.frame_index]
        self.viewer.update(data=data)

    def __prev_next(self, value):
        if self.is_playing is False and self.file_data is not None:
            self.frame_index = (self.frame_index+value) % self.num_frame

    def update(self, event, values):
        if PLAY_PAUSE_PREFIX in event:
            action = event.split('-')[-1]
            if action == 'PLAY':
                self.__play_pause()
            if action == 'PREV':
                self.__prev_next(-1)
            if action == 'NEXT':
                self.__prev_next(1)
        self.__update()

    def update_chamber(self, event, values, is_init=False):
        if self.file_data is None:
            return

        key = int(event.split('-')[-1])
        if key == 0 and is_init is True:
            return

        for chamber_button in self.chamber_viewer:
            chamber_button.update(button_color=('blue', 'white'))
        self.chamber_viewer[key].update(button_color=('red', 'yellow'))
        self.__update_chamber_file(key, self.chamber_mapping[key])
        return (key, self.chamber_mapping[key])

    def __update_chamber_file(self, key, value):
        try:
            with open(OUT_JSON_CHAMBER_PATH, 'r') as f:
                data = json.load(f)
        except:
            data = {}

        case_id = self.file_data[4]
        rel_path = self.file_data[0]

        case_chamber_dict = data.get(case_id, None)
        if case_chamber_dict:
            chambers = case_chamber_dict.get('chambers', {})
            chambers[rel_path] = value
            case_chamber_dict['chambers'] = chambers
        else:
            case_chamber_dict = {
                'chambers': {rel_path: value}
            }

        #case_chamber_dict = data.get(case_id, {'chambers': {}}).get('chambers', {})
        #case_chamber_dict[rel_path] = value

        data[case_id] = case_chamber_dict
        with open(OUT_JSON_CHAMBER_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def __play_pause(self):
        if self.file_data is None:
            return
        if self.is_playing is True:
            self.is_playing = False
            self.play_button.update(text='PLAY', button_color=('green', None))
        else:
            self.is_playing = True
            self.play_button.update(text='PAUSE', button_color=('red', None))
