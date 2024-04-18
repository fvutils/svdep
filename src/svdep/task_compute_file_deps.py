#****************************************************************************
#* task_compute_file_deps.py
#*
#* Copyright 2023 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
from typing import List
from .file_collection_info import FileCollectionInfo
from .file_deps_report import FileDepsReport

class TaskComputeFileDeps(object):

    def __init__(self, file_info_i : FileCollectionInfo):
        self.file_info_i = file_info_i
        self.file_info_o = None
        self.report = None
        pass

    def compute(self, root_files : List[str]) -> (
            FileCollectionInfo, FileDepsReport):
        self.file_info_i = FileCollectionInfo()
        self.report = FileDepsReport()

        for file in root_files:
            self.process_file(file)

    def process_file(self, file):

        if 



