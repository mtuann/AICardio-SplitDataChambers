import os
import glob
import json
import shutil
import pydicom
import cv2
import imageio
import numpy as np

def readFileJSON(file):
    with open(file, "r") as fr:
        return json.load(fr)

    
def writeDataToJSON(data, file):
    with open(file, "w") as fw:
        json.dump(data, fw)
    fw.close()
    
    
def viewData(data, numView=5):
    for idx, (k, v) in enumerate(data.items()):
        if idx == numView:
            break
        print(idx, k, v)

    
def getDataFromJSON(data, key, default="no"):
    
    if key in data: 
        return data[key]["value"] 
    else:
        return default
    
    
def set_copy_file_same_time(file_src, file_des):
    mtime = os.path.getmtime(file_src)
    atime = os.path.getatime(file_src)
    os.utime(file_des, (atime, mtime))
    
    
def getFiles(folder="/data.local/data/dicom_data_20200821"):
    files = glob.glob(os.path.join(folder, "**"), recursive=True)
    return [f for f in files if os.path.isfile(f)]




class GenerateTrainData():
    
    def __init__(self, path_file_dicom="/media/tuan/DATA/AI-Cardio/modules/Screen01/train_20200820_4011_cases_72730_files_sorted_time.json"):
        self.data_dicom = readFileJSON(path_file_dicom)

        # self.TypeData = ["train"]
        # self.levelData = ["vinif", "kc", "bad", "no_defined"]
        # self.NumberOfDicoms = 0
        # self.dataFiles = {}
        # self.missFileMP4 = 0
        # self.missFileJPG = 0

        # self.generateData()
        
        self.dataMobile()


#         self.countingFolder()
    
    def getDataDeltaXY(self, dataDelta):
        # [{'PhysicalDeltaX': '0.022980796208341193', 'PhysicalDeltaY': '0.022980796208341193'}, {'PhysicalDeltaX': '0.022980796208341193', 'PhysicalDeltaY': '0.022980796208341193'}]
        result = {}
        for idx, value in enumerate(dataDelta):
            PhysicalDeltaX = float(value["PhysicalDeltaX"])
            PhysicalDeltaY = float(value["PhysicalDeltaY"])
            if PhysicalDeltaY == PhysicalDeltaX and PhysicalDeltaY > 0:
                result["PhysicalDeltaY"] = PhysicalDeltaY
                result["PhysicalDeltaX"] = PhysicalDeltaX
                break
        return result




    def dataMobile(self):
        
        data = {}

        for idx, (key, value) in enumerate(self.data_dicom.items()):
            ListFileDicom = value["ListFileDicom"]
            AddDataMap = value["AddDataMap"]
            # print(AddDataMap)
            # {'InstitutionName': 'BV VL', 'AcquisitionDateTime': '20181114012000.000', 'PatientName': 'Tran Trung Tin', 
            # 'ReferringPhysicianName': 'BS. Vu Thi Phuong', 'StudyInstanceUID': '1.2.840.113663.1500.1.420121243.1.1.20180515.83948.356', 
            # 'IDStudy': '000919', 'NumberOfDicom': 6}


            # return
            # print(ListFileDicom)
            # break
            StudyInstanceUID = AddDataMap["StudyInstanceUID"]

            data[StudyInstanceUID] = {}
            
            data[StudyInstanceUID]["IDStudy"] = AddDataMap["IDStudy"]

            data[StudyInstanceUID]["NumberOfDicom"] = AddDataMap["NumberOfDicom"]
            data[StudyInstanceUID]["ListFileDicom"] = []


            for idy, fileDicom in enumerate(ListFileDicom):
                fileInfo = {}

                fileInfo["SequenceOfUltrasoundRegions"] = self.getDataDeltaXY( fileDicom.get("SequenceOfUltrasoundRegions", []) )

                fileInfo["RelativePath"] = fileDicom.get("relative_path", "")
                fileInfo["NumberOfFrames"] = fileDicom.get("NumberOfFrames", 1)
                
                fileInfo["PixelData"] = fileDicom.get("PixelData", "NotIMG")

                data[StudyInstanceUID]["ListFileDicom"].append(fileInfo)

                # break
            # break

