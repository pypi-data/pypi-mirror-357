import os
import re

class assemblerError(Exception):
    pass

def insert(idx, string, char):
    return string[:idx] + char + string[idx:]

def normalize_spaces(string):
    return re.sub(r'\s+', ' ', string).strip()

def split_by_length(s, length=8):
    return [s[i:i+length] for i in range(0, len(s), length)]

def convert_hex_to_binary(number):
    number = number.lower()
    hex_numbers = "0123456789abcdef"
    hex_to_binary = {h: bin(int(h, 16))[2:].zfill(4) for h in hex_numbers}
    binary_number = ""
    for char in number:
        if char not in hex_to_binary:
            raise assemblerError(f"Invalid hex digit '{char}'")
        binary_number += hex_to_binary[char]
    return binary_number

def evaluate_expression(expression, variables, n_bytes, overflow):
    if not expression.strip():
        raise assemblerError("Expression is empty or malformed")
    try:
        answer = round(eval(expression, {"__builtins__": {}}, variables))
    except Exception as e:
        raise assemblerError(f"Error evaluating expression '{expression}': {e}")
    # For a two-byte instruction, we have 1 operand byte → max value 256.
    max_value = 2 ** ((n_bytes - 1) * 8)
    if not overflow and answer >= max_value:
        raise assemblerError(f"Result {answer} exceeds allowed maximum {max_value-1} without overflow enabled.")
    if overflow:
        answer = answer % max_value
    expected_length = 2 if n_bytes == 2 else 4
    return hex(answer)[2:].zfill(expected_length)

