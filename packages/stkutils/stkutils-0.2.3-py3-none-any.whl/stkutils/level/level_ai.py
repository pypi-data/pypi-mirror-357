# Module for handling level.ai stalker files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax
##################################################
from stkutils.binary_data import unpack
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, substr


class level_ai:
    # use strict;
    # use chunked;
    # use data_packet;
    # use debug qw(fail);
    def __init__(self, data=""):
        self.data = data
        self.vertex_data = ""
        self.header = ai_header()

    def read(self, mode):
        (switch,) = unpack("V", substr(self.data, 0, 4))
        if switch > 6:
            if switch > 7:
                self.header.read(data_packet(substr(self.data, 0, 56)))
                self.vertex_data = substr(self.data, 56)
            else:
                self.header.read(data_packet(substr(self.data, 0, 40)))
                self.vertex_data = substr(self.data, 40)

        else:
            fail("unsupported version")

        if mode is not None and mode == "full":
            self._read_vertices()

    def _read_vertices(self):
        packet = data_packet(self.vertex_data)
        for i in range(self.header.vertex_count):
            vertex = ai_vertex(self.header.version)
            vertex.read(packet)
            self.vertices.append(vertex)

    def write(self, mode):
        packet = data_packet()
        self.header.write(packet)
        if mode is not None and mode == "full":
            self._write_vertices()

        data = packet.data().self.vertex_data
        self.data = data

    def _write_vertices(self):
        packet = data_packet()
        for vertex in self.vertices:
            vertex.write(packet)

        self.vertex_data = packet.data()


######################################################
class ai_header:
    header = (
        {"name": "version", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "cell_size", "type": "f32"},
        {"name": "factor_y", "type": "f32"},
        {"name": "bbox_min", "type": "f32v3"},
        {"name": "bbox_max", "type": "f32v3"},
        {"name": "level_guid", "type": "guid"},
    )

    def __init__(self, version):
        self.version = version

    # my $class = shift;
    # my self = universal_dict_object();
    # bless(self, $class);
    # return self;

    def read(self, arg):
        arg.unpack_properties(self, self.header[0:5])
        if self.version > 7:
            arg.unpack_properties(self, self.header[6])

    def write(self, arg):
        arg.pack_properties(self, self.header[0:5])
        if self.version > 7:
            arg.pack_properties(self, self.header[6])

    def export(self, fh):

        fh.write("version = self.version\n")
        fh.write("vertex_count = self.vertex_count\n")
        fh.write("cell_size = self.cell_size\n")
        fh.write("factor_y = self.factor_y\n")
        fh.write("bbox_min = self.bbox_min\n")
        fh.write("bbox_max = self.bbox_max\n")
        if self.version > 7:
            fh.write("level_guid = self.level_guid\n")
        fh.write("\n")

    def _import(self, fh):
        self.version = fh.value("header", "version")
        self.vertex_count = fh.value("header", "vertex_count")
        self.cell_size = fh.value("header", "cell_size")
        self.factor_y = fh.value("header", "factor_y")
        self.bbox_min = fh.value("header", "bbox_min")
        self.bbox_max = fh.value("header", "bbox_max")
        self.level_guid = fh.value("header", "level_guid")


######################################################
class ai_vertex:
    vertex = (
        {"name": "data", "type": "ha1"},
        {"name": "cover", "type": "u16"},
        {"name": "low_cover", "type": "u16"},
        {"name": "plane", "type": "u16"},
        {"name": "packed_xz_lo", "type": "u16"},
        {"name": "packed_xz_hi", "type": "u8"},
        {"name": "packed_y", "type": "u16"},
    )

    def __init__(self, version):
        self.version = version

    # 	my $class = shift;
    # 	my self = universal_dict_object();
    # 	self.version = self;
    # 	bless(self, $class);
    # 	return self;
    # }
    def read(self, arg):
        arg.unpack_properties(self, self.vertex[0:1])
        if self.version > 9:
            arg.unpack_properties(self, self.vertex[2])

        arg.unpack_properties(self, self.vertex[3:6])

    def write(self, arg):
        arg.pack_properties(self, self.vertex[0:1])
        if self.version > 9:
            arg.pack_properties(self, self.vertex[2])

        arg.pack_properties(self, self.vertex[3:6])

    def export(self, fh):
        print("not implemented\n")

    def _import(self, fh, i):
        print("not implemented\n")


######################################################
