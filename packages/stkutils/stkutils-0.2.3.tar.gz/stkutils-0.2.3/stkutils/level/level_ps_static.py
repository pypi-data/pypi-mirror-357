# Module for handling level.ps_static stalker files
# Update history:
# 	17/01/2013 - initial release
##################################################
from stkutils.binary_data import pack
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import fail, universal_dict_object


class level_ps_static:
    # use strict;
    # use data_packet;
    # use ini_file;
    # use debug qw(fail warn);

    def __init__(self):
        self.flag = 0
        self.config = universal_dict_object()

    def read(self, CDH):
        expected_index = 0
        if self.flag == 1:
            (index, size) = CDH.r_chunk_open()
            # 		warn('load switch is off') unless $index == 1;
            CDH.r_chunk_close()
            expected_index = 1

        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index:
                break
            # defined $index or last;
            if expected_index != index:
                fail("chunk " + index + " have unproper index")
            packet = data_packet(CDH.r_chunk_data())
            ps_static = ps_static()
            ps_static.flag = self.flag
            ps_static.read(packet)
            if packet.resid() != 0:
                fail("there is some data left in packet: " + packet.resid())
            self.ps_statics.append(ps_static)
            expected_index += 1
            CDH.r_chunk_close()

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

    def my_import(self, arg):
        IFH = ini_file(arg, "r")  # or die;
        for section in IFH.sections_list:
            ps_static = ps_static()
            ps_static.flag = self.flag
            ps_static._import(IFH, section)
            self.ps_statics.append(ps_static)

        IFH.close()

    def export(self, arg):
        IFH = ini_file(arg, "w")  # or die;
        RFH = IFH.fh
        # index = 0;
        for index, ps_static in self.ps_statics:
            RFH.write(f"[{index}]\n")
            ps_static.export(IFH, f"{index}")
            RFH.write("\n")

        IFH.close()


#######################################################################
class ps_static:
    # use strict;
    properties_info = (
        {"name": "particle_name", "type": "sz"},
        {"name": "matrix_1", "type": "f32v4"},
        {"name": "matrix_2", "type": "f32v4"},
        {"name": "matrix_3", "type": "f32v4"},
        {"name": "matrix_4", "type": "f32v4"},
    )
    cs_properties_info = ({"name": "load_switch", "type": "u16"},)

    def __init__(self):
        # my $class = shift;
        # my self = universal_dict_object();
        self.flag = 0

    # 	bless self, $class;
    # 	return self;
    # }

    def read(self, arg):
        if self.flag == 1:
            arg.unpack_properties(self, self.cs_properties_info)

        arg.unpack_properties(self, self.properties_info)

    def write(self, arg):
        if self.flag == 1:
            arg.pack_properties(self, self.cs_properties_info)

        arg.pack_properties(self, self.properties_info)

    def _import(self, arg, v):
        if self.flag == 1:
            arg.import_properties(v, self, self.cs_properties_info)

        arg.import_properties(v, self, self.properties_info)

    def export(self, arg):
        if self.flag == 1:
            arg.export_properties(None, self, self.cs_properties_info)

        arg.export_properties(None, self, self.properties_info)


#######################################################################