class SAP2Assembler:
    def __init__(self):
        self.MnemonicToOpcode = {
            "add b": ["10000000", 1],
            "add c": ["10000001", 1],
            "adi": ["11000110", 2],
            "ana b": ["10100000", 1],
            "ana c": ["10100001", 1],
            "ani": ["11100110", 2],
            "call": ["11001101", 3],
            "cmp b": ["10111000", 1],
            "cmp c": ["10111001", 1],
            "cpi": ["11111110", 2],
            "dcr a": ["00111101", 1],
            "dcr b": ["00000101", 1],
            "dcr c": ["00001101", 1],
            "hlt": ["01110110", 1],
            "inr a": ["00111100", 1],
            "inr b": ["00000100", 1],
            "inr c": ["00001100", 1],
            "in": ["11011011", 2],
            "jmp": ["11000011", 3],
            "jm": ["11111010", 3],
            "jnz": ["11000010", 3],
            "jz": ["11001010", 3],
            "lda": ["00111010", 3],
            "mov a, b": ["01111000", 1],
            "mov a, c": ["01111001", 1],
            "mov b, a": ["01000111", 1],
            "mov b, c": ["01000001", 1],
            "mov c, a": ["01001111", 1],
            "mov c, b": ["01001000", 1],
            "mvi a": ["00111110", 2],
            "mvi b": ["00000110", 2],
            "mvi c": ["00001110", 2],
            "nop": ["00000000", 1],
            "ora b": ["10110000", 1],
            "ora c": ["10110001", 1],
            "ori": ["11110110", 2],
            "out": ["11010011", 2],
            "ret": ["11001001", 1],
            "sta": ["00110010", 3],
            "sub b": ["10010000", 1],
            "sub c": ["10010001", 1],
            "sui": ["11010110", 2],
            "xra b": ["10101000", 1],
            "xra c": ["10101001", 1],
            "xri": ["11101110", 2]
        }
        self.address = 0  # Internal address is maintained as an integer.
        self.fileToAssemble = None
        self.fileToWrite = None
        self.unformattedCodeToAssemble = ""
        self.codeToAssemble = ""
        self.labels = {}  # label -> address mapping
        self.mnemonics_requiring_labels = ["call", "jmp", "jm", "jz", "jnz"]
        self.pseudo_instructions = [".org", ".word"]
        self.assemblyCodeLines = None
        self.mnemonics = [m.lower() for m in self.MnemonicToOpcode.keys()]
        self.assembledCode = [self.convertMnemonicToOpcode("nop") for _ in range(65536)]
        self.variables = {}   # variable_name -> [address (int), value (binary string)]
        self.macros = {}

    def defineVariable(self, assignment):
        equals_index = assignment.find("==")
        expr = insert(equals_index, assignment, " ")
        expr = insert(equals_index + 3, expr, " ")
        expr = normalize_spaces(expr)
        expression = expr.split(" ")
        if len(expression) != 3:
            raise assemblerError(f"Invalid variable assignment on line {self.find_line_index(assignment)}")
        if expression[2].startswith("$"):
            value_str = expression[2][1:]
            try:
                variable_location_int = int(value_str, 16)
            except Exception as e:
                raise assemblerError(f"Invalid hex in variable assignment on line {self.find_line_index(assignment)}: {e}")
        elif expression[2].startswith("#"):
            value_str = expression[2][1:]
            try:
                variable_location_int = int(value_str, 2)
            except Exception as e:
                raise assemblerError(f"Invalid binary in variable assignment on line {self.find_line_index(assignment)}: {e}")
        else:
            try:
                variable_location_int = int(expression[2], 16)
            except Exception as e:
                raise assemblerError(f"Invalid number in variable assignment on line {self.find_line_index(assignment)}: {e}")
        if variable_location_int < 0 or variable_location_int > 0xFFFF:
            raise assemblerError(f"Variable address out of range on line {self.find_line_index(assignment)}")
        self.variables[expression[0]] = [variable_location_int, "00000000"]

    def setVariable(self, variable_set_expression):
        equals_index = variable_set_expression.find("=")
        expr = insert(equals_index, variable_set_expression, " ")
        expr = insert(equals_index + 2, expr, " ")
        expr = normalize_spaces(expr)
        variable_specs = expr.split(" ")
        if len(variable_specs) != 3:
            raise assemblerError(f"Invalid variable assignment on line {self.find_line_index(variable_set_expression)}")
        if variable_specs[2].startswith("$"):
            value = variable_specs[2][1:]
            try:
                int_value = int(value, 16)
            except Exception as e:
                raise assemblerError(f"Invalid hex in setVariable on line {self.find_line_index(variable_set_expression)}: {e}")
            bin_value = bin(int_value)[2:].zfill(8)
            variable_specs[2] = bin_value
        elif variable_specs[2].startswith("#"):
            value = variable_specs[2][1:]
            try:
                int_value = int(value, 2)
            except Exception as e:
                raise assemblerError(f"Invalid binary in setVariable on line {self.find_line_index(variable_set_expression)}: {e}")
            bin_value = bin(int_value)[2:].zfill(8)
            variable_specs[2] = bin_value
        variable_name = variable_specs[0]
        variable_value = variable_specs[2].zfill(8)
        if len(variable_value) > 8:
            raise assemblerError(f"Invalid variable assignment on line {self.find_line_index(variable_set_expression)}")
        if variable_name not in self.variables:
            raise assemblerError(f"Variable '{variable_name}' not defined (line {self.find_line_index(variable_set_expression)})")
        self.variables[variable_name][1] = variable_value
        self.assembledCode[self.variables[variable_name][0]] = variable_value

    def handleVariable(self, expression):
        if "==" in expression:
            self.defineVariable(expression)
        elif "=" in expression:
            self.setVariable(expression)

    def addressCheck(self):
        if self.address > 0x10000:
            raise assemblerError(f"The SAP2 architecture only supports 16-bit addresses (max: 65535), exceeded by {self.address - 0xFFFF}")

    def printAssembledCode(self, row_width=16, hex_data=False, n_bytes=256):
        for idx in range(min(n_bytes, len(self.assembledCode))):
            data = self.assembledCode[idx]
            if hex_data:
                try:
                    data = hex(int(data, 2))[2:].zfill(2)
                except Exception:
                    pass
            if idx % row_width == 0:
                print(f"{hex(idx)[2:].zfill(4)}: {data}", end=" ")
            elif (idx % row_width) != (row_width - 1):
                print(f"{data}", end=" ")
            else:
                print(f"{data}")
        print()

    def parseAscii(self, string):
        ascii_vals = [ord(char) for char in string]
        return [bin(val)[2:].zfill(8) for val in ascii_vals]

    def identifyLabels(self):
        assemblyCodeLines = []
        self.identifyVariables()
        self.parseMacros()
        self.address = 0
        for line in self.assemblyCodeLines:
            if ":" in line:
                label = line.split(":")[0].strip()
                self.labels[label] = self.address
                continue
            for mnemonic in self.MnemonicToOpcode.keys():
                if line.startswith(mnemonic):
                    num_bytes = self.getNumBytesForMnemonic(mnemonic)
                    self.address += num_bytes
                    assemblyCodeLines.append(line)
                    break
            if ".word" in line:
                self.address += 2
                assemblyCodeLines.append(line)
            if ".org" in line:
                origin = line[6:].strip()
                operand_identifier = line[5]
                if operand_identifier == "$":
                    try:
                        self.address = int(origin, 16)
                    except Exception as e:
                        raise assemblerError(f"Invalid hex origin in .org on line: {line}")
                elif operand_identifier == "#":
                    try:
                        self.address = int(origin, 2)
                    except Exception as e:
                        raise assemblerError(f"Invalid binary origin in .org on line: {line}")
                assemblyCodeLines.append(line)
            if line.startswith(".byte"):
                self.address += 1
                assemblyCodeLines.append(line)
            if line.startswith(".ascii"):
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    raise assemblerError(f"Missing ASCII string in line: {line}")
                ascii_bytes = self.parseAscii(parts[1].strip())
                self.address += len(ascii_bytes)
                assemblyCodeLines.append(line)
            if line.strip() != "" and not any(kw in line for kw in list(self.MnemonicToOpcode.keys()) + [".word", ".org", "=",".byte", ".ascii", ":"]):
                assemblyCodeLines.append(line)
        self.address = 0
        self.assemblyCodeLines = assemblyCodeLines
        self.codeToAssemble = "\n".join(self.assemblyCodeLines)

    def convertMnemonicToOpcode(self, mnemonic):
        return self.MnemonicToOpcode[mnemonic][0]

    def getNumBytesForMnemonic(self, mnemonic):
        return self.MnemonicToOpcode[mnemonic][1]

    def areKeywordsInLine(self, line):
        for mnemonic in self.MnemonicToOpcode.keys():
            if mnemonic in line:
                return True
        if any(p in line for p in [".org", ".word", "=", ".byte", ".ascii"]):
            return True
        return False

    def getCodeFromFile(self, recursion):
        if not self.fileToAssemble.endswith(".sap2asm"):
            raise assemblerError("File Error: Invalid file format. please use .sap2")
        with open(self.fileToAssemble, "r") as file:
            self.codeToAssemble = file.read().lower() if not recursion else file.read().lower() + "\n\n" + self.codeToAssemble
        self.assemblyCodeLines = self.codeToAssemble.split("\n")
        self.unformattedCodeToAssemble = self.codeToAssemble

    def incrementAddress(self):
        self.address += 1

    def find_line_index(self, lineToFind):
        lines = self.unformattedCodeToAssemble.split("\n")
        for idx, line in enumerate(lines):
            if lineToFind.strip() == line.strip():
                return idx + 1
        return "?"  # Fallback if not found.

    def parse_number(self, number, identifier):
        if identifier == "$":
            bin_number = convert_hex_to_binary(number)
            operand_bytes = split_by_length(bin_number, 8)
            return [b.zfill(8) for b in operand_bytes]
        elif identifier == "#":
            operand_bytes = split_by_length(number, 8)
            return [b.zfill(8) for b in operand_bytes]
        else:
            raise assemblerError(f"Unknown operand identifier {identifier}")

    def formatAssemblyLines(self):
        lines = []
        for line in self.assemblyCodeLines:
            if line.strip() != "":
                if ";" in line:
                    comment_idx = line.find(";")
                    line = line[:comment_idx].strip()
                lines.append(line.strip())
        self.assemblyCodeLines = lines

    def saveAssembledCode(self, filename, row_width=16, hex_data=False, n_bytes=256):
        with open(filename, 'w') as file:
            for idx in range(min(n_bytes, len(self.assembledCode))):
                data = self.assembledCode[idx]
                if hex_data:
                    try:
                        data = hex(int(data, 2))[2:].zfill(2)
                    except Exception:
                        pass
                if idx % row_width == 0:
                    file.write(f"{hex(idx)[2:].zfill(4)}: {data} ")
                elif (idx % row_width) != (row_width - 1):
                    file.write(f"{data} ")
                else:
                    file.write(f"{data}\n")

    def identifyVariables(self):
        for line in self.assemblyCodeLines:
            if "=" in line:
                self.handleVariable(line)

    def parseMacros(self):
        assemblyCodeLines = self.assemblyCodeLines
        self.assemblyCodeLines = []
        in_macro = False
        macro_name = ""
        for line_idx, line in enumerate(assemblyCodeLines):
            finished_macro = False
            if line.startswith(".macro") or in_macro:
                if not in_macro:
                    parts = line.split()
                    if len(parts) < 2:
                        raise assemblerError(f"Missing macro name at line {line_idx + 1}")
                    macro_name = parts[1].strip()
                    self.macros[macro_name] = []
                if line.strip() != ".endmacro":
                    self.macros[macro_name].append(line)
                    in_macro = True
                else:
                    in_macro = False
                    finished_macro = True
            else:
                self.assemblyCodeLines.append(line)
            if finished_macro:
                if self.macros[macro_name]:
                    self.macros[macro_name] = self.macros[macro_name][1:]
        expanded_lines = []
        for line in self.assemblyCodeLines:
            if line.strip() in self.macros:
                expanded_lines.extend(self.macros[line.strip()])
            else:
                expanded_lines.append(line)
        self.assemblyCodeLines = expanded_lines
        self.formatAssemblyLines()
        self.codeToAssemble = "\n".join(self.assemblyCodeLines)

    def changeMnemonic(self, mnemonicToChange, n_bytes=False, opcode=False, requires_label=False):
        if n_bytes:
            self.MnemonicToOpcode[mnemonicToChange][1] = n_bytes
        if opcode:
            self.MnemonicToOpcode[mnemonicToChange][0] = opcode
        if requires_label and mnemonicToChange not in self.mnemonics_requiring_labels:
            self.mnemonics_requiring_labels.append(mnemonicToChange)

    def addMnemonic(self, mnemonicToAdd, opcode, requires_label=False, n_bytes=1):
        if requires_label and mnemonicToAdd not in self.mnemonics_requiring_labels:
            self.mnemonics_requiring_labels.append(mnemonicToAdd)
        self.MnemonicToOpcode[mnemonicToAdd] = [opcode, n_bytes]

    def removeMnemonic(self, mnemonicToRemove):
        if mnemonicToRemove in self.MnemonicToOpcode:
            del self.MnemonicToOpcode[mnemonicToRemove]
        if mnemonicToRemove in self.mnemonics_requiring_labels:
            self.mnemonics_requiring_labels.remove(mnemonicToRemove)

    def assemble(self, fileToAssemble, fileToWrite="", row_width=16, hex_data=False, n_bytes=256, print_data=False, overflow=False, debug=False):
        self.fileToAssemble = fileToAssemble
        self.fileToWrite = fileToWrite

        if not os.path.exists(fileToAssemble):
            raise assemblerError(f"File {fileToAssemble} not found")

        self.getCodeFromFile(recursion=False)


        i = 0
        included_files = set()

        while i < len(self.assemblyCodeLines):
            line = self.assemblyCodeLines[i]

            if line.startswith(".include <") and line.endswith(">"):
                file_to_include = line.split("<")[1].split(">")[0].strip()

                if file_to_include in included_files:
                    i += 1
                    continue

                included_files.add(file_to_include)

                if debug:
                    print(f"[DEBUG] Including file: {file_to_include}")

                # Remove the .include line
                self.assemblyCodeLines.pop(i)

                # Temporarily set fileToAssemble to load the included file
                original_file = self.fileToAssemble
                self.fileToAssemble = file_to_include
                self.getCodeFromFile(recursion=True)
                self.fileToAssemble = original_file

        # DO NOT increment i → we want to re-check current position (new content added to the end or in-place)
            elif line.startswith(".include <") and not line.endswith(">"):
                raise assemblerError(f"Invalid include statement on line: {self.find_line_index(line)}")
            else:
                i += 1


        self.formatAssemblyLines()
        self.identifyLabels()
        for line in self.assemblyCodeLines:
            if debug:
                print(f"\n[DEBUG] Processing line: '{line}' at address {hex(self.address)}")

            if (".org" not in line) and (".word" not in line) and ("=" not in line) and (".ascii" not in line) and (".byte" not in line) and (":" not in line):
                if not self.areKeywordsInLine(line):
                    raise assemblerError(f"Error in line {self.find_line_index(line)}, '{line}' doesn't contain a mnemonic or pseudo-instruction")
                for mnemonic in self.MnemonicToOpcode.keys():
                    try:
                        if line[:len(mnemonic)] == mnemonic:
                            opcode = self.convertMnemonicToOpcode(mnemonic)
                            num_bytes = self.getNumBytesForMnemonic(mnemonic)
                            self.assembledCode[self.address] = opcode
                            if debug:
                                print(f"[DEBUG] Writing opcode '{opcode}' for mnemonic '{mnemonic}' at {hex(self.address)}")

                            if num_bytes == 1 and line.strip() != mnemonic:
                                raise assemblerError(f"Error in line {self.find_line_index(line)}, extra operand found for mnemonic '{mnemonic}'")
                            if mnemonic not in self.mnemonics_requiring_labels:
                                if num_bytes > 1:
                                    if "$" in line or "#" in line:
                                        operand_str = line[len(mnemonic):].strip()
                                        operand_identifier = operand_str[0]
                                        number = operand_str[1:].strip()
                                        operand_bytes = self.parse_number(number, operand_identifier)
                                        if debug:
                                            print(f"[DEBUG] Parsed operand bytes: {operand_bytes}")
                                        if len(operand_bytes) != (num_bytes - 1):
                                            raise assemblerError(f"Error in line {self.find_line_index(line)}, invalid operand length")
                                        for operand_byte in operand_bytes:
                                            self.incrementAddress()
                                            self.assembledCode[self.address] = operand_byte
                                            if debug:
                                                print(f"[DEBUG] Writing operand byte '{operand_byte}' at {hex(self.address)}")
                                    else:
                                        label_found = any(label in line for label in self.labels)
                                        operand_str = line[len(mnemonic):].strip()
                                        if not label_found:
                                            if operand_str in self.variables:
                                                variable_value = self.variables[operand_str][1]
                                                self.incrementAddress()
                                                if num_bytes == 2:
                                                    self.assembledCode[self.address] = variable_value
                                                    if debug:
                                                        print(f"[DEBUG] Writing variable value '{variable_value}' at {hex(self.address)}")
                                                else:
                                                    var_location = self.variables[operand_str][0]
                                                    operand_bytes = self.parse_number(hex(var_location)[2:], "$")
                                                    if debug:
                                                        print(f"[DEBUG] Variable location bytes: {operand_bytes}")
                                                    if len(operand_bytes) != (num_bytes - 1):
                                                        raise assemblerError(f"Error in line {self.find_line_index(line)}, invalid variable operand")
                                                    print(operand_bytes)
                                                    for operand_byte in operand_bytes:
                                                        self.incrementAddress()
                                                        self.assembledCode[self.address] = operand_byte
                                                        if debug:
                                                            print(f"[DEBUG] Writing variable operand byte '{operand_byte}' at {hex(self.address)}")
                                            else:
                                                variables_in_expression = {}
                                                expression = operand_str
                                                for variable in self.variables:
                                                    if variable in expression:
                                                        if num_bytes == 2:
                                                            variables_in_expression[variable] = int(self.variables[variable][1], 2)
                                                        elif num_bytes == 3:
                                                            variables_in_expression[variable] = self.variables[variable][0]
                                                number = evaluate_expression(expression, variables_in_expression, num_bytes, overflow)
                                                operand_bytes = self.parse_number(number, "$")
                                                if debug:
                                                    print(f"[DEBUG] Expression result bytes: {operand_bytes}")
                                                if len(operand_bytes) != (num_bytes - 1):
                                                    raise assemblerError(f"Error in line {self.find_line_index(line)}, invalid expression operand")
                                                for operand_byte in operand_bytes:
                                                    self.incrementAddress()
                                                    self.assembledCode[self.address] = operand_byte
                                                    if debug:
                                                        print(f"[DEBUG] Writing expression operand byte '{operand_byte}' at {hex(self.address)}")
                                        else:
                                            pass
                            else:
                                label = line[len(mnemonic):].strip()
                                if label not in self.labels:
                                    raise assemblerError(f"Error in line {self.find_line_index(line)}, label '{label}' doesn't exist.")
                                label_address = self.labels[label]
                                operand_bytes = self.parse_number(hex(label_address)[2:].zfill(4), "$")
                                if debug:
                                    print(f"[DEBUG] Label '{label}' resolved to address {hex(label_address)} -> bytes {operand_bytes}")
                                if len(operand_bytes) < 2:
                                    raise assemblerError(f"Label address for '{label}' is invalid")
                                for operand_byte in operand_bytes:
                                    self.incrementAddress()
                                    self.assembledCode[self.address] = operand_byte
                                    if debug:
                                        print(f"[DEBUG] Writing label operand byte '{operand_byte}' at {hex(self.address)}")
                            break
                    except Exception:
                        continue
                self.incrementAddress()

            if ".word" in line:
                word = line[7:].strip()
                operand_identifier = line[6]
                operand_bytes = self.parse_number(word, operand_identifier)
                if debug:
                    print(f"[DEBUG] .word value {word} -> bytes {operand_bytes}")
                if len(operand_bytes) != 2:
                    raise assemblerError(f"Invalid .word operand in line {self.find_line_index(line)}")
                self.assembledCode[self.address] = operand_bytes[0]
                self.incrementAddress()
                self.assembledCode[self.address] = operand_bytes[1]

            if ".byte" in line:
                byte = line[7:].strip()
                byte_identifier = line[6]
                operand_bytes = self.parse_number(byte, byte_identifier)
                if debug:
                    print(f"[DEBUG] .byte value {byte} -> byte {operand_bytes}")
                if len(operand_bytes) != 1:
                    raise assemblerError(f"Invalid .byte operand in line {self.find_line_index(line)}")
                self.assembledCode[self.address] = operand_bytes[0]

            if ".ascii" in line:
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    raise assemblerError(f"Missing ASCII string in line {line}")
                text = parts[1].strip()
                ascii_text = self.parseAscii(text)
                if debug:
                    print(f"[DEBUG] .ascii text '{text}' -> bytes {ascii_text}")
                self.assembledCode[self.address] = ascii_text[0]
                for char in ascii_text[1:]:
                    self.incrementAddress()
                    self.assembledCode[self.address] = char

            if ".org" in line:
                origin = line[6:].strip()
                operand_identifier = line[5]
                if operand_identifier == "$":
                    try:
                        self.address = int(origin, 16)
                        if debug:
                            print(f"[DEBUG] .org set address to {hex(self.address)}")
                    except Exception as e:
                        raise assemblerError(f"Invalid hex origin in .org on line: {line}")
                elif operand_identifier == "#":
                    try:
                        self.address = int(origin, 2)
                        if debug:
                            print(f"[DEBUG] .org set address to {hex(self.address)}")
                    except Exception as e:
                        raise assemblerError(f"Invalid binary origin in .org on line: {line}")
                else:
                    raise assemblerError(f"Unknown operand identifier {operand_identifier} in .org")
            if ("=" in line) and ("==" not in line):
                self.handleVariable(line)
                if debug:
                    print(f"[DEBUG] Handled variable line: {line}")

            self.addressCheck()

        if self.fileToWrite != "":
            self.saveAssembledCode(filename=self.fileToWrite, hex_data=hex_data, n_bytes=n_bytes, row_width=row_width)
        if print_data:
            self.printAssembledCode(row_width=row_width, hex_data=hex_data, n_bytes=n_bytes)
