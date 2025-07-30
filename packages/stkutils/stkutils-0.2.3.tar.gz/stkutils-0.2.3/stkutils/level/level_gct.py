# Module for handling level.gct stalker files
# Update history:
# 	26/08/2012 - fix code for new fail() syntax
##################################################
from stkutils import perl_utils
from stkutils.binary_data import pack, unpack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, length, substr


class level_gct:
    # use strict;
    # use chunked;
    # use data_packet;
    # use debug qw(fail);
    CT_HEADER = 0x0
    CT_DATA = 0x1

    def __init__(self, data=""):
        # my $class = shift;
        # my $self = universal_dict_object();
        # $self.data = '';
        self.data = data
        self.cell_data = ""
        self.header = ct_header()

    # 	bless $self, $class;
    # 	return $self;
    # }
    def set_version(self, v):
        self.header.version = v

    def get_data(self):
        return self.data

    def read(self, mode):
        (switch,) = unpack("V", substr(self.data, 0, 4))
        if switch == 0:  # soc and pre-soc old format
            dh = chunked(self.data, "data")
            if dh.find_chunk(self.CT_HEADER):
                self.header.read(data_packet(dh.r_chunk_data()))
                dh.close_found_chunk()
            else:
                fail("cannot find header chunk")

            if dh.find_chunk(self.CT_DATA):
                self.cell_data = dh.r_chunk_data()
                if mode is not None and mode == "full":
                    self._read_cells()

                dh.close_found_chunk()
            else:
                fail("cannot find data chunk")

            dh.close()
        else:  # 3120 and next
            header_data = substr(self.data, 4, 44)
            self.header.read(data_packet(header_data))
            self.cell_data = substr(self.data, 48)
            if mode is not None and mode == "full":
                self._read_cells()

    def _read_cells(self):
        packet = data_packet(self.cell_data)
        if perl_utils.length() % 6 != 0:
            fail("bad CT_DATA chunk")
        for i in range(self.header.cell_count):
            cell = ct_cell()
            cell.read(packet)
            self.cells.append(cell)

    def write(self, mode):
        packet = data_packet()
        self.header.write(packet)
        if mode is not None and mode == "full":
            self._write_cells()

        if self.header.version < 9:  # soc and pre-soc old format
            dh = chunked("", "data")
            dh.w_chunk(self.CT_HEADER, packet.data())
            dh.w_chunk(self.CT_DATA, self.cell_data)
            self.data = dh.data()
            dh.close()
        else:  # 3120 and next
            data = packet.data()[self.cell_data]
            size = length(data) + 4
            data = pack("V", size.data)
            self.data = data

    def _write_cells(self):
        packet = data_packet()
        for cell in self.cells:
            cell.write(packet)

        self.cell_data = packet.data()


######################################################
class ct_header:
    header = (
        {"name": "version", "type": "u32"},
        {"name": "cell_count", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "level_guid", "type": "guid"},
        {"name": "game_guid", "type": "guid"},
    )

    # def new {
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless($self, $class);
    # 	return $self;
    # }
    def read(self, arg):
        arg.unpack_properties(self, self.header[0:2])
        if self.version > 7:
            arg.unpack_properties(self, self.header[3:4])

    def write(self, arg):
        arg.pack_properties(self, self.header[0:2])
        if self.version > 7:
            arg.pack_properties(self, self.header[3:4])

    def export(self, fh):

        fh.write(f"version = {self.version}\n")
        fh.write(f"cell_count = {self.cell_count}\n")
        fh.write(f"vertex_count = {self.vertex_count}\n")
        if self.version > 7:
            fh.write(f"level_guid = {self.level_guid}\n")
        if self.version > 7:
            fh.write(f"game_guid = {self.game_guid}\n")
        fh.write("\n")

    def _import(self, fh):

        self.version = fh.value("header", "version")
        self.cell_count = fh.value("header", "cell_count")
        self.vertex_count = fh.value("header", "vertex_count")
        self.level_guid = fh.value("header", "level_guid")
        self.game_guid = fh.value("header", "game_guid")


######################################################
class ct_cell:
    cell = (
        {"name": "game_vertex_id", "type": "u16"},
        {"name": "distance", "type": "f32"},
    )

    # def new {
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless($self, $class);
    # 	return $self;
    # }
    def read(self, arg):
        arg.unpack_properties(self, self.cell)

    def write(self, arg):
        arg.pack_properties(self, self.cell)

    def export(self, fh):
        fh.write(f"game_vertex_id = {self.game_vertex_id}\n")
        fh.write(f"distance = {self.distance}\n")
        fh.write("\n")

    def _import(self, fh, i):
        self.game_vertex_id = fh.value(i, "game_vertex_id")
        self.distance = fh.value(i, "distance")


######################################################
