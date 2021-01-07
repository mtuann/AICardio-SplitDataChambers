import json
import cv2
import os
import numpy as np
import PySimpleGUI as sg
import math

from config import *


class Database:
    mapping = {99: "not_view", 1: "no_defined", 5: "other", 6: "no_chamber", 2: "bad", 3:"vinif", 4:"kc", 7: "3d"}
    # mapping = {99: "not_view", 5: "other", 6: "no_chamber", 2: "bad", 3:"vinif", 4:"kc", 7: "3d"}

    """
        'no_defined': 1,
        'bad': 2,
        'vinif': 3,
        'kc': 4,
        'other': 5,
        'no_chamber': 6,
        'none': 7,

    """
    # mapping = {99: "not_view", 0: "other", 1: "no_chamber", 2: "bad", 3:"vinif", 4:"kc"}


    def __init__(self):
        self.cur_id = 0
        self.annotation = {}

        self.__load_json()
        self.__load_case()

    def __load_json(self):
        with open(JSON_PATH, 'r') as file:
            self.data = json.load(file)

        try:
            with open(OUT_JSON_PATH, 'r') as file:
                self.annotation = json.load(file)
        except:
            pass

    def __check_case(self, levelData, diagnosis):
        if len(levelData) == 0:
            return True
        return len(diagnosis) == 0 and levelData != "bad"

    def __load_case(self):
        self.case_list = []
        for case_id, case_data in self.data.items():
            case_level = ""

            case_level = JSON_ORDER_MAPPING.get(case_level, -1)

            list_dicom_data = []
            for file_data in case_data['ListFileDicom']:
                if 'PixelData' not in file_data:
                    continue

                relative_path = file_data['RelativePath']
                num_frame = file_data.get('NumberOfFrames', 1)

                jpg_path = file_data.get('RelativePath')
                jpg_path = os.path.join(REPRESENTATION_ROOT, case_id, jpg_path+'.jpg')

                mp4_path = file_data.get('RelativePath')
                mp4_path = os.path.join(REPRESENTATION_ROOT, case_id, mp4_path+'.mp4')

                chamber = self.__get_chamber(case_id, relative_path)
                list_dicom_data.append([relative_path, num_frame, jpg_path, mp4_path, case_id, case_level, chamber])

            if len(list_dicom_data) > 0:
                list_dicom_data = sorted(list_dicom_data, key=lambda x: -int(x[1]))
                self.case_list.append(list_dicom_data)

        self.num_cases = len(self.case_list)
        self.case_list = sorted(self.case_list, key=lambda x: x[0][5])

        self.__get_first_not_done()
        # self.__getCurID()

    def __get_first_not_done(self):
        try:
            with open(OUT_JSON_CHAMBER_PATH, 'r') as f:
                data = json.load(f)
                list_key = list(data.keys())
            with open(OUT_JSON_PATH, 'r') as f:
                data = json.load(f)
                list_key.extend(list(data.keys()))

            while self.case_list[self.cur_id][0][4] in list_key:
                #print(self.case_list[self.cur_id][0][4])
                self.cur_id += 1
                if self.cur_id >= len(self.case_list):
                    self.cur_id = 0
                    break
            print(self.cur_id)
        except:
            print('no out json chamber file')

    def getCurID(self):
        for idx, case in enumerate(self.case_list):
            case_id = case[0][4]
            if case_id not in self.annotation:
                return idx
        return 0

    def __save_json(self):
        with open(OUT_JSON_PATH, 'w') as file:
            json.dump(self.annotation, file, indent=2)

    def get_current_case(self, isPrevNext=True):
        # set case not review if isPrevNext = False
        if not isPrevNext:
            self.cur_id = self.getCurID()

        print("\n","---"*20)
        print("Loading to case id: {} -- {}".format(self.cur_id + 1, self.mapping.get(self.case_list[self.cur_id][0][5]), "not_view"))

        case_notification = f'Case: {self.cur_id+1}/{len(self.case_list)}'
        case_id = self.case_list[self.cur_id][0][4]
        annotation = self.annotation.get(case_id, None)

        if annotation is None:
            TypeData = self.mapping.get(self.case_list[self.cur_id][0][5], "not_view")
            if TypeData != "no_defined":
                annotation = {
                    "TypeData" : self.mapping.get(self.case_list[self.cur_id][0][5], "not_view"),
                    "Chambers": [],
                    "Comments": []
                }
        return self.case_list[self.cur_id], case_notification, annotation

    def get_prev_case(self):
        self.cur_id = (self.cur_id - 1) % len(self.case_list)
        return self.get_current_case(isPrevNext=True)

    def get_next_case(self):
        self.cur_id = (self.cur_id + 1) % len(self.case_list)
        return self.get_current_case(isPrevNext=True)

    def on_change(self, event):
        value = event.split('-')[-1]

        if value == 'PREV':
            return self.get_prev_case()
        if value == 'NEXT':
            return self.get_next_case()

        # else get case not review
        print("GO TO NOT REVIEW CASE")
        return self.get_current_case()

    def update_annotation(self, case_type, comments, chambers):
        case_id = self.case_list[self.cur_id][0][4]  # case->first_file->case_id
        # print("VALUE AT COMMENT: {}  {} -- {}".format(comments[-1], ord(comments[-1]), len(comments)))
        #if ord(comments[-1]) == 10:
            #comments = comments[:-1]

        data_update = {
            "TypeData" : case_type,
            "Chambers": chambers,
            "Comments": comments
        }

        if case_type != "not_view":
            print("update_annotation idx: {} -- {}".format(self.cur_id + 1, data_update))
            # print("TYPE DATA: {} --- {}".format(type(chambers), chambers))
            # print("LEN comments: {}".format(len(comments)))
            self.annotation[case_id] = data_update
            print("---"*20,"\n")

            # [case_type, comments]
            self.__save_json()

    def __get_chamber(self, case_id, rel_path):
        try:
            with open(OUT_JSON_CHAMBER_PATH, 'r') as f:
                data = json.load(f)
                chamber_dict = data.get(case_id, {}).get('chambers', {})
                chamber = chamber_dict.get(rel_path, '')
        except:
            chamber = ''
        return chamber
