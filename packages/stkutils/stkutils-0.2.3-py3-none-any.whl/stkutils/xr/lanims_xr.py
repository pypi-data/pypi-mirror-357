# S.T.A.L.K.E.R. lanims.xr handling module
# Update history:
# 	29/08/2012 - initial release
##############################################
import re

from stkutils.binary_data import pack, unpack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import chdir, mkpath, split, universal_dict_object
from stkutils.utils import get_filelist, get_path


class lanims_xr:

    def __init__(self, data=""):
        self.data = data

    def read(self, _fh=None):
        if _fh is None:
            fh = chunked(self.data, "data")
        else:
            fh = _fh
        while 1:
            (index, size) = fh.r_chunk_open()
            if not (index is not None):
                break

            if index == 0:
                (self.version,) = unpack("v", fh.r_chunk_data())
            elif index == 1:
                self.read_laitem(fh)

            fh.r_chunk_close()

        if _fh is None:
            fh.close()

    def read_laitem(self, fh):

        while 1:
            (index, size) = fh.r_chunk_open()
            if not (index is not None):
                break
            laitem = universal_dict_object()
            while 1:
                (in_index, in_size) = fh.r_chunk_open()
                if not (in_index is not None):
                    break
                # SWITCH: {
                if in_index == 1:
                    (laitem.name, laitem.fps, laitem.frame_count) = unpack(
                        "Z*fV",
                        fh.r_chunk_data(),
                    )
                elif in_index == 2:
                    packet = data_packet(fh.r_chunk_data())
                    (count) = packet.unpack("V", 4)
                    for i in range(count):
                        key = universal_dict_object()
                        (key.frame, key.color) = packet.unpack("VV", 8)
                        laitem.keys.append(key)

                fh.r_chunk_close()

            fh.r_chunk_close()
            self.laitems.append(laitem)

    def write(self, _fh=None):

        if _fh is None:
            fh = chunked("", "data")
        else:
            fh = _fh

        packet = data_packet()
        fh.w_chunk(0, pack("v", 1))  # version
        fh.w_chunk_open(1)
        for i, obj in enumerate(self.laitems):
            fh.w_chunk_open(i)

            fh.w_chunk(1, pack("Z*fV", obj.name, obj.fps, obj.frame_count))

            fh.w_chunk_open(2)
            fh.w_chunk_data(pack("V", len(obj.keys)))
            for key in obj.keys:
                fh.w_chunk_data(pack("VV", key.frame, key.color))

            fh.w_chunk_close()

            fh.w_chunk_close()

        fh.w_chunk_close()
        self.data = fh.data()
        if _fh is None:
            fh.close()

    def export(self, out, mode):

        mkpath(out)
        chdir(out)  # or fail ("$out: $!\n");
        for laitem in self.laitems:
            str = laitem.name + ".ltx"
            (path, fn) = get_path(str)
            if (path is not None) and (path != ""):
                mkpath(path)
            ini = open(str, "w", encoding="cp1251")  # or fail("$str: $!\n");
            ini.write("[header]\n")
            ini.write(f"name = {laitem.name}\n")
            ini.write(f"fps = {laitem.fps}\n")
            ini.write(f"frame_count = {laitem.frame_count}\n\n")
            ini.write("[keys]\n")
            ini.write("keys_count = " + str(len(laitem.keys)) + "\n\n")

            for i, key in enumerate(laitem.keys):
                ini.write(f"{i}:frame = {key.frame}\n")
                ini.write(f"{i}:color = ")
                if mode and mode == 1:
                    A = (key.color >> 24) & 0xFF
                    R = (key.color >> 16) & 0xFF
                    G = (key.color >> 8) & 0xFF
                    B = key.color & 0xFF
                    ini.write("%u:%u:%u:%u\n\n" % (A, R, G, B))
                else:
                    ini.write(f"{key.color}\n\n")

            ini.close()

    def my_import(self, src):

        list = get_filelist(src, "ltx")
        for file in list:
            ini = ini_file(file, "r")  # or fail("$file: $!\n");
            obj = universal_dict_object()
            obj.fps = ini.value("header", "fps")
            obj.name = ini.value("header", "name")
            obj.frame_count = ini.value("header", "frame_count")
            count = ini.value("keys", "keys_count")
            for i in range(count):
                key = universal_dict_object()
                key.frame = ini.value("keys", f"{i}:frame")
                key.color = ini.value("keys", f"{i}:color")
                if re.match(":", key.color):
                    temp = split(":", key.color)
                    key.color = (
                        (temp[0] << 24) + (temp[1] << 16) + (temp[2] << 8) + temp[3]
                    )

                obj.keys.append(key)

            self.laitems.append(obj)
            ini.close()


#################################################################################