#             self.handleStudy(value, mapTime, mapLevelData)
            # {'no_defined': 2006, 'vinif': 577, 'bad': 688, 'kc': 631, 'other': 107, 'not_found_img': 2}
            # {'no_defined': 2004, 'vinif': 577, 'bad': 688, 'kc': 631, 'other': 111}

            if idx % 200 == 0:
                print("process to: {} / {}".format(idx + 1, len(self.data_dicom)))

        writeDataToJSON(data, "./data_mobile_202009.json")

        # print(data)

        return True

    def generateData(self):
        print("LEN DATA: {}".format(len(self.data_dicom)))
        mapLevelData = {}
        # print(self.data_dicom["b'1.2.999.999.99.9.9999.8888'"])
        # exit(0)
        # 'StudyDescription': '', 'PixelData': [95, 600, 800, 3], 

        # 'SequenceOfUltrasoundRegions': [{'PhysicalDeltaX': '0.024619547072563842', 'PhysicalDeltaY': '0.024619547072563842'}], 
        # 'NumberOfFrames': '95', 'Rows': '600', 'Columns': '800', 'FrameTime': '17.053', 'HeartRate': '72', 
        # 'relative_path': '1.2.840.113663.1500.1.420121243.3.1.20180515.84005.369____IM_0020'}
        


        for idx, (key, value) in enumerate(self.data_dicom.items()):

            if key == "b'1.2.999.999.99.9.9999.8888'":
                continue

