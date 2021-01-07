import json
import os
import glob


def readFileJSON(json_path):
    with open(json_path, "r") as fr:
        data = json.load(fr)
    print("Len data file: {} -- {}".format(json_path, len(data)))
    return data

list_files_dicom_info = [
    "/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/Ref-20201230.json",
    "/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20201219_4076_cases.json",
]

class Set6DIndexStudy():
    def __init__(self, data_json=""):
        
        # self.data_dicom = readFileJSON(data_json)
        
        # self.SetIndex6D()
        # self.splitDATA()
        self.moveDATA()
    

    def checkDataCase(self, data_case):
        listFileDicom = data_case["ListFileDicom"]
        for idx, file in enumerate(listFileDicom):
            numberOfFrames = 1
            try:
                numberOfFrames = int(file["NumberOfFrames"])
            except Exception as e:
                pass
            if numberOfFrames > 1:
                return True

        return False

    def SetIndex6D(self, id_start=4077):

        data_dicom = readFileJSON(list_files_dicom_info[0])
        newData = {}
        dataTime = {}
        for idx, (k, study_detail) in enumerate(data_dicom.items()): 
            if self.checkDataCase(study_detail):

                dataTime[k] = study_detail["AddDataMap"]["AcquisitionDateTime"]
            listFileDicom = study_detail["ListFileDicom"]
            for f in listFileDicom:
                f["RelativePath"] = f["RelativePath"].split("/")[-1]
        
        sortedData = sorted(dataTime, key=lambda kv: kv[1]) # kv[0]; key, kv[1]: value
        dataCntTime = {}
        print(len(sortedData))
        for idx, value in enumerate(sortedData):
            # print(idx, value)
            dataCntTime[value] = f'{id_start + idx:06d}'
            # print(idx, value, dataCntTime[value])
            # if idx == 20:
            #     break
        data_dicom_02 = readFileJSON(list_files_dicom_info[1])
        for idx, (k, study_detail) in enumerate(data_dicom_02.items()): 
            newData[k] = data_dicom_02[k]

        for idx, (k, study_detail) in enumerate(data_dicom.items()): 
            if k in dataCntTime:
                newData[k] = {}

                newData[k]["ListFileDicom"] = study_detail["ListFileDicom"]
                newData[k]["StudyInformation"] = study_detail["AddDataMap"]
                newData[k]["StudyInformation"]["IDStudy"] = dataCntTime[k]
                newData[k]["StudyInformation"]["NumberOfDicom"] = len(study_detail["ListFileDicom"])
                
                # "NumberOfDicom"

        

        print("Len newData: {}".format(len(newData)))
        fn = "/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20210101_5374_cases.json"
        with open(fn, "w") as fw:
            json.dump(newData, fw, indent=2)
        print("Done write to file: {}".format(fn))

        
        # print(len(sortedData))

        namePeople = ["TuanNM", "DucTM", "PhiNV", "LinhLPV", "TuanND", "BachTQ", "LongTQ"]

    def moveDATA(self, ROOT_DATA="/media/tuan/My Passport/DATA_REPRESENTATION/DATA_BY_PEOPLE"):
        SRC_FOLDER = "/media/tuan/My Passport/DATA_REPRESENTATION/6260_CASES"
        json_path="/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20210101_5374_cases.json"
        data_dicom = readFileJSON(json_path)
        studies = []
        dataList = []
        
        for idx, (k, study_detail) in enumerate(data_dicom.items()): 
            IDStudy = study_detail["StudyInformation"]["IDStudy"]
            studies.append(IDStudy)
            dataList.append(study_detail)


        studies = set(studies)
        print("Len studies: {}".format(len(studies)))
        # LongTQ, TuanNM, DucTM, PhiNV, LinhLPV, TuanND, BachTQ
        namePeople = ["TuanNM", "DucTM", "PhiNV", "LinhLPV", "TuanND", "BachTQ", "LongTQ"]

        numberOfPeople = 7
        numberOfCase = 800
        for idx in range(numberOfPeople):
            newData = {}

            start_id = numberOfCase * idx
            end_id = min( numberOfCase * (idx + 1), len(data_dicom))
            des_path = "/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20210101_5374_cases____{}.json".format(namePeople[idx])
            # print(des_path)
            # print(start_id, end_id, des_path)
            DES_DATA_PEOPLE = os.path.join(ROOT_DATA, namePeople[idx], "data")
            os.makedirs(DES_DATA_PEOPLE, exist_ok=True)

            for idc in range(start_id, end_id, 1):
                StudyInstanceUID = dataList[idc]["StudyInformation"]["StudyInstanceUID"]
                src_dir = os.path.join(SRC_FOLDER, StudyInstanceUID)
                # print(src_dir, os.path.isdir(src_dir))
                if not os.path.isdir(src_dir):
                    print("DM miss folder: {}".format(src_dir))
                des_dir = os.path.join(DES_DATA_PEOPLE, StudyInstanceUID)
                cmd = f'mv "{src_dir}" "{des_dir}"'
                os.system(cmd)
                # print(cmd)
                # break
                # break
            #     newData[StudyInstanceUID] = dataList[idc]



    def splitDATA(self, json_path="/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20210101_5374_cases.json"):

        data_dicom = readFileJSON(json_path)
        studies = []
        dataList = []
        
        for idx, (k, study_detail) in enumerate(data_dicom.items()): 
            IDStudy = study_detail["StudyInformation"]["IDStudy"]
            studies.append(IDStudy)
            dataList.append(study_detail)


        studies = set(studies)
        print("Len studies: {}".format(len(studies)))
        # LongTQ, TuanNM, DucTM, PhiNV, LinhLPV, TuanND, BachTQ
        namePeople = ["TuanNM", "DucTM", "PhiNV", "LinhLPV", "TuanND", "BachTQ", "LongTQ"]

        numberOfPeople = 7
        numberOfCase = 800
        for idx in range(numberOfPeople):
            newData = {}

            start_id = numberOfCase * idx
            end_id = min( numberOfCase * (idx + 1), len(data_dicom))
            des_path = "/media/tuan/DATA/AI-Cardio/modules/SplitDataChambers/src/data_20210101_5374_cases____{}.json".format(namePeople[idx])
            # print(des_path)
            print(start_id, end_id, des_path)

            for idc in range(start_id, end_id, 1):
                StudyInstanceUID = dataList[idc]["StudyInformation"]["StudyInstanceUID"]
                newData[StudyInstanceUID] = dataList[idc]

            with open(des_path, "w") as fw:
                json.dump(newData, fw, indent=2)
            print("Len newData: {}".format(len(newData)))

        # "StudyInformation": {
        #   "InstitutionName": "BV VL",
        #   "AcquisitionDateTime": "20180101033215.000",
        #   "PatientName": "Cao Minh Toan",
        #   "ReferringPhysicianName": "BS. Nguyen Viet Son",
        #   "StudyInstanceUID": "1.2.840.113619.2.239.3276.1438593578.0.233",
        #   "IDStudy": "000001",
        #   "NumberOfDicom": 1
        # },

        # "AddDataMap": {
        #   "InstitutionName": "BENH VIEN VINMEC",
        #   "AcquisitionDateTime": "20181221135712.000",
        #   "PatientName": "PHAN THANH PHUONG",
        #   "ReferringPhysicianName": "",
        #   "StudyInstanceUID": "1.2.840.113619.2.391.1878.1545400160.218.1"
        # }

        return True




set6DIndexStudy = Set6DIndexStudy()
