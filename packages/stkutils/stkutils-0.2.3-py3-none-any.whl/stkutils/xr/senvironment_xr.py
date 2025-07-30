# S.T.A.L.K.E.R. senvironment.xr handling module
# Update history:
# 	28/08/2012 - initial release
##############################################
import os

from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import chdir, fail, mkpath, universal_dict_object
from stkutils.utils import get_filelist


class senvironment_xr:
    # use strict;
    # use stkutils::debug qw(fail);
    # use stkutils::data_packet;
    # use stkutils::ini_file;
    # use stkutils::utils qw(get_filelist);
    # use File::Path qw(mkpath);

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
            packet = data_packet(fh.r_chunk_data())
            obj = universal_dict_object()
            (
                obj.Version,
                obj.Name,
                obj.Room,
                obj.RoomHF,
                obj.RoomRolloffFactor,
                obj.DecayTime,
                obj.DecayHFRatio,
                obj.Reflections,
                obj.ReflectionsDelay,
                obj.Reverb,
                obj.ReverbDelay,
                obj.Size,
                obj.Diffusion,
                obj.AirAbsorptionHF,
            ) = packet.unpack("VZ*f12")
            if obj.Version > 3:
                (obj.PresetID) = packet.unpack("V")
            if packet.resid() != 0:
                fail("there is some data left in packet: " + packet.resid())
            fh.r_chunk_close()
            self.envs.append(obj)

        if _fh is None:
            fh.close()

    def write(self, _fh):
        if _fh is None:
            fh = chunked(self.data, "data")
        else:
            fh = _fh

        for i, obj in enumerate(sorted(self.envs, key=lambda a: a.Name)):
            packet = data_packet()
            packet.pack(
                "VZ*f12",
                obj.Version,
                obj.Name,
                obj.Room,
                obj.RoomHF,
                obj.RoomRolloffFactor,
                obj.DecayTime,
                obj.DecayHFRatio,
                obj.Reflections,
                obj.ReflectionsDelay,
                obj.Reverb,
                obj.ReverbDelay,
                obj.Size,
                obj.Diffusion,
                obj.AirAbsorptionHF,
            )
            if obj.Version > 3:
                packet.pack("V", obj.PresetID)
            fh.w_chunk(i, packet.data())

        self.data = fh.data()
        if _fh is None:
            fh.close()

    def export(self, out):
        mkpath(out)
        chdir(out)  # or fail ("$out: $!\n");
        for object in self.envs:
            fn = object.Name + ".ltx"
            ini = open(
                os.path.join(out, fn),
                "w",
                encoding="cp1251",
            )  # or fail("$fn: $!\n");
            ini.write("[header]\n")
            ini.write(f"name = {object.Name}\n")
            ini.write(f"version = {object.Version}\n\n")
            ini.write("[environment]\n")
            ini.write("size = %.5g\n" % object.Size)
            ini.write("diffusion = %.5g\n" % object.Diffusion)
            if object.Version > 3:
                ini.write(f"preset_id = {object.PresetID}\n\n")
            else:
                ini.write("\n")

            ini.write("[room]\n")
            ini.write("room = %.5g\n" % object.Room)
            ini.write("room_hf = %.5g\n\n" % object.RoomHF)
            ini.write("[distance_effects]\n")
            ini.write("room_rolloff_factor = %.5g\n" % object.RoomRolloffFactor)
            ini.write("air_absorption_hf = %.5g\n\n" % object.AirAbsorptionHF)
            ini.write("[decay]\n")
            ini.write("decay_time = %.5g\n" % object.DecayTime)
            ini.write("decay_hf_ratio = %.5g\n\n" % object.DecayHFRatio)
            ini.write("[reflections]\n")
            ini.write("reflections = %.5g\n" % object.Reflections)
            ini.write("reflections_delay = %.5g\n\n" % object.ReflectionsDelay)
            ini.write("[reverb]\n")
            ini.write("reverb = %.5g\n" % object.Reverb)
            ini.write("reverb_delay = %.5g\n" % object.ReverbDelay)
            ini.close()

    def my_import(self, out):

        list = get_filelist(out, "ltx")
        for file in list:
            ini = ini_file(file, "r")  # or fail("$file: $!\n");
            obj = universal_dict_object()
            obj.Version = ini.value("header", "version")
            obj.Name = ini.value("header", "name")
            obj.Size = ini.value("environment", "size")
            obj.Diffusion = ini.value("environment", "diffusion")
            obj.AirAbsorptionHF = ini.value("distance_effects", "air_absorption_hf")
            if obj.Version > 3:
                obj.PresetID = ini.value("environment", "preset_id")
            obj.Room = ini.value("room", "room")
            obj.RoomHF = ini.value("room", "room_hf")
            obj.RoomRolloffFactor = ini.value("distance_effects", "room_rolloff_factor")
            obj.DecayTime = ini.value("decay", "decay_time")
            obj.DecayHFRatio = ini.value("decay", "decay_hf_ratio")
            obj.Reflections = ini.value("reflections", "reflections")
            obj.ReflectionsDelay = ini.value("reflections", "reflections_delay")
            obj.Reverb = ini.value("reverb", "reverb")
            obj.ReverbDelay = ini.value("reverb", "reverb_delay")
            self.envs.append(obj)
            ini.close()


#################################################################################