#             self.handleStudy(value, mapTime, mapLevelData)
            # {'no_defined': 2006, 'vinif': 577, 'bad': 688, 'kc': 631, 'other': 107, 'not_found_img': 2}
            # {'no_defined': 2004, 'vinif': 577, 'bad': 688, 'kc': 631, 'other': 111}

            if idx % 200 == 0:
                print("process to: {} / {}".format(idx + 1, len(self.data_dicom)))
        
            levelData = value["levelData"]

            if levelData in self.levelData:
                self.handleStudy(value)


            if levelData not in mapLevelData:
                mapLevelData[levelData] = 0
            mapLevelData[levelData] += 1
            
        print(mapLevelData)
        print(self.NumberOfDicoms)
        print(self.missFileJPG)
        print(self.missFileMP4)


    def DumpRepresentation(self, dicom_path, FOLDER_DUMP="/media/tuan/DATA/AI-Cardio/dicom_data_20200821_map_bv/miss_rep"):
        try:    
            dataset = pydicom.dcmread(dicom_path)
            images = self.convert_images(dataset.pixel_array)
            thumbnail = self.get_thumbnail(images)
            StudyInstanceUID = dataset[0x0020,0x000D].value
            SOPInstanceUID = dataset[0x0008,0x0018].value

            basename = os.path.basename(dicom_path).split("____")[-1]
            # print(basename)
            # print(StudyInstanceUID)
            # print(SOPInstanceUID)
            root_representation_folder = os.path.join(FOLDER_DUMP, StudyInstanceUID)
            os.makedirs(root_representation_folder, exist_ok=True)

            root_representation = os.path.join(FOLDER_DUMP, StudyInstanceUID, f'{SOPInstanceUID}____{basename}')
            print(root_representation)
            # exit(0)
            cv2.imwrite(f'{root_representation}.jpg', thumbnail)

            fps = 30
            try:
                fps = dataset[0x0018,0x1063].value
            except:
                pass

            imageio.mimwrite(f'{root_representation}.mp4', images, fps=fps, macro_block_size=1, quality=5)

        except Exception as e:
            print("Error Reading dicom: {}".format(e))

    def compress_mp4(self, imgs, out_path, fps=30):
        imageio.mimwrite(out_path, imgs, fps=fps, macro_block_size=1, quality=5)
        
        
    def get_thumbnail(self, images, index=10):
        # print(images.shape)
        # exit(0)
        if images.shape[0] > index:
            return images[index, ...]
        return images[-1, ...]


    def convert_images(self, images):
        # convert to N*H*W*3
        if len(images.shape) == 2:
            # only one GRAY frame
            images = np.stack([images]*3).transpose(1, 2, 0)[None,...]
        elif len(images.shape) == 3:
            if images.shape[-1] <= 3:
                images = images[None, ...]
                # only one RGB frame
            else:
                # video of GRAY frames
                images = np.repeat(images[..., None], 3, axis=-1)
        else:
            # video of RGB frames
            pass
        return images

    def  make_grid(self, imgs, margin=2, w = 5):

        img_h, img_w, img_c = imgs[0].shape

        m_x = int(margin)
        m_y = m_x
        h = math.ceil(len(imgs) / w)
        n = w*h

        imgmatrix = np.zeros((img_h * h + m_y * (h - 1),
                              img_w * w + m_x * (w - 1),
                              img_c),
                             np.uint8)

        imgmatrix.fill(255)    

        for x_i in range(w):
            for y_i in range(h):
                if y_i*w+x_i >= len(imgs): continue
                img = imgs[y_i*w+x_i]
                
                if len(img.shape) == 2:
                    img = np.repeat(img[..., None], 3, axis=-1) 
                # print(y_i*w+x_i, img.shape, type(img))
                x = x_i * (img_w + m_x)
                y = y_i * (img_h + m_y)
                imgmatrix[y:y+img_h, x:x+img_w, :] = img

        return imgmatrix


    def __init_grid(self, imgs):

        nrows, block_size, margin = self.nrows, self.block_size, self.margin
        imgs, labels = self.thumbnails, self.labels

        ncols = math.ceil(len(imgs) / nrows)

        n_blocks = ncols * nrows

        img_matrix = np.ones((block_size*nrows + margin*(nrows-1),
                             block_size*ncols + margin*(ncols-1),
                             3), np.uint8) * 255

        n_imgs = imgs.shape[0]
        for col in range(ncols):
            for row in range(nrows):
                i_block = col * nrows + row #row*ncols + col
                if i_block >= n_imgs:
                    continue

                # get image at index i
                img = imgs[i_block]
                label = labels[i_block]
                img = cv2.resize(img, (block_size, block_size))
                img = cv2.putText(img, f'{self.imgs_data[i_block].shape[0]}-{label}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (37, 200, 37), 2)

                # calc image position
                x = col * (block_size + margin)
                y = row * (block_size + margin)
                img_matrix[y:y+block_size, x:x+block_size] = img

        self.img_matrix = img_matrix
        self.grid = img_matrix.copy()

        self.win_width = img_matrix.shape[1]


    def handleStudy(self, studyDetail, FOLDER_REPRESENTAION="/media/tuan/DATA/AI-Cardio/dicom_data_20200821_map_bv/representation"):
        # check time and set Index 6D for data

        TypeData = studyDetail["TypeData"]
        levelData = studyDetail["levelData"]
        StudyInstanceUID = studyDetail["ListFileDicom"][0]["StudyInstanceUID"]
        AcquisitionDateTime = studyDetail["AddDataMap"]["AcquisitionDateTime"]
        AddDataMap = studyDetail["AddDataMap"]
        
        InstitutionName = AddDataMap["InstitutionName"]
        AcquisitionDateTime = AddDataMap["AcquisitionDateTime"]
        PatientName = AddDataMap["PatientName"]
        ReferringPhysicianName = AddDataMap["ReferringPhysicianName"]
        ListFileDicom = studyDetail["ListFileDicom"]

        self.NumberOfDicoms += len(ListFileDicom)

        ImageMatrixInfor = []


        for idx, fileDicom in enumerate(ListFileDicom):
            StudyInstanceUID = fileDicom["StudyInstanceUID"]
            SOPInstanceUID = fileDicom["SOPInstanceUID"]

            relative_path = fileDicom["relative_path"]
            full_path = os.path.join(FOLDER_REPRESENTAION, StudyInstanceUID, relative_path)
            # full_path_dicom = full_path.replace("representation", "train")

            # print(full_path, os.path.isfile(full_path))
            # if not os.path.isfile(full_path):
            #     print("DM DICOM NOT EXIST: {}".format(full_path))

            # if full_path not in self.dataFiles:
            #     self.dataFiles[full_path] = relative_path
            # else:

            #     print("StudyInstanceUID: {}".format(StudyInstanceUID))
            #     print("DM MISS: {}".format(self.dataFiles[full_path]))
            #     print("relative_path: {}".format(relative_path))

            if "PixelData" in fileDicom:
                # pass
                # PixelData = fileDicom["PixelData"]
                path_mp4 = full_path + ".mp4"
                path_jpg = full_path + ".jpg"

                # print(path_mp4, os.path.isfile(path_mp4))
                # print(path_jpg, os.path.isfile(path_jpg))
                NumberOfFrames = 1
                if "NumberOfFrames" in fileDicom:
                    NumberOfFrames = fileDicom["NumberOfFrames"]


                if not os.path.isfile(path_mp4) or not os.path.isfile(path_jpg):
                    # print(full_path, fileDicom["PixelData"])
                    # self.missFileJPG += 1
                    # self.DumpRepresentation(full_path_dicom)
                    print("Miss representation: {}".format(full_path))

                else:
                    ImageMatrixInfor.append([idx, path_mp4, path_jpg, NumberOfFrames])
                    # pass
                    # concatinate -> 1 anh dai dien cho toan bo folder


                # if not os.path.isfile(path_mp4):
                #     # print("MISS FILE MP4: {}".format(path_mp4))
                #     FOLDER_MISS = "/media/tuan/DATA/AI-Cardio/dicom_data_20200821_map_bv/miss_rep"
                #     full_path_miss = os.path.join(FOLDER_MISS, StudyInstanceUID, relative_path)
                #     if os.path.isfile(full_path_miss):
                #         continue
                #     else:
                #         os.makedirs(os.path.dirname(full_path_miss), exist_ok=True)
                #         shutil.copy(full_path_dicom, full_path_miss)

                #     # self.missFileMP4 += 1


                # if not os.path.isfile(path_jpg):
                #     # print("MISS FILE JPG: {}".format(path_jpg))
                #     # self.missFileJPG += 1
                #     full_path_miss = os.path.join(FOLDER_MISS, StudyInstanceUID, relative_path)
                #     if os.path.isfile(full_path_miss):
                #         continue
                #     else:
                #         os.makedirs(os.path.dirname(full_path_miss), exist_ok=True)
                #         shutil.copy(full_path_dicom, full_path_miss)
                
                
                # SequenceOfUltrasoundRegions = fileDicom["SequenceOfUltrasoundRegions"]
            else:
                pass

            
                # relative_path = fileDicom["relative_path"]
            # NumberOfFrames, Rows, Columns, FrameTime, HeartRatem
        # exit(0)   

    def countingFolder(self, ROOT_FOLDER = "/data.local/data/dicom_data_20200821_raw/train"):
        listDATA = ["bad", "kc", "no_defined", "not_found_img", "other", "vinif"]
        for ty in listDATA:
            path_folder = os.path.join(ROOT_FOLDER, ty)
            print("path_folder: {} -- len: {}".format(path_folder, len(os.listdir(path_folder))))
            
        data2979 = readFileJSON("/data.local/tuannm/Utils-DICOM-GEN-Loading/anonymous_dicom/data_vinif_kc_2979_cases_20200821.json")
        
        mapLevelData = {}
        
        for k, v in data2979.items():
            if v not in mapLevelData:
                mapLevelData[v] = 0
            mapLevelData[v] += 1
        print(mapLevelData)

    def checkMediaType(self, studyDetail):

        ListFileDicom = studyDetail["ListFileDicom"]
        levelData = studyDetail["levelData"]
        
        if levelData == "not_found_img":
            
            studyDetail["levelData"] = "no_defined"
            
        for idx, fileDicom in enumerate(ListFileDicom):
            StudyInstanceUID = fileDicom["StudyInstanceUID"]
            


            if "NumberOfFrames" in fileDicom:
                NumberOfFrames = fileDicom["NumberOfFrames"]
                try:
                    NumberOfFrames = int(NumberOfFrames)
                    if NumberOfFrames > 1:
                        studyDetail["TypeMedia"] = "video"    
                        return
                    
                except Exception as e:
                    print("Exception: {} -- {}".format(e, NumberOfFrames))
                    
        studyDetail["TypeMedia"] = "text_image"
        studyDetail["levelData"] = "other"

    def removeDuplicatedDate(self):
        
        mapLevelData = {}

        keyDuplicated = "1.2.840.113663.1500.1.420121243.1.1.20181016.84125.935"

        dataDuplicated = self.data_dicom[keyDuplicated]["ListFileDicom"]

        uniqueData = {}
        removeDuplicated = dataDuplicated[:8]
        self.data_dicom[keyDuplicated]["ListFileDicom"] = removeDuplicated

        writeDataToJSON(self.data_dicom, "./train_20200820_4011_cases_72730_files.json")
        
        print("DONE write to file: {}".format("./train_20200820_4011_cases_72730_files.json"))

        # print(len(removeDuplicated))
        # for idx, fileDicom in enumerate(removeDuplicated):
        #     print(idx, fileDicom["relative_path"])
        # print(len(dataDuplicated))
        # for idx, fileDicom in enumerate(dataDuplicated):

        #     StudyInstanceUID = fileDicom["StudyInstanceUID"]
        #     SOPInstanceUID = fileDicom["SOPInstanceUID"]

        #     relative_path = fileDicom["relative_path"]
        #     if relative_path not in uniqueData:
        #         uniqueData[relative_path] = True

        #     else:
        #         print(idx, relative_path)



        

# print(len(getFiles("/media/tuan/DATA/AI-Cardio/dicom_data_20200821_map_bv/train")))
     
generateTrainData = GenerateTrainData()
