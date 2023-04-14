from ltspice import Ltspice
import os
import numpy as np

class Qspice(Ltspice):
    def read_header(self)->None:
        filesize = os.stat(self.file_path).st_size
        
        # if the file is too big, read only the designated amount of bytes
        with open(self.file_path, 'rb') as f:
            if filesize > self.max_header_size:
                data = f.read(self.max_header_size)  
            else:
                data = f.read()  

        #TODO : have to find more adequate way to determine proper encoding of text..
        try:
            buffer_line = ''
            header_content_lines = []   
            byte_index_line_begin = 0
            byte_index_line_end = 0
            try:
                while not ('Binary' in buffer_line or 'Values' in buffer_line):
                    if bytes([data[byte_index_line_end]]) == b'\n':
                        buffer_line = str(bytes(data[byte_index_line_begin:byte_index_line_end+2]), encoding='UTF16')
                        header_content_lines.append(buffer_line)
                        byte_index_line_begin = byte_index_line_end+2
                        byte_index_line_end   = byte_index_line_begin
                    else:
                        byte_index_line_end += 1
                self._encoding = 'utf-16-le'
            except IndexError as e:
                print("Variable description header size is over 1Mbyte. Please adjust max_header_size manually.")
                raise e
        except UnicodeDecodeError as e:
            buffer_line = ''
            header_content_lines = []   
            byte_index_line_begin = 0
            byte_index_line_end = 0
            try:
                while not ('Binary' in buffer_line or 'Values' in buffer_line):
                    if bytes([data[byte_index_line_end]]) == b'\n':
                        buffer_line = str(bytes(data[byte_index_line_begin:byte_index_line_end+1]), encoding='SJIS')
                        header_content_lines.append(buffer_line)
                        byte_index_line_begin = byte_index_line_end+1
                        byte_index_line_end   = byte_index_line_begin
                    else:
                        byte_index_line_end += 1
                self._encoding = 'SJIS'
            except IndexError as e:
                print("Variable description header size is over 1Mbyte. Please adjust max_header_size manually.")
                raise e

        if self._encoding == 'unknown':
            raise UnknownEncodingTypeException("Unknown encoding type")

        header_content_lines = [x.rstrip().rstrip() for x in header_content_lines]

        # remove string header from binary data 
        self.header_size = byte_index_line_end

        variable_declaration_line_num = header_content_lines.index('Variables:')
        header_content_only_lines     = header_content_lines[0:variable_declaration_line_num]
        variable_type_content_lines   = header_content_lines[variable_declaration_line_num+1:-1]

        for header_content_line in header_content_only_lines:
            if self.tags[0] in header_content_line:
                self.title = header_content_line[len(self.tags[0]):]
            if self.tags[1] in header_content_line:
                self.date = header_content_line[len(self.tags[1]):]
            if self.tags[2] in header_content_line:
                self.plot_name = header_content_line[len(self.tags[2]):]
            if self.tags[3] in header_content_line:
                self.flags = header_content_line[len(self.tags[3]):].split(' ')
            if self.tags[4] in header_content_line:
                self._variable_num = int(header_content_line[len(self.tags[4]):])
            if self.tags[5] in header_content_line:
                self._point_num = int(header_content_line[len(self.tags[5]):])
            if self.tags[6] in header_content_line:
                self.offset = float(header_content_line[len(self.tags[6]):])

        for variable_type_content_line in variable_type_content_lines:
            variable_type_split_list = variable_type_content_line.split()
            self._variables.append(variable_type_split_list[1])
            self._types.append(variable_type_split_list[2])

        # check mode
        if 'FFT' in self.plot_name:
            self._mode = 'FFT'
        elif 'Transient' in self.plot_name:
            self._mode = 'Transient'
        elif 'AC' in self.plot_name:
            self._mode = 'AC'
        elif 'DC' in self.plot_name:
            self._mode = 'DC'
        elif 'Noise' in self.plot_name:
            self._mode = 'Noise'
        elif 'Operating Point' in self.plot_name:
            self._mode = "Operating Point"

        # check file type
        if 'Binary' in header_content_lines[-1]:
            self._file_type = 'Binary'

            if 'double' in self.flags:
                self._y_dtype = np.float64

        elif 'Value' in header_content_lines[-1]:
            self._file_type = 'Ascii'
            self._y_dtype = np.float64
        else:
            raise UnknownEncodingTypeException

        if self._mode == 'FFT' or self._mode == 'AC':
            self._y_dtype = np.complex128
            self._x_dtype = np.complex128
