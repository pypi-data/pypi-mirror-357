# Module for handling thm files
# Update history:
# 	20/01/2013 - initial release
##################################################
from stkutils.binary_data import pack, unpack
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, substr


class texture_thumbnail:
    THM_CHUNK_VERSION = 0x0810
    THM_CHUNK_DATA = 0x0811
    THM_CHUNK_TEXTUREPARAM = 0x0812
    THM_CHUNK_TYPE = 0x0813
    THM_CHUNK_TEXTUREPARAM_TYPE = 0x0814
    THM_CHUNK_TEXTUREPARAM_DETAIL = 0x0815
    THM_CHUNK_TEXTUREPARAM_MATERIAL = 0x0816
    THM_CHUNK_TEXTUREPARAM_BUMP = 0x0817
    THM_CHUNK_TEXTUREPARAM_NMAP = 0x0818
    THM_CHUNK_TEXTUREPARAM_FADE = 0x0819

    def __init__(self, type):
        self.version = 0x12
        self.type = type

    def set_bump_name(*args):
        args[0].bump_name = args[1]

    def set_material(*args):
        args[0].material = args[1]

    def set_detail_name(*args):
        args[0].detail_name = args[1]

    def set_detail_scale(*args):
        args[0].detail_scale = args[1]

    def read(self, CDH):

        while 1:
            (index, size) = CDH.r_chunk_open()
            # defined $index or last;
            if index is None:
                break
            packet = data_packet(CDH.r_chunk_data())
            # SWITCH: {
            if index == self.THM_CHUNK_VERSION:
                self.read_version(packet)
            elif index == self.THM_CHUNK_DATA:
                self.read_data(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM:
                self.read_textureparam(packet)
            elif index == self.THM_CHUNK_TYPE:
                self.read_type(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_TYPE:
                self.read_textureparam_type(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_DETAIL:
                self.read_textureparam_detail(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_MATERIAL:
                self.read_textureparam_material(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_BUMP:
                self.read_textureparam_bump(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_NMAP:
                self.read_textureparam_nmap(packet)
            elif index == self.THM_CHUNK_TEXTUREPARAM_FADE:
                self.read_textureparam_fade(packet)
            # }
            CDH.r_chunk_close()

    def read_version(self, packet):
        (self.version) = packet.unpack("v")
        if self.version != 0x12:
            fail("unknown version " + self.version)

    def read_data(self, packet):

        self.data = packet.data()

    def read_textureparam(self, packet):
        (
            self.fmt,
            self.flags,
            self.border_color,
            self.fade_color,
            self.fade_amount,
            self.mip_filter,
            self.width,
            self.height,
        ) = packet.unpack("VVVVVVVV")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_type(self, packet):

        (self.type) = packet.unpack("V")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_type(self, packet):
        (self.texture_type) = packet.unpack("V")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_detail(self, packet):
        (self.detail_name, self.detail_scale) = packet.unpack("Z*f")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_material(self, packet):
        (self.material, self.material_weight) = packet.unpack("Vf")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_bump(self, packet):
        (self.bump_virtual_height, self.bump_mode, self.bump_name) = packet.unpack(
            "fVZ*",
        )
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_nmap(self, packet):
        (self.ext_normal_map_name) = packet.unpack("Z*")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_textureparam_fade(self, packet):
        (self.fade_delay) = packet.unpack("C")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def get_data_from_texture(self, *args):
        data = substr(args[0], 0, 128)
        (dwMagic,) = unpack("V", substr(data, 0, 4))
        if dwMagic != 542327876:
            fail("this is not dds")
        (self.fmt,) = unpack("V", substr(data, 80, 4))
        (self.width,) = unpack("V", substr(data, 12, 4))
        (self.height,) = unpack("V", substr(data, 8, 4))

    def write(self, CDH):
        index = 0
        if self.flag == 1:
            CDH.w_chunk(index, pack("V", 1))
            index += 1

        for ps_static in self.ps_statics:
            packet = data_packet()
            ps_static.write(packet)
            CDH.w_chunk(index, packet.data())
            index += 1


#######################################################################
