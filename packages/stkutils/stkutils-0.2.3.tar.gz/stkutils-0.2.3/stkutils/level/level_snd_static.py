# Module for handling level.snd_static stalker files
# Update history:
# 	10/11/2013 - fixed handling of old build files
# 	27/08/2012 - initial release
##################################################
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import fail, universal_dict_object


class level_snd_static:
    # use strict;
    # use data_packet;
    # use ini_file;
    # use debug qw(fail);
    FL_OLD = 0x1

    def __init__(self):
        # my $class = shift;
        # my self = universal_dict_object();
        self.flag = 0
        self.config = universal_dict_object()

    # 	bless self, $class;
    # 	return self;
    # }
    def set_flag(self, arg):
        self.flag |= arg

    def get_flag(self):
        return self.flag

    def get_src(self):
        return self.config.src

    def mode(self):
        return self.config.mode

    def old(self):
        if self.flag & self.FL_OLD == self.FL_OLD:
            return 1

        return 0

    def read(self, CDH):
        expected_index = 0
        while 1:
            (index, size) = CDH.r_chunk_open()
            if index is None:
                break
            if expected_index != index:
                fail("chunk " + index + " have unproper index")

            if not self.old():
                (in_index, in_size) = CDH.r_chunk_open()
                if in_index != 0:
                    fail("cant find chunk 0")

            packet = data_packet(CDH.r_chunk_data())
            snd_static = snd_static()
            snd_static.flag = self.get_flag()
            snd_static.read(packet)
            if packet.resid() != 0:
                fail("there is some data left in packet: " + packet.resid())
            self.snd_statics.append(snd_static)
            expected_index += 1

            if not self.old():
                CDH.r_chunk_close()

            CDH.r_chunk_close()

    def write(self, CDH):

        for index, snd_static in enumerate(self.snd_statics):
            packet = data_packet()
            snd_static.write(packet)
            CDH.w_chunk_open(index)
            if not self.old():
                CDH.w_chunk(0, packet.data())
            else:
                CDH.w_chunk_data(packet.data())

            CDH.w_chunk_close()

    def my_import(self, arg):
        IFH = ini_file(arg, "r")  # or die;
        for section in IFH.sections_list:
            snd_static = snd_static()
            snd_static.flag = self.get_flag()
            snd_static._import(IFH, section)
            self.snd_statics.append(snd_static)

        IFH.close()

    def export(self, arg):
        IFH = ini_file(arg, "w")  # or die;
        RFH = IFH.fh

        for index, snd_static in enumerate(self.snd_statics):
            RFH.write(f"[{index}]\n")
            snd_static.export(IFH, f"{index}")
            RFH.write("\n")

        IFH.close()


#######################################################################
class snd_static:
    # use strict;
    FL_OLD = 0x1
    first_properties_info = (
        {"name": "sound_name", "type": "sz"},
        {"name": "position", "type": "f32v3"},
        {"name": "volume", "type": "f32"},
        {"name": "frequency", "type": "f32"},
    )
    second_properties_info = (
        {"name": "active_time", "type": "u32v2"},
        {"name": "play_time", "type": "u32v2"},
        {"name": "pause_time", "type": "u32v2"},
    )
    third_properties_info = (
        {"name": "min_dist", "type": "f32"},
        {"name": "max_dist", "type": "f32"},
    )

    def __init__(self):
        # my $class = shift;
        # my self = universal_dict_object();
        self.type = 0

    # 	bless self, $class;
    # 	return self;
    # }
    def read(self, arg):
        arg.unpack_properties(self, self.first_properties_info)
        if self.old():
            arg.unpack_properties(self, self.third_properties_info)
        else:
            arg.unpack_properties(self, self.second_properties_info)

    def write(self, arg):
        arg.pack_properties(self, self.first_properties_info)
        if self.old():
            arg.pack_properties(self, self.third_properties_info)
        else:
            arg.pack_properties(self, self.second_properties_info)

    def _import(self, arg, arg2):
        arg.import_properties(arg2, self, self.first_properties_info)
        if self.old():
            arg.import_properties(arg2, self, self.third_properties_info)
        else:
            arg.import_properties(arg2, self, self.second_properties_info)

    def export(self, arg):
        arg.export_properties(None, self, self.first_properties_info)
        if self.old():
            arg.export_properties(None, self, self.third_properties_info)
        else:
            arg.export_properties(None, self, self.second_properties_info)

    def old(self):
        if self.flag & self.FL_OLD == self.FL_OLD:
            return 1

        return 0


#######################################################################
