# S.T.A.L.K.E.R. shaders_xrlc.xr handling module
# Update history:
# 	28/08/2012 - initial release
##############################################
from stkutils import perl_utils
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file


class shaders_xrlc_xr:
    # use strict;
    # use stkutils::debug qw(fail);
    # use stkutils::data_packet;

    FL_CSF_COLLISION = 0x1
    FL_CSF_RENDERING = 0x2
    FL_CSF_OPTIMIZE_UV = 0x4
    FL_CSF_VERTEX_LIGHT = 0x8
    FL_CSF_CAST_SHADOW = 0x10
    FL_CSF_UNKNOWN_1 = 0x20
    FL_CSF_UNKNOWN_2 = 0x40

    def __init__(self, data=""):
        self.data = data

    def read(self):

        packet = data_packet(self.data)
        shCount = perl_utils.length() / 0x90
        if perl_utils.length() % 144 != 0:
            perl_utils.fail("bad file")
        for i in range(shCount):
            shader = perl_utils.universal_dict_object()
            pos = packet.pos()
            (shader.name) = packet.unpack("Z*")
            packet.pos(pos + 0x80)
            (shader.flags, shader.translucency, shader.ambient, shader.lm_density) = (
                packet.unpack("Vfff")
            )
            self.shaders.append(shader)

        if packet.resid() != 0:
            perl_utils.fail("there is some data left in packet:" + packet.resid())

    def write(self):
        packet = data_packet()
        for object in self.shaders:
            packet.pack("Z*", object.name)
            zero_count = 0x80 - perl_utils.length(object.name) - 1
            for i in range(zero_count):
                packet.pack("C", 0)

            packet.pack(
                "Vfff",
                object.flags,
                object.translucency,
                object.ambient,
                object.lm_density,
            )

        self.data = packet.data()

    def export(self, ini):
        ini.write("[shaders_xrlc]\n")
        ini.write("count = " + ((len(self.shaders) - 1) + 1) + "\n")
        for i, shader in enumerate(self.shaders):
            ini.write(f"[{i}]\n")
            ini.write(f"name = {shader.name}\n")
            ini.write("flags = ")
            bFlags = shader.flags
            if bFlags & self.FL_CSF_COLLISION == self.FL_CSF_COLLISION:
                ini.write("CSF_COLLISION,")
            if bFlags & self.FL_CSF_RENDERING == self.FL_CSF_RENDERING:
                ini.write("CSF_RENDERING,")
            if bFlags & self.FL_CSF_OPTIMIZE_UV == self.FL_CSF_OPTIMIZE_UV:
                ini.write("CSF_OPTIMIZE_UV,")
            if bFlags & self.FL_CSF_VERTEX_LIGHT == self.FL_CSF_VERTEX_LIGHT:
                ini.write("CSF_VERTEX_LIGHT,")
            if bFlags & self.FL_CSF_CAST_SHADOW == self.FL_CSF_CAST_SHADOW:
                ini.write("CSF_CAST_SHADOW,")
            if bFlags & self.FL_CSF_UNKNOWN_1 == self.FL_CSF_UNKNOWN_1:
                ini.write("CSF_UNKNOWN_1,")
            if bFlags & self.FL_CSF_UNKNOWN_2 == self.FL_CSF_UNKNOWN_2:
                ini.write("CSF_UNKNOWN_2,")
            if (bFlags & 0x80) != 0:
                print(f"{shader.name}: SOME ADDITIONAL FLAGS EXISTS!\n")
            ini.write("\n")
            ini.write("translucency = %.5g\n" % shader.translucency)
            ini.write("ambient = %.5g\n" % shader.ambient)
            ini.write("lm_density = %.5g\n" % shader.lm_density)

    def my_import(self, ini: ini_file):

        (count) = ini.value("shaders_xrlc", "count")
        for i in range(count):
            shader = perl_utils.universal_dict_object()
            conv_flags = 0
            raw_flags = perl_utils.split(r",\s*", ini.value(f"{i}", "flags"))
            for flag in raw_flags:

                if flag == "CSF_COLLISION":
                    conv_flags &= self.FL_CSF_COLLISION
                if flag == "CSF_OPTIMIZE_UV":
                    conv_flags &= self.FL_CSF_OPTIMIZE_UV
                if flag == "CSF_RENDERING":
                    conv_flags &= self.FL_CSF_RENDERING
                if flag == "CSF_CAST_SHADOW":
                    conv_flags &= self.FL_CSF_CAST_SHADOW
                if flag == "CSF_VERTEX_LIGHT":
                    conv_flags &= self.FL_CSF_VERTEX_LIGHT
                if flag == "CSF_UNKNOWN_2":
                    conv_flags &= self.FL_CSF_UNKNOWN_2
                if flag == "CSF_UNKNOWN_1":
                    conv_flags &= self.FL_CSF_UNKNOWN_1

            shader.dummy = conv_flags
            shader.name = ini.value(f"{i}", "name")
            shader.translucency = ini.value(f"{i}", "translucency")
            shader.ambient = ini.value(f"{i}", "ambient")
            shader.lm_density = ini.value(f"{i}", "lm_density")
            self.shaders.append(shader)


#################################################################################
