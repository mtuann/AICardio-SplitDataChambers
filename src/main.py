import json
import cv2
import os
import numpy as np
import math
import PySimpleGUI as sg

from config import *
from dataloader import *
from button_layout import ButtonLayout
from grid_layout import GridLayout
from video_layout import VideoLayout


sg.ChangeLookAndFeel('DarkAmber')


def get_window_layout(current_case, case_notification, annotation=None):
    grid = GridLayout(current_case)
    button = ButtonLayout(case_notification, annotation)
    video_player = VideoLayout()

    sidebar = [[button.get_layout()], [sg.HorizontalSeparator(color="blue")], [grid.get_layout()]]
    sidebar = sg.Column(layout=sidebar,
                        element_justification='center',
                        vertical_alignment='top')
    window_layout = [
        [sidebar, sg.VerticalSeparator(color='blue'), video_player.get_layout()]
    ]
    window = sg.Window(layout=window_layout, **WINDOW_CONFIG)
    #window.finalize() # TODO del this line too
    #window.move(2000, 2000)  # TODO del this line to not move the window

    return window, button, grid, video_player


if __name__ == '__main__':
    database = Database()
    case_data, case_notification, annotation = database.get_current_case()

    #print(case_data, case_notification, annotation)
    window, button, grid, video_player = get_window_layout(case_data, case_notification, annotation)
    while True:
        event, values = window.read(timeout=WINDOW_TIMEOUT)
        if event == sg.WIN_CLOSED:
            break

        video_player.update(event, values)

        if GRID_PREFIX in str(event):
            try:
                file_data = grid.update_event(event)
                video_player.on_change(file_data)
            except Exception as e:
                print("Error case {} \n-- {}".format(file_data, e))
                print("---"*20)
                # UPDATE DATA
                case_type, comments, chambers = button.get_all_annotation(values)
                # print("NOT_REVIEW_PREFIX case_type: {} comments: {}".format(case_type, comments))
                print(case_type, comments, chambers)
                database.update_annotation("other", "Error-CASE", chambers)

                new_case_data, new_case_notification, annotation = database.on_change(event)

                # button.update_saved()

                window.close()

                window, button, grid, video_player = get_window_layout(new_case_data, new_case_notification, annotation)
                continue

        if CHAMBER_ANNOTATION_PREFIX in str(event):
            chamber_value = video_player.update_chamber(event, values)
            if chamber_value:
                key, c_value = chamber_value
                grid.update_chamber(c_value)
            print(chamber_value)

        if CHOOSE_CASE_PREFIX in str(event):
            case_type, comments, chambers = button.get_all_annotation(values)
            # print("case_type: {} comments: {}".format(case_type, comments))
            database.update_annotation(case_type, comments, chambers)

            new_case_data, new_case_notification, annotation = database.on_change(event)

            # case_type, comments = button.get_all_annotation(values)
            # database.update_annotation(case_type, comments)

            window.close()
            window, button, grid, video_player = get_window_layout(new_case_data, new_case_notification, annotation)

        """
        if SAVE_ALL_PREFIX in str(event):
            case_type, comments, chambers = button.get_all_annotation(values)
            database.update_annotation(case_type, comments, chambers)
            button.update_saved()

        # if DROP_DOWN_CHAMBER in str(event):
        #     # print("USING DROP_DOWN_CHAMBER")
        #     case_type, comments, chambers = button.get_all_annotation(values)
        #     print("{} comments = {} {}".format(case_type, comments, chambers))


        if NOT_REVIEW_PREFIX in str(event):
            print("\n")
            print("---"*20)
            # UPDATE DATA
            case_type, comments, chambers = button.get_all_annotation(values)
            # print("NOT_REVIEW_PREFIX case_type: {} comments: {}".format(case_type, comments))
            database.update_annotation(case_type, comments, chambers)

            new_case_data, new_case_notification, annotation = database.on_change(event)

            # button.update_saved()
            window.close()
            window, button, grid, video_player = get_window_layout(new_case_data, new_case_notification, annotation)
        """
    window.close()
