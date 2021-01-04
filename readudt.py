"""
ConPlc - connect PLC and PC
Copyright (C) 2020  Marvin Mangold (mangold.mangold00@googlemail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import re


# define possible Datatypes and its bits-size
standard_types = {"Bool": 1,
                  "Byte": 8,
                  "Word": 16,
                  "DWord": 32,
                  "LWord": 64,
                  "SInt": 8,
                  "USInt": 8,
                  "Int": 16,
                  "UInt": 16,
                  "DInt": 32,
                  "UDInt": 32,
                  "LInt": 64,
                  "ULInt": 64,
                  "Real": 32,
                  "LReal": 64,
                  "Char": 8,
                  "WChar": 16,
                  "String": 16,
                  "WString": 16}
special_types = {"DTL": 0,
                 "Array": 0,
                 "Struct": 0}


def read_udt_file(path):
    udt = []
    with open(path, "r", encoding="utf-8") as udt_file:
        for line in udt_file:
            stripped = line.strip()
            if stripped != "":
                udt.append(stripped)
    return udt


def get_udt_name(line):
    # get Name of udt (must have string "TYPE ")
    # -->TYPE "udt Name"
    result = False
    name = ""
    regex = re.search(r'TYPE "(.*?)"', line)
    if regex is not None:
        result = True
        name = regex.group(1)
    return result, name


def get_udt_description(line):
    # get Description of udt (must have string "TITLE = ")
    # -->TITLE = udt with variables
    result = False
    description = ""
    regex = re.search(r'TITLE = (.*)', line)
    if regex is not None:
        result = True
        description = regex.group(1)
    return result, description


def get_udt_version(line):
    # get Version of udt (must have string "VERSION : ")
    # -->VERSION : 0.1
    result = False
    version = ""
    regex = re.search(r'VERSION : (.*)', line)
    if regex is not None:
        result = True
        version = regex.group(1)
    return result, version


def get_udt_info(line):
    # get Info of udt (string has to start with "//")
    # -->//Information about this udt
    result = False
    info = ""
    regex = re.search(r'^/{2}(.*)', line)
    if regex is not None:
        result = True
        info = regex.group(1)
    return result, info


def get_udt_headerend(line):
    # get last part of the header
    # -->STRUCT
    result = False
    regex = re.search(r'STRUCT', line)
    if regex is not None:
        result = True
    return result


def get_datatype(line):
    # get VAR declaration datatype (must have ":")
    # -->name : Bool;   // comment
    result = False
    datatype = ""
    regex = re.search(r'(.*) : ([^;/\[ ]*)', line)
    if regex is not None:
        result = True
        datatype = regex.group(2)
    return result, datatype


def clean_varname(varname):
    # erase additional info in Varname (internal settings in {} brackets)
    # -->name {InstructionName := 'DTL'; LibVersion := '1.0'} : DTL;   // comment
    regex = re.search(r'(.*) {', varname)
    if regex is not None:
        varname = regex.group(1)
    return varname


def get_struct(line):
    # get Struct declaration (must have ":" and "Struct" and can have "// comment")
    # -->name : Struct   // comment
    result = False
    element = {}
    regex = re.search(r'(.*) : (Struct)(?:\s{3}// )?(.*)?', line)
    if regex is not None:
        result = True
        name, datatype, comment = clean_varname(regex.group(1)), regex.group(2), regex.group(3)
        # first part of struct (declaration line)
        element = {
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": False, "action": "open"}
    return result, element


def get_endstruct(line):
    # get end of Struct declaration (must have string "END_STRUCT;")
    # -->END_STRUCT;
    result = False
    element = {}
    regex = re.search(r'END_STRUCT;', line)
    if regex is not None:
        result = True
        # last part of struct (end indicator)
        element = {
            "name": "", "datatype": "", "comment": "", "visible": False, "access": False, "action": "close"}
    return result, element


def get_var(line):
    # get VAR declaration (must have ":" and can have "// comment")
    # -->name : Bool;   // comment
    result = False
    element = {}
    regex = re.search(r'(.*) : (.*);(?:\s{3}// )?(.*)?', line)
    if regex is not None:
        result = True
        name, datatype, comment = clean_varname(regex.group(1)), regex.group(2), regex.group(3)
        element = {
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"}
    return result, element


def get_dtl(line):
    # get VAR declaration (must have ":" and can have "// comment")
    # -->name : Bool;   // comment
    result = False
    elements = []
    regex = re.search(r'(.*) : (.*);(?:\s{3}// )?(.*)?', line)
    if regex is not None:
        result = True
        name, datatype, comment = clean_varname(regex.group(1)), regex.group(2), regex.group(3)
        # first part of dtl (declaration line)
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": False, "action": "open"})
        name, datatype, comment = "YEAR", "UInt", "Year"
        # middle part of dtl (data)
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "MONTH", "USInt", "Month"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "DAY", "USInt", "Day"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "WEEKDAY", "USInt", "Weekday"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "HOUR", "USInt", "Hour"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "MINUTE", "USInt", "Minute"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "SECOND", "USInt", "Second"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        name, datatype, comment = "NANOSECOND", "UDint", "Nanosecond"
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True, "action": "none"})
        # last part of dtl (end indicator)
        elements.append({
            "name": "", "datatype": "", "comment": "", "visible": False, "access": False, "action": "close"})
    return result, elements


def get_array_data(line):
    # -->Array[X..Y] of Datatype
    start = 0
    end = 0
    datatype = ""
    regex = re.search(r'(?:Array\[)(.*)(?:\.\.)(.*)(?:] of )(.*);', line)
    if regex is not None:
        start = int(regex.group(1))
        end = int(regex.group(2)) + 1
        datatype = regex.group(3)
    return start, end, datatype


def get_array(line):
    # get VAR declaration (must have ":" and can have "// comment")
    # -->name : Bool;   // comment
    result = False
    elements = []
    regex = re.search(r'(.*) : (.*);(?:\s{3}// )?(.*)?', line)
    if regex is not None:
        result = True
        name, datatype, comment = clean_varname(regex.group(1)), regex.group(2), regex.group(3)
        # first part of array (declaration line)
        elements.append({
            "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": False, "action": "open"})
        start, end, datatype = get_array_data(line)
        for entry in range(start, end):
            name, datatype = "[" + str(entry) + "]", datatype
            # middle part of array (data)
            elements.append({
                "name": name, "datatype": datatype, "comment": comment, "visible": True, "access": True,
                "action": "none"})
        # last part of array (end indicator)
        elements.append({
            "name": "", "datatype": "", "comment": "", "visible": False, "access": False, "action": "close"})
    return result, elements


def get_udt(line, data, foldernames, dependencies, datatype):
    result, element = get_var(line)
    if result:
        # first part of udt (declaration line)
        element["access"] = False
        element["action"] = "open"
        save_element(data, foldernames, element)
        foldernames.append(element["name"] + ".")
        # middle part of udt (data)
        _path = dependencies[datatype]
        _name, _description, _version, _info, _size, data = get_udt_data(data=data,
                                                                         foldernames=foldernames,
                                                                         filepath=_path,
                                                                         dependencies=dependencies)
        # last part of udt (end indicator)
        element = {"name": "", "datatype": "", "comment": "",
                   "visible": False, "access": False, "action": "close"}
        save_element(data, foldernames, element)
        foldernames.pop()


def element_is_udt(datatype):
    # check if element datatype is special udt type
    # -->"someName"
    result = False
    element = ""
    regex = re.search(r'"(.*)"', datatype)
    if regex is not None:
        result = True
        element = regex[0]
    return result, element
    

def save_element(data, foldernames, element):
    # put prefix to varname
    varname = ""
    newelement = element.copy()
    for prefix in foldernames:
        varname += prefix
    newelement["name"] = varname + newelement["name"]
    # add value parameter to element
    newelement["value"] = ""
    # save element
    data.append(newelement)


def get_udt_data(data=None, foldernames=None, filepath="", dependencies=None):
    if data is None:
        data = []
    if foldernames is None:
        foldernames = []
    name = ""
    description = ""
    version = ""
    info = ""
    readheader = True
    # read Data from udt-File
    udt = read_udt_file(filepath)
    # analyse Data from udt-File
    for line in udt:
        # read header
        if readheader:
            # get udt name
            result, element = get_udt_name(line)
            if result:
                name = element
            # get udt description
            result, element = get_udt_description(line)
            if result:
                description = element
            # get udt version
            result, element = get_udt_version(line)
            if result:
                version = element
            # get udt info
            result, element = get_udt_info(line)
            if result:
                info = element
            # get udt header end
            result = get_udt_headerend(line)
            if result:
                readheader = False
                foldernames.append("")
        # read data
        else:
            # get endstruct
            result, element = get_endstruct(line)
            if result:
                foldernames.pop()
                save_element(data, foldernames, element)
            # check datatype of element
            result, datatype = get_datatype(line)
            if result:
                # standard datatype
                if datatype in standard_types:
                    result, element = get_var(line)
                    if result:
                        save_element(data, foldernames, element)
                # special datatype
                elif datatype in special_types:
                    # special datatype struct
                    if datatype == "Struct":
                        result, element = get_struct(line)
                        if result:
                            save_element(data, foldernames, element)
                            foldernames.append(element["name"]+".")
                    # special datatype dtl
                    elif datatype == "DTL":
                        result, elements = get_dtl(line)
                        if result:
                            firstrun = True
                            for element in elements:
                                save_element(data, foldernames, element)
                                if firstrun:
                                    foldernames.append(element["name"] + ".")
                                    firstrun = False
                            foldernames.pop()
                    # special datatype array
                    elif datatype == "Array":
                        result, elements = get_array(line)
                        if result:
                            firstrun = True
                            for element in elements:
                                save_element(data, foldernames, element)
                                if firstrun:
                                    foldernames.append(element["name"])
                                    firstrun = False
                            foldernames.pop()
                # special datatype udt
                elif element_is_udt(datatype)[0]:
                    get_udt(line=line, data=data, foldernames=foldernames, dependencies=dependencies, datatype=datatype)
                else:
                    print("Datentyp {datatype} nicht implementiert!".format(datatype=datatype))
    size = 0
    return name, description, version, info, size, data


def get_udt_dependencies(path):
    dependencies = {}
    udt = read_udt_file(path)
    # check every line in udt file for udt declaration
    for line in udt:
        result, datatype = get_datatype(line)
        if result:
            # declaration type udt in array
            if datatype == "Array":
                # get array data
                result, elements = get_array(line)
                if result:
                    # check in (array[x..x] of datatype) if datatype is udt type
                    if element_is_udt(elements[1]["datatype"])[0]:
                        dependencies[elements[1]["datatype"]] = ""
            # declaration type udt direct or in struct
            elif element_is_udt(datatype)[0]:
                dependencies[datatype] = ""
    return dependencies
