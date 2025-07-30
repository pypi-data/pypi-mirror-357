# S.T.A.L.K.E.R. shaders.xr handling module
# Update history:
# 	01/09/2012 - initial release
##############################################

from stkutils.binary_data import pack
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import (
    bless,
    fail,
    join,
    length,
    mkpath,
    reverse,
    split,
    substr,
    universal_dict_object,
)
from stkutils.stkutils_math import stkutils_math
from stkutils.utils import get_filelist, get_path, read_file, write_file


class shaders_xr:
    # use strict;
    # use data_packet;
    # use ini_file;
    # use math;
    # use debug qw(fail warn);
    # use utils qw(get_filelist get_path write_file read_file);
    # use File::Path;

    SHADERS_CHUNK_CONSTANTS = 0
    SHADERS_CHUNK_MATRICES = 1
    SHADERS_CHUNK_BLENDERS = 2
    SHADERS_CHUNK_NAMES = 3

    # enum WaveForm::EFunction
    fCONSTANT = 0
    fSIN = 1
    fTRIANGLE = 2
    fSQUARE = 3
    fSAWTOOTH = 4
    fINVSAWTOOTH = 5
    fFORCE32 = 0xFFFFFFFF

    def read(self, CDH, mode):
        print("reading...\n")
        if not ((mode == "ltx") or (mode == "bin")):
            fail("unsuported mode " + mode)
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break

            if index == self.SHADERS_CHUNK_CONSTANTS:
                self.read_constants(CDH, mode)
            elif index == self.SHADERS_CHUNK_MATRICES:
                self.read_matrices(CDH, mode)
            elif index == self.SHADERS_CHUNK_BLENDERS:
                self.read_blenders(CDH, mode)
            elif index == self.SHADERS_CHUNK_NAMES:
                self.read_names(CDH)
            else:
                fail("unknown chunk index " + index)

            CDH.r_chunk_close()

        CDH.close()

    def read_constants(self, CDH, mode):
        print("	constants\n")
        packet = data_packet(CDH.r_chunk_data())
        if mode and (mode == "bin"):
            self.raw_constants = packet.data()
        else:
            while packet.resid() > 0:
                constant = universal_dict_object()
                (constant.name) = packet.unpack("Z*")
                for i in range(4):
                    waveform = stkutils_math.create("waveform")
                    waveform.set(packet.unpack("Vf4", 20))
                    constant.waveforms.append(waveform)

                self.constants.append(constant)

            if packet.resid() != 0:
                fail("there is some data left in packet: " + packet.resid())

    def read_matrices(self, CDH, mode):
        print("	matrices\n")
        packet = data_packet(CDH.r_chunk_data())
        if mode and (mode == "bin"):
            self.raw_matrices = packet.data()
        else:
            while packet.resid() > 0:
                matrix = universal_dict_object()
                (matrix.name, matrix.dwmode, matrix.tcm) = packet.unpack("Z*VV")
                matrix.scaleU = stkutils_math.create("waveform")
                matrix.scaleU.set(packet.unpack("Vf4", 20))
                matrix.scaleV = stkutils_math.create("waveform")
                matrix.scaleV.set(packet.unpack("Vf4", 20))
                matrix.rotate = stkutils_math.create("waveform")
                matrix.rotate.set(packet.unpack("Vf4", 20))
                matrix.scrollU = stkutils_math.create("waveform")
                matrix.scrollU.set(packet.unpack("Vf4", 20))
                matrix.scrollV = stkutils_math.create("waveform")
                matrix.scrollV.set(packet.unpack("Vf4", 20))
                self.matrices.append(matrix)

            if packet.resid() != 0:
                fail("there is some data left in packet: " + packet.resid())

    def read_blenders(self, CDH, mode):
        print("	blenders\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            if mode and (mode == "bin"):
                self.blenders.append(CDH.r_chunk_data())
            else:
                blender = universal_dict_object()
                packet = data_packet(CDH.r_chunk_data())
                (blender.cls, blender.name) = packet.unpack("a[8]Z*")
                blender.cls = reverse(blender.cls)
                # 			print("$blender.name: $blender.cls\n")
                packet.pos(136)
                (blender.computer) = packet.unpack("Z*")
                packet.pos(168)
                (blender.ctime, blender.version) = packet.unpack("Vv", 6)
                packet.pos(176)
                # SWITCH: {
                if (blender.cls == "LmBmmD  ") or (blender.cls == "BmmDold "):
                    bless(blender, "CBlender_BmmD")
                    blender.read(packet)
                elif (blender.cls == "MODELEbB") or (blender.cls == "LmEbB   "):
                    bless(blender, "CBlender_EbB")
                    blender.read(packet)  # CBlender_LmEbB
                elif blender.cls == "D_STILL ":
                    bless(blender, "CBlender_Detail_Still")
                    blender.read(packet)
                elif blender.cls == "D_TREE  ":
                    bless(blender, "CBlender_Tree")
                    blender.read(packet)
                elif blender.cls == "LM_AREF ":
                    bless(blender, "CBlender_deffer_aref")
                    blender.read(packet)
                elif blender.cls == "V_AREF  ":
                    bless(blender, "CBlender_Vertex_aref")
                    blender.read(packet)
                elif blender.cls == "MODEL   ":
                    bless(blender, "CBlender_deffer_model")
                    blender.read(packet)
                elif (blender.cls == "E_SEL   ") or (blender.cls == "E_WIRE  "):
                    bless(blender, "CBlender_Editor")
                    blender.read(packet)  # CBlender_Editor_Wire
                elif blender.cls == "PARTICLE":
                    bless(blender, "CBlender_Particle")
                    blender.read(packet)
                elif blender.cls == "S_SET   ":
                    bless(blender, "CBlender_Screen_SET")
                    blender.read(packet)
                elif (
                    (blender.cls == "BLUR    ")  # CBlender_Blur, 		R1 only
                    or (blender.cls == "LM      ")  # CBlender_default,		R1 only
                    or (blender.cls == "SH_WORLD")  # CBlender_ShWorld, 		R1 only
                    or (blender.cls == "S_GRAY  ")
                    or (blender.cls == "V       ")
                ):
                    bless(blender, "CBlender_Tesselation")
                    blender.read(packet)
                else:
                    warning("unsupported cls " + blender.cls)
                    continue
                # }
                self.blenders.append(blender)
                if packet.resid() != 0:
                    fail("there is some data left in packet: " + packet.resid())

            CDH.r_chunk_close()

    def read_names(self, CDH):
        print("	names\n")
        packet = data_packet(CDH.r_chunk_data())
        (count) = packet.unpack("V", 4)
        for i in range(count):
            self.names.append(packet.unpack("Z*"))

        if packet.resid() != 0:
            fail("there is some data left in packet: " + packet.resid())

    def write(self, CDH, mode):

        print("writing...\n")
        if mode != "ltx" or (mode == "bin"):
            fail("unsuported mode " + mode)

        self.write_constants(CDH, mode)
        self.write_matrices(CDH, mode)
        self.write_blenders(CDH, mode)
        self.write_names(CDH)

    def write_constants(self, CDH, mode):
        print("	constants\n")
        if mode and (mode == "bin"):
            CDH.w_chunk(self.SHADERS_CHUNK_CONSTANTS, self.raw_constants)
        else:
            CDH.w_chunk_open(self.SHADERS_CHUNK_CONSTANTS)
            for constant in self.constants:
                CDH.w_chunk_data(pack("Z*", constant.name))
                for i in range(4):
                    CDH.w_chunk_data(pack("Vf4", constant.waveforms[i].get()))

            CDH.w_chunk_close()

    def write_matrices(self, CDH, mode):

        print("	matrices\n")
        if mode and (mode == "bin"):
            CDH.w_chunk(self.SHADERS_CHUNK_MATRICES, self.raw_matrices)
        else:
            CDH.w_chunk_open(self.SHADERS_CHUNK_MATRICES)
            for matrix in self.matrices:
                CDH.w_chunk_data(pack("Z*VV", matrix.name, matrix.dwmode, matrix.tcm))
                CDH.w_chunk_data(pack("Vf4", matrix.scaleU.get()))
                CDH.w_chunk_data(pack("Vf4", matrix.scaleV.get()))
                CDH.w_chunk_data(pack("Vf4", matrix.rotate.get()))
                CDH.w_chunk_data(pack("Vf4", matrix.scrollU.get()))
                CDH.w_chunk_data(pack("Vf4", matrix.scrollV.get()))

            CDH.w_chunk_close()

    def write_blenders(self, CDH, mode):
        print("	blenders\n")
        CDH.w_chunk_open(self.SHADERS_CHUNK_BLENDERS)

        for i, blender in enumerate(self.blenders):
            CDH.w_chunk_open(i)
            if mode and (mode == "bin"):
                CDH.w_chunk_data(blender)
            else:
                gl_pos = CDH.offset()
                blender.cls = reverse(blender.cls)
                CDH.w_chunk_data(pack("a[8]Z*", blender.cls, blender.name))
                delta = 136 + gl_pos - CDH.offset()
                CDH.w_chunk_data(pack(f"C{delta}", 0xED))
                pos = CDH.offset()
                CDH.w_chunk_data(pack("Z*", blender.computer))
                delta = 32 + pos - CDH.offset()
                CDH.w_chunk_data(pack(f"C{delta}", 0xED))
                CDH.w_chunk_data(
                    pack("VvC2", blender.ctime, blender.version, 0xED, 0xED),
                )
                blender.write(CDH)

            CDH.w_chunk_close()

        CDH.w_chunk_close()

    def write_names(self, CDH):
        print("	names\n")
        CDH.w_chunk_open(self.SHADERS_CHUNK_NAMES)
        CDH.w_chunk_data(pack("V", len(self.names)))
        for name in self.names:
            CDH.w_chunk_data(pack("Z*", name))

        CDH.w_chunk_close()

    def export(self, folder, mode):
        print("exporting...\n")

        mkpath(folder)
        self.export_constants(folder, mode)
        self.export_matrices(folder, mode)
        self.export_blenders(folder, mode)

    def export_constants(self, folder, mode):
        print("	constants\n")

        if mode and (mode == "bin"):
            write_file(folder + "\\CONSTANTS.bin", self.raw_constants)
        else:
            mkpath(folder + "\\CONSTANTS")
            for constant in self.constants:
                fh = open(
                    folder + "\\CONSTANTS\\" + constant.name + ".ltx",
                    "w",
                    encoding="cp1251",
                )
                fh.write("[general]\n")
                fh.write(f"name = {constant.name}\n")
                R = constant.waveforms[0].get()
                fh.write("\n[_R]\n")
                fh.write(f"type = {R[0]}\n")
                fh.write(f"args = {R[1:3]}\n")
                G = constant.waveforms[1].get()
                fh.write("\n[_G]\n")
                fh.write(f"type = {G[0]}\n")
                fh.write(f"args = {G[1:3]}\n")
                B = constant.waveforms[2].get()
                fh.write("\n[_B]\n")
                fh.write(f"type = {B[0]}\n")
                fh.write(f"args = {B[1:3]}\n")
                A = constant.waveforms[3].get()
                fh.write("\n[_A]\n")
                fh.write(f"type = {A[0]}\n")
                fh.write(f"args = {A[1:3]}\n")
                fh.close()

    def export_matrices(self, folder, mode):
        print("	matrices\n")

        if mode and (mode == "bin"):
            write_file(folder + "\\MATRICES.bin", self.raw_matrices)
        else:
            mkpath(folder + "\\MATRICES")
            for matrix in self.matrices:
                fh = open(
                    folder + "\\MATRICES\\" + matrix.name + ".ltx",
                    "w",
                    encoding="cp1251",
                )
                fh.write("[general]\n")
                fh.write(f"name = {matrix.name}\n")
                fh.write(f"dwmode = {matrix.dwmode}\n")
                fh.write(f"tcm = {matrix.tcm}\n")
                scaleU = matrix.scaleU.get()
                fh.write("\n[scaleU]\n")
                fh.write(f"type = {scaleU[0]}\n")
                fh.write("args = " + join(",", scaleU[1:3]) + "\n")
                scaleV = matrix.scaleV.get()
                fh.write("\n[scaleV]\n")
                fh.write(f"type = {scaleV[0]}\n")
                fh.write("args = " + join(",", scaleV[1:3]) + "\n")
                rotate = matrix.rotate.get()
                fh.write("\n[rotate]\n")
                fh.write(f"type = {rotate[0]}\n")
                fh.write("args = " + join(",", rotate[1:3]) + "\n")
                scrollU = matrix.scrollU.get()
                fh.write("\n[scrollU]\n")
                fh.write(f"type = {scrollU[0]}\n")
                fh.write("args = " + join(",", scrollU[1:3]) + "\n")
                scrollV = matrix.scrollV.get()
                fh.write("\n[scrollV]\n")
                fh.write(f"type = {scrollV[0]}\n")
                fh.write("args = " + join(",", scrollV[1:3]) + "\n")
                fh.close()

    def export_blenders(self, folder, mode):
        print("	blenders\n")
        mkpath(folder + "\\BLENDERS")
        for i, blender in enumerate(self.blenders):
            name = self.names[i]
            path = get_path(name)
            if len(path) > 0:
                mkpath(folder + "\\BLENDERS\\" + path[0])
            if mode and (mode == "bin"):
                write_file(folder + "\\BLENDERS\\" + name + ".bin", blender)
            else:
                ini = open(
                    folder + "\\BLENDERS\\" + name + ".ltx",
                    "w",
                    encoding="cp1251",
                )
                ini.write("[common]\n")
                ini.write(f"cls = {blender.cls}\n")
                ini.write(f"name = {blender.name}\n")
                ini.write(f"computer = {blender.computer}\n")
                ini.write(f"ctime = {blender.ctime}\n")
                ini.write(f"version = {blender.version}\n")
                blender.export(ini)
                ini.close()

    def my_import(self, folder, mode):
        print("importing...\n")

        self.import_constants(folder, mode)
        self.import_matrices(folder, mode)
        self.import_blenders(folder, mode)

    def import_constants(self, folder, mode):
        print("	constants\n")

        if mode and (mode == "bin"):
            self.raw_constants = read_file(folder + "\\CONSTANTS.bin")
        else:
            constants = get_filelist(folder + "\\CONSTANTS\\", "ltx")
            for path in constants:
                constant = universal_dict_object()
                ini = ini_file(path, "r")  # or fail("$path: $!\n");
                constant.name = ini.value("general", "name")
                for i in range(4):
                    constant.waveforms[i] = stkutils_math.create("waveform")

                constant.waveforms[0].set(
                    ini.value("_R", "type"),
                    split(r",\s*", ini.value("_R", "args")),
                )
                constant.waveforms[1].set(
                    ini.value("_G", "type"),
                    split(r",\s*", ini.value("_G", "args")),
                )
                constant.waveforms[2].set(
                    ini.value("_B", "type"),
                    split(r",\s*,", ini.value("_B", "args")),
                )
                constant.waveforms[3].set(
                    ini.value("_A", "type"),
                    split(r",\s*", ini.value("_A", "args")),
                )
                ini.close()
                self.constants.append(constant)

    def import_matrices(self, folder, mode):
        print("	matrices\n")

        if mode and (mode == "bin"):
            self.raw_matrices = read_file(folder + "\\MATRICES.bin")
        else:
            matrices = get_filelist(folder + "\\MATRICES\\", "ltx")
            for path in matrices:
                matrix = universal_dict_object()
                ini = ini_file(path, "r")  # or fail("$path: $!\n");
                matrix.name = ini.value("general", "name")
                matrix.dwmode = ini.value("general", "dwmode")
                matrix.tcm = ini.value("general", "tcm")
                matrix.scaleU = stkutils_math.create("waveform")
                matrix.scaleU.set(
                    ini.value("scaleU", "type"),
                    split(r",\s*", ini.value("scaleU", "args")),
                )
                matrix.scaleV = stkutils_math.create("waveform")
                matrix.scaleV.set(
                    ini.value("scaleV", "type"),
                    split(r",\s*", ini.value("scaleV", "args")),
                )
                matrix.rotate = stkutils_math.create("waveform")
                matrix.rotate.set(
                    ini.value("rotate", "type"),
                    split(r",\s*", ini.value("rotate", "args")),
                )
                matrix.scrollU = stkutils_math.create("waveform")
                matrix.scrollU.set(
                    ini.value("scrollU", "type"),
                    split(r",\s*", ini.value("scrollU", "args")),
                )
                matrix.scrollV = stkutils_math.create("waveform")
                matrix.scrollV.set(
                    ini.value("scrollV", "type"),
                    split(r",\s*", ini.value("scrollV", "args")),
                )
                ini.close()
                self.matrices.append(matrix)

    def import_blenders(self, folder, mode):
        print("	blenders\n")

        if mode and (mode == "bin"):
            blenders = get_filelist(folder + "\\BLENDERS\\", "bin")
            for path in blenders:
                self.blenders.append(read_file(path))
                self.names.append(self.prepare_path(path))

        else:
            blenders = get_filelist(folder + "\\BLENDERS\\", "ltx")
            for path in blenders:
                blender = universal_dict_object()
                ini = ini_file(path, "r")  # or fail("$path: $!\n");
                blender.cls = ini.value("common", "cls")
                blender.name = ini.value("common", "name")
                blender.computer = ini.value("common", "computer")
                blender.ctime = ini.value("common", "ctime")
                blender.version = ini.value("common", "version")
                # 			print("$blender.name: $blender.cls\n")
                # SWITCH: {
                if (blender.cls == "LmBmmD  ") or (  # CBlender_BmmD
                    blender.cls == "BmmDold "
                ):
                    bless(blender, "CBlender_BmmD")
                    blender._import(ini)
                elif (blender.cls == "MODELEbB") or (  # CBlender_Model_EbB
                    blender.cls == "LmEbB   "
                ):
                    bless(blender, "CBlender_EbB")
                    blender._import(ini)  # CBlender_LmEbB
                elif blender.cls == "D_STILL ":
                    bless(blender, "CBlender_Detail_Still")
                    blender._import(ini)
                elif blender.cls == "D_TREE  ":
                    bless(blender, "CBlender_Tree")
                    blender._import(ini)
                elif blender.cls == "LM_AREF ":
                    bless(blender, "CBlender_deffer_aref")
                    blender._import(ini)
                elif blender.cls == "V_AREF  ":
                    bless(blender, "CBlender_Vertex_aref")
                    blender._import(ini)
                elif blender.cls == "MODEL   ":
                    bless(blender, "CBlender_deffer_model")
                    blender._import(ini)
                elif (blender.cls == "E_SEL   ") or (  # CBlender_Editor_Selection
                    blender.cls == "E_WIRE  "
                ):
                    bless(blender, "CBlender_Editor")
                    blender._import(ini)  # CBlender_Editor_Wire
                elif blender.cls == "PARTICLE":
                    bless(blender, "CBlender_Particle")
                    blender._import(ini)
                elif blender.cls == "S_SET   ":
                    bless(blender, "CBlender_Screen_SET")
                    blender._import(ini)
                elif (
                    (blender.cls == "BLUR    ")  # CBlender_Blur, 		R1 only
                    or (blender.cls == "LM      ")  # CBlender_default,		R1 only
                    or (blender.cls == "SH_WORLD")  # CBlender_ShWorld, 		R1 only
                    or (blender.cls == "S_GRAY  ")  # CBlender_Screen_GRAY, 	R1 only
                    or (blender.cls == "V       ")
                ):
                    bless(blender, "CBlender_Tesselation")
                    blender._import(ini)  # CBlender_Vertex, 		R1 only
                else:
                    warning("unsupported cls " + blender.cls)
                    continue
                # }
                self.blenders.append(blender)
                self.names.append(self.prepare_path(path))

    def prepare_path(self, path):
        # $path =~ s/\//\\/g;
        temp = split("\\+", path)
        l = len(temp)
        i = 0
        for i, t in enumerate(temp):
            if t == "BLENDERS":
                break

        return substr(join("\\", temp[i:l]), 0, -4)


#######################################################################
class IBlender:
    # use strict;

    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def read(self, packet):
        self.properties["M_General"] = self.load_value(packet, self.xrPID_MARKER)
        self.properties["oPriority"] = self.load_value(packet, self.xrPID_INTEGER)
        self.properties["oStrictSorting"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["M_Base_Texture"] = self.load_value(packet, self.xrPID_MARKER)
        self.properties["oT_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
        self.properties["oT_xform"] = self.load_value(packet, self.xrPID_MATRIX)

    def write(self, CDH):
        self.save_value(CDH, "M_General", self.xrPID_MARKER)
        self.save_value(CDH, "oPriority", self.xrPID_INTEGER)
        self.save_value(CDH, "oStrictSorting", self.xrPID_BOOL)
        self.save_value(CDH, "M_Base_Texture", self.xrPID_MARKER)
        self.save_value(CDH, "oT_Name", self.xrPID_TEXTURE)
        self.save_value(CDH, "oT_xform", self.xrPID_MATRIX)

    def _import(self, ini):

        self.properties["M_General"].name = "General"
        self.properties["M_General"].value = None
        self.properties["oPriority"].name = "Priority"
        self.properties["oPriority"].value = split(
            r",\s*,",
            ini.value(
                self.properties["M_General"].name,
                self.properties["oPriority"].name,
            ),
        )
        self.properties["oStrictSorting"].name = "Strict sorting"
        self.properties["oStrictSorting"].value = ini.value(
            self.properties["M_General"].name,
            self.properties["oStrictSorting"].name,
        )
        self.properties["M_Base_Texture"].name = "Base Texture"
        self.properties["M_Base_Texture"].value = None
        self.properties["oT_Name"].name = "Name"
        self.properties["oT_Name"].value = ini.value(
            self.properties["M_Base_Texture"].name,
            self.properties["oT_Name"].name,
        )
        self.properties["oT_xform"].name = "Transform"
        self.properties["oT_xform"].value = ini.value(
            self.properties["M_Base_Texture"].name,
            self.properties["oT_xform"].name,
        )

    def export(self, ini):

        ini.write(f"\n[{self.properties['M_General'].name}]\n")
        ini.write(
            f"{self.properties['oPriority'].name} = "
            + join(",", self.properties["oPriority"].value)
            + "\n",
        )
        ini.write(
            f"{self.properties['oStrictSorting'].name} = {self.properties['oStrictSorting'].value}\n",
        )
        ini.write(f"\n[{self.properties['M_Base_Texture'].name}]\n")
        ini.write(
            f"{self.properties['oT_Name'].name} = {self.properties['oT_Name'].value}\n",
        )
        ini.write(
            f"{self.properties['oT_xform'].name} = {self.properties['oT_xform'].value}\n",
        )

    def load_value(self, packet, type):
        (marker) = packet.unpack("V")
        hash = universal_dict_object()
        # val;
        # SWITCH: {
        if marker == self.xrPID_MARKER and marker == type:
            (hash["name"]) = packet.unpack("Z*")
            hash["value"] = None
        elif (
            (marker == self.xrPID_MATRIX)
            or (marker == self.xrPID_TEXTURE)
            or (marker == self.xrPID_CONSTANT)
        ) and marker == type:
            (hash["name"], hash["value"]) = packet.unpack("Z*Z*")
            packet.pos(packet.pos() + 64 - length(hash["value"]) - 1)
        elif marker == self.xrPID_INTEGER and marker == type:
            (hash["name"], val) = packet.unpack("Z*V3")
            hash["value"] = val
        elif marker == self.xrPID_BOOL and marker == type:
            (hash["name"], hash["value"]) = packet.unpack("Z*V")
        elif marker == self.xrPID_TOKEN and marker == type:
            (hash["name"], val) = packet.unpack("Z*VV")
            hash["value"] = val
        # }
        return hash

    def save_value(self, CDH, prop, type):
        CDH.w_chunk_data(pack("VZ*", type, self.properties[prop].name))
        # SWITCH: {
        if (
            (type == self.xrPID_MATRIX)
            or (type == self.xrPID_TEXTURE)
            or (type == self.xrPID_CONSTANT)
        ):
            pos = CDH.offset()
            CDH.w_chunk_data(pack("Z*", self.properties[prop].value))
            delta = 64 + pos - CDH.offset()
            CDH.w_chunk_data(pack(f"C{delta}", 0xED))

        elif type == self.xrPID_INTEGER:
            CDH.w_chunk_data(pack("V3", self.properties[prop].value))
        elif type == self.xrPID_BOOL:
            CDH.w_chunk_data(pack("V", self.properties[prop].value))
        elif type == self.xrPID_TOKEN:
            CDH.w_chunk_data(pack("V2", self.properties[prop].value))

    # }

    def load_set(self, packet):
        set = universal_dict_object()
        (set.ID, set.name) = packet.unpack("VZ*")
        packet.pos(packet.pos() + 64 - length(set.name) - 1)
        return set

    def save_set(self, set, CDH):

        pos = CDH.offset()
        CDH.w_chunk_data(pack("VZ*", set.ID, set.name))
        delta = 68 + pos - CDH.offset()
        CDH.w_chunk_data(pack(f"C{delta}", 0xED))


#######################################################################
class CBlender_BmmD(IBlender):
    # use strict;
    # use base 'IBlender';

    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):

        super(IBlender, self).read(packet)

        self.properties["M_CBlender_BmmD"] = self.load_value(packet, self.xrPID_MARKER)
        self.properties["oT2_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
        self.properties["oT2_xform"] = self.load_value(packet, self.xrPID_MATRIX)
        if self.version >= 3:
            self.properties["oR_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
            self.properties["oG_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
            self.properties["oB_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
            self.properties["oA_Name"] = self.load_value(packet, self.xrPID_TEXTURE)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "M_CBlender_BmmD", self.xrPID_MARKER)
        self.save_value(CDH, "oT2_Name", self.xrPID_TEXTURE)
        self.save_value(CDH, "oT2_xform", self.xrPID_MATRIX)
        if self.version >= 3:
            self.save_value(CDH, "oR_Name", self.xrPID_TEXTURE)
            self.save_value(CDH, "oG_Name", self.xrPID_TEXTURE)
            self.save_value(CDH, "oB_Name", self.xrPID_TEXTURE)
            self.save_value(CDH, "oA_Name", self.xrPID_TEXTURE)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        self.properties["M_CBlender_BmmD"].name = ini.value("properties", "class")
        self.properties["M_CBlender_BmmD"].value = None
        self.properties["oT2_Name"].name = "Name"
        self.properties["oT2_Name"].value = ini.value(
            "properties",
            self.properties["oT2_Name"].name,
        )
        self.properties["oT2_xform"].name = "Transform"
        self.properties["oT2_xform"].value = ini.value(
            "properties",
            self.properties["oT2_xform"].name,
        )
        if self.version >= 3:
            self.properties["oR_Name"].name = "R2-R"
            self.properties["oR_Name"].value = ini.value(
                "properties",
                self.properties["oR_Name"].name,
            )
            self.properties["oG_Name"].name = "R2-G"
            self.properties["oG_Name"].value = ini.value(
                "properties",
                self.properties["oG_Name"].name,
            )
            self.properties["oB_Name"].name = "R2-B"
            self.properties["oB_Name"].value = ini.value(
                "properties",
                self.properties["oB_Name"].name,
            )
            self.properties["oA_Name"].name = "R2-A"
            self.properties["oA_Name"].value = ini.value(
                "properties",
                self.properties["oA_Name"].name,
            )

    def export(self, ini):

        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(f"class = {self.properties['M_CBlender_BmmD'].name}\n")
        ini.write(
            f"{self.properties['oT2_Name'].name} = {self.properties['oT2_Name'].value}\n",
        )
        ini.write(
            f"{self.properties['oT2_xform'].name} = {self.properties['oT2_xform'].value}\n",
        )
        if self.version >= 3:
            ini.write(
                f"{self.properties['oR_Name'].name} = {self.properties['oR_Name'].value}\n",
            )
            ini.write(
                f"{self.properties['oG_Name'].name} = {self.properties['oG_Name'].value}\n",
            )
            ini.write(
                f"{self.properties['oB_Name'].name} = {self.properties['oB_Name'].value}\n",
            )
            ini.write(
                f"{self.properties['oA_Name'].name} = {self.properties['oA_Name'].value}\n",
            )


#######################################################################
class CBlender_EbB(IBlender):
    # use strict;
    # use base '';

    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["M_CBlender_EbB"] = self.load_value(packet, self.xrPID_MARKER)
        self.properties["oT2_Name"] = self.load_value(packet, self.xrPID_TEXTURE)
        self.properties["oT2_xform"] = self.load_value(packet, self.xrPID_MATRIX)
        if self.version >= 1:
            self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "M_CBlender_EbB", self.xrPID_MARKER)
        self.save_value(CDH, "oT2_Name", self.xrPID_TEXTURE)
        self.save_value(CDH, "oT2_xform", self.xrPID_MATRIX)
        if self.version >= 1:
            self.save_value(CDH, "oBlend", self.xrPID_BOOL)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        self.properties["M_CBlender_EbB"].name = ini.value("properties", "class")
        self.properties["M_CBlender_EbB"].value = None
        self.properties["oT2_Name"].name = "Name"
        self.properties["oT2_Name"].value = ini.value(
            "properties",
            self.properties["oT2_Name"].name,
        )
        self.properties["oT2_xform"].name = "Transform"
        self.properties["oT2_xform"].value = ini.value(
            "properties",
            self.properties["oT2_xform"].name,
        )
        if self.version >= 1:
            self.properties["oBlend"].name = "Alpha-Blend"
            self.properties["oBlend"].value = ini.value(
                "properties",
                self.properties["oBlend"].name,
            )

    def export(self, ini):

        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(f"class = {self.properties['M_CBlender_EbB'].name}\n")
        ini.write(
            f"{self.properties['oT2_Name'].name} = {self.properties['oT2_Name'].value}\n",
        )
        ini.write(
            f"{self.properties['oT2_xform'].name} = {self.properties['oT2_xform'].value}\n",
        )
        if self.version >= 1:
            ini.write(
                f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
            )


#######################################################################
class CBlender_Detail_Still(IBlender):
    # use strict;
    # use base '';

    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):
        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oBlend", self.xrPID_BOOL)

    def _import(self, ini):
        super(IBlender, self)._import(ini)
        self.properties["oBlend"].name = "Alpha-blend"
        self.properties["oBlend"].value = ini.value(
            "properties",
            self.properties["oBlend"].name,
        )

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(
            f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
        )


#######################################################################
class CBlender_Tree(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)
        if self.version >= 1:
            self.properties["oNotAnTree"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oBlend", self.xrPID_BOOL)
        if self.version >= 1:
            self.save_value(CDH, "oNotAnTree", self.xrPID_BOOL)

    def _import(self, ini):
        super(IBlender, self)._import(ini)
        self.properties["oBlend"].name = "Alpha-blend"
        self.properties["oBlend"].value = ini.value(
            "properties",
            self.properties["oBlend"].name,
        )
        if self.version >= 1:
            self.properties["oNotAnTree"].name = "Object LOD"
            self.properties["oNotAnTree"].value = ini.value(
                "properties",
                self.properties["oNotAnTree"].name,
            )

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(
            f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
        )
        if self.version >= 1:
            ini.write(
                f"{self.properties['oNotAnTree'].name} = {self.properties['oNotAnTree'].value}\n",
            )


#######################################################################
class CBlender_deffer_aref(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        if self.version == 1:
            self.properties["oAREF"] = self.load_value(packet, self.xrPID_INTEGER)
            self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        if self.version == 1:
            self.save_value(CDH, "oAREF", self.xrPID_INTEGER)
            self.save_value(CDH, "oBlend", self.xrPID_BOOL)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        if self.version == 1:
            self.properties["oAREF"].name = "Alpha ref"
            self.properties["oAREF"].value = split(
                r",\s*",
                ini.value("properties", self.properties["oAREF"].name),
            )
            self.properties["oBlend"].name = "Alpha-blend"
            self.properties["oBlend"].value = ini.value(
                "properties",
                self.properties["oBlend"].name,
            )

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        if self.version == 1:
            ini.write(
                f"{self.properties['oAREF'].name} = "
                + join(",", self.properties["oAREF"].value)
                + "\n",
            )
            ini.write(
                f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
            )


#######################################################################
class CBlender_Vertex_aref(IBlender):
    # use strict;
    # use base '';

    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oAREF"] = self.load_value(packet, self.xrPID_INTEGER)
        if self.version > 0:
            self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oAREF", self.xrPID_INTEGER)
        if self.version > 0:
            self.save_value(CDH, "oBlend", self.xrPID_BOOL)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        self.properties["oAREF"].name = "Alpha ref"
        self.properties["oAREF"].value = split(
            r",\s*",
            ini.value("properties", self.properties["oAREF"].name),
        )
        if self.version > 0:
            self.properties["oBlend"].name = "Alpha-blend"
            self.properties["oBlend"].value = ini.value(
                "properties",
                self.properties["oBlend"].name,
            )

    def export(self, ini):

        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")

        ini.write(
            f"{self.properties['oAREF'].name} = "
            + join(",", self.properties["oAREF"].value)
            + "\n",
        )
        if self.version > 0:
            ini.write(
                f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
            )


#######################################################################
class CBlender_Tesselation(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):

        super(IBlender, self).read(packet)

        if self.version > 0:
            self.properties["oTess"] = self.load_value(packet, self.xrPID_TOKEN)
            for i in range(self.properties["oTess"].value[1]):
                self.properties["SETS"].append(self.load_set(packet))

    def write(self, CDH):
        super(IBlender, self).write(CDH)
        if self.version > 0:
            self.save_value(CDH, "oTess", self.xrPID_TOKEN)
            for set in self.properties["SETS"]:
                self.save_set(set, CDH)

    def _import(self, ini):
        super(IBlender, self)._import(ini)
        if self.version > 0:
            self.properties["oTess"].name = "Tessellation"
            self.properties["oTess"].value = split(
                r",\s*",
                ini.value("properties", self.properties["oTess"].name),
            )
            for i in range(self.properties["oTess"].value[1]):
                set = universal_dict_object()
                set.ID = i
                set.name = ini.value("sets", set.ID)
                self.properties["SETS"].append(set)

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")

        if self.version > 0:
            ini.write(
                f"{self.properties['oTess'].name} = "
                + join(",", self.properties["oTess"].value)
                + "\n",
            )
            ini.write("\n[sets]\n")
            for set in self.properties["SETS"]:
                ini.write(f"{set.ID} = {set.name}\n")


#######################################################################
class CBlender_deffer_model(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):

        super(IBlender, self).read(packet)

        if self.version >= 1:
            self.properties["oBlend"] = self.load_value(packet, self.xrPID_BOOL)
            self.properties["oAREF"] = self.load_value(packet, self.xrPID_INTEGER)
            if self.version >= 2:
                self.properties["oTess"] = self.load_value(packet, self.xrPID_TOKEN)
                for i in range(self.properties["oTess"].value[1]):
                    self.properties["SETS"].append(self.load_set(packet))

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        if self.version >= 1:
            self.save_value(CDH, "oBlend", self.xrPID_BOOL)
            self.save_value(CDH, "oAREF", self.xrPID_INTEGER)
            if self.version >= 2:
                self.save_value(CDH, "oTess", self.xrPID_TOKEN)
                for set in self.properties["SETS"]:
                    self.save_set(set, CDH)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        if self.version >= 1:
            self.properties["oAREF"].name = "Alpha ref"
            self.properties["oAREF"].value = split(
                r",\s*",
                ini.value("properties", self.properties["oAREF"].name),
            )
            self.properties["oBlend"].name = "Use alpha-channel"
            self.properties["oBlend"].value = ini.value(
                "properties",
                self.properties["oBlend"].name,
            )
            if self.version >= 2:
                self.properties["oTess"].name = "Tessellation"
                self.properties["oTess"].value = split(
                    r",\s*",
                    ini.value("properties", self.properties["oTess"].name),
                )
                for i in range(self.properties["oTess"].value[1]):
                    set = universal_dict_object()
                    set.ID = i
                    set.name = ini.value("sets", set.ID)
                    self.properties["SETS"].append(set)

    def export(self, ini):

        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        if self.version >= 1:
            ini.write(
                f"{self.properties['oAREF'].name} = "
                + join(",", self.properties["oAREF"].value)
                + "\n",
            )
            ini.write(
                f"{self.properties['oBlend'].name} = {self.properties['oBlend'].value}\n",
            )
            if self.version >= 2:
                ini.write(
                    f"{self.properties['oTess'].name} = "
                    + join(",", self.properties["oTess"].value)
                    + "\n",
                )
                ini.write("\n[sets]\n")
                for set in self.properties["SETS"]:
                    ini.write(f"{set.ID} = {set.name}\n")


#######################################################################
class CBlender_Editor(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oT_Factor"] = self.load_value(packet, self.xrPID_CONSTANT)

    def write(self, CDH):
        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oT_Factor", self.xrPID_CONSTANT)

    def _import(self, ini):
        super(IBlender, self)._import(ini)
        self.properties["oT_Factor"].name = "TFactor"
        self.properties["oT_Factor"].value = ini.value(
            "properties",
            self.properties["oT_Factor"].name,
        )

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(
            f"{self.properties['oT_Factor'].name} = {self.properties['oT_Factor'].value}\n",
        )


#######################################################################
class CBlender_Particle(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oBlend"] = self.load_value(packet, self.xrPID_TOKEN)
        for i in range(self.properties["oBlend"].value[1]):
            self.properties["SETS"].append(self.load_set(packet))

        self.properties["oClamp"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["oAREF"] = self.load_value(packet, self.xrPID_INTEGER)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oBlend", self.xrPID_TOKEN)
        for set in self.properties["SETS"]:
            self.save_set(set, CDH)

        self.save_value(CDH, "oClamp", self.xrPID_BOOL)
        self.save_value(CDH, "oAREF", self.xrPID_INTEGER)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        self.properties["oBlend"].name = "Blending"
        self.properties["oBlend"].value = split(
            r",\s*",
            ini.value("properties", self.properties["oBlend"].name),
        )
        self.properties["oClamp"].name = "Texture clamp"
        self.properties["oClamp"].value = ini.value(
            "properties",
            self.properties["oClamp"].name,
        )
        self.properties["oAREF"].name = "Alpha ref"
        self.properties["oAREF"].value = split(
            r",\s*",
            ini.value("properties", self.properties["oAREF"].name),
        )
        for i in range(self.properties["oBlend"].value[1]):
            set = universal_dict_object()
            set.ID = i
            set.name = ini.value("sets", set.ID)
            self.properties["SETS"].append(set)

    def export(self, ini):
        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(
            f"{self.properties['oBlend'].name} = "
            + join(",", self.properties["oBlend"].value)
            + "\n",
        )
        ini.write(
            f"{self.properties['oClamp'].name} = {self.properties['oClamp'].value}\n",
        )
        ini.write(
            f"{self.properties['oAREF'].name} = "
            + join(",", self.properties["oAREF"].value)
            + "\n",
        )
        ini.write("\n[sets]\n")
        for set in self.properties["SETS"]:
            ini.write(f"{set.ID} = {set.name}\n")


#######################################################################
class CBlender_Screen_SET(IBlender):
    xrPID_MARKER = 0
    xrPID_MATRIX = 1
    xrPID_CONSTANT = 2
    xrPID_TEXTURE = 3
    xrPID_INTEGER = 4
    xrPID_BOOL = 6
    xrPID_TOKEN = 7

    def __init__(self):
        self.properties = universal_dict_object()

    def read(self, packet):
        super(IBlender, self).read(packet)

        self.properties["oBlend"] = self.load_value(packet, self.xrPID_TOKEN)
        for i in range(self.properties["oBlend"].value[1]):
            self.properties["SETS"].append(self.load_set(packet))

        if self.version != 2:
            self.properties["oClamp"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["oAREF"] = self.load_value(packet, self.xrPID_INTEGER)
        self.properties["oZTest"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["oZWrite"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["oLighting"] = self.load_value(packet, self.xrPID_BOOL)
        self.properties["oFog"] = self.load_value(packet, self.xrPID_BOOL)

    def write(self, CDH):

        super(IBlender, self).write(CDH)
        self.save_value(CDH, "oBlend", self.xrPID_TOKEN)
        for set in self.properties["SETS"]:
            self.save_set(set, CDH)

        self.save_value(CDH, "oClamp", self.xrPID_BOOL)
        self.save_value(CDH, "oAREF", self.xrPID_INTEGER)
        self.save_value(CDH, "oZTest", self.xrPID_BOOL)
        self.save_value(CDH, "oZWrite", self.xrPID_BOOL)
        self.save_value(CDH, "oLighting", self.xrPID_BOOL)
        self.save_value(CDH, "oFog", self.xrPID_BOOL)

    def _import(self, ini):

        super(IBlender, self)._import(ini)
        self.properties["oBlend"].name = "Blending"
        self.properties["oBlend"].value = split(
            r",\s*",
            ini.value("properties", self.properties["oBlend"].name),
        )
        self.properties["oClamp"].name = "Texture clamp"
        self.properties["oClamp"].value = ini.value(
            "properties",
            self.properties["oClamp"].name,
        )
        self.properties["oAREF"].name = "Alpha ref"
        self.properties["oAREF"].value = split(
            r",\s*",
            ini.value("properties", self.properties["oAREF"].name),
        )
        self.properties["oZTest"].name = "Z-test"
        self.properties["oZTest"].value = ini.value(
            "properties",
            self.properties["oZTest"].name,
        )
        self.properties["oZWrite"].name = "Z-write"
        self.properties["oZWrite"].value = ini.value(
            "properties",
            self.properties["oZWrite"].name,
        )
        self.properties["oLighting"].name = "Lighting"
        self.properties["oLighting"].value = ini.value(
            "properties",
            self.properties["oLighting"].name,
        )
        self.properties["oFog"].name = "Fog"
        self.properties["oFog"].value = ini.value(
            "properties",
            self.properties["oFog"].name,
        )
        for i in range(self.properties["oBlend"].value[1]):
            set = universal_dict_object()
            set.ID = i
            set.name = ini.value("sets", set.ID)
            self.properties["SETS"].append(set)

    def export(self, ini):

        super(IBlender, self).export(ini)
        ini.write("\n[properties]\n")
        ini.write(
            f"{self.properties['oBlend'].name} = "
            + join(",", self.properties["oBlend"].value)
            + "\n",
        )
        if self.version != 2:
            ini.write(
                f"{self.properties['oClamp'].name} = {self.properties['oClamp'].value}\n",
            )
        ini.write(
            f"{self.properties['oAREF'].name} = "
            + join(",", self.properties["oAREF"].value)
            + "\n",
        )
        ini.write(
            f"{self.properties['oZTest'].name} = {self.properties['oZTest'].value}\n",
        )
        ini.write(
            f"{self.properties['oZWrite'].name} = {self.properties['oZWrite'].value}\n",
        )
        ini.write(
            f"{self.properties['oLighting'].name} = {self.properties['oLighting'].value}\n",
        )
        ini.write(f"{self.properties['oFog'].name} = {self.properties['oFog'].value}\n")
        ini.write("\n[sets]\n")
        for set in self.properties["SETS"]:
            ini.write(f"{set.ID} = {set.name}\n")


#######################################################################
