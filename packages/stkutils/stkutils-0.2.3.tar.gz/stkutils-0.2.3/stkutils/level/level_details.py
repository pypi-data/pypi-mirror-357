# Module for handling level.details stalker files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax, fix bugs
##################################################
from stkutils import perl_utils
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, universal_dict_object


class fsd_mesh:
    # use strict;
    # 	def __init__():
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, packet):
        (
            self.shader,
            self.textures,
            self.flags,
            self.min_scale,
            self.max_scale,
            self.number_vertices,
            self.number_indices,
        ) = packet.unpack("Z*Z*VffVV")
        for i in range(self.number_vertices):
            vertex = universal_dict_object()
            vertex.position = packet.unpack("f3", 12)
            (vertex.u, vertex.v) = packet.unpack("ff", 8)
            self.vertices.append(vertex)

        self.indices = packet.unpack(f"v{self.number_indices}", 2 * self.number_indices)
        self.calculate_corners()

    def write(self, packet):

        packet.pack(
            "Z*Z*VffVV",
            self.shader,
            self.textures,
            self.flags,
            self.min_scale,
            self.max_scale,
            self.number_vertices,
            self.number_indices,
        )
        for vertex in self.vertices:
            packet.pack("f3ff", vertex.position, vertex.u, vertex.v)

        packet.pack(f"v{self.number_indices}", self.indices)

    def calculate_corners(self):
        self.min = universal_dict_object()
        self.max = universal_dict_object()
        self.min.u = 5192
        self.min.v = 5192
        self.max.u = 0
        self.max.v = 0
        for vert in self.vertices:
            self.min.u = min(vert.u, self.min.u)
            self.min.v = min(vert.v, self.min.v)
            self.max.u = max(vert.u, self.max.u)
            self.max.v = max(vert.v, self.max.v)

    def _import(self):
        print("fsd_mesh::import - not implemented")

    def export(self):
        print("fsd_mesh::export - not implemented")


#######################################
class fsd_slot:
    # use strict;
    properties_info = (
        {"name": "data", "type": "ha2"},
        {"name": "palette", "type": "u16v4"},
    )

    # def __init__():
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, a):
        a.unpack_properties(self, self.properties_info)

    def write(self, a):
        a.pack_properties(self, self.properties_info)

    def _import(self):
        print("fsd_slot::import - not implemented")

    def export(self):
        print("fsd_slot::export - not implemented")


#######################################
class level_details:
    # use strict;
    # use data_packet;
    # use chunked;
    # use debug qw(fail);

    FSD_HEADER = 0x0
    FSD_MESHES = 0x1
    FSD_SLOTS = 0x2

    def __init__(self, data):
        # my $class = shift;
        # my $self = universal_dict_object();
        self.data = data
        # $self.data = $_[0] if defined $_[0];
        self.slot_data = ""

    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, mode):
        cf = chunked(self.data, "data")
        while 1:
            (id, size) = cf.r_chunk_open()
            if id is None:
                break

            if id == self.FSD_HEADER:
                self.read_header(cf)
            elif id == self.FSD_MESHES:
                self.read_meshes(cf)
            elif id == self.FSD_SLOTS:
                self.read_slots(cf, mode)
            else:
                fail("unexpected chunk " + id)

            cf.r_chunk_close()

        cf.close()

    def write(self, mode):
        cf = chunked("", "data")
        self.write_meshes(cf)
        self.write_slots(cf, mode)
        self.write_header(cf)
        self.data = cf.data()
        cf.close()

    def read_header(self, cf):
        print("	read header...\n")
        packet = data_packet(cf.r_chunk_data())
        (
            self.version,
            self.object_count,
            self.offset_x,
            self.offset_z,
            self.size_x,
            self.size_z,
        ) = packet.unpack("VVllVV")
        if packet.resid() != 0:
            fail("data left " + packet.resid())

    def write_header(self, cf):
        packet = data_packet()
        packet.pack(
            "VVllVV",
            self.version,
            self.object_count,
            self.offset_x,
            self.offset_z,
            self.size_x,
            self.size_z,
        )
        cf.w_chunk(self.FSD_HEADER, packet.data())

    def read_meshes(self, cf):

        print("	read meshes...\n")
        while 1:
            (id, size) = cf.r_chunk_open()
            if id is None:
                break
            packet = data_packet(cf.r_chunk_data())
            mesh = fsd_mesh()
            mesh.read(packet)
            self.meshes.append(mesh)
            cf.r_chunk_close()
            if packet.resid() != 0:
                fail("data left " + packet.resid())

    def write_meshes(self, cf):

        cf.w_chunk_open(self.FSD_MESHES)
        for i, mesh in enumerate(self.meshes):
            packet = data_packet()
            mesh.write(packet)
            cf.w_chunk(i, packet.data())

        cf.w_chunk_close()

    def read_slots(self, cf, mode):
        # my () = @_;
        print("	read slots...\n")
        if mode and (mode == "full"):
            packet = data_packet(cf.r_chunk_data())
            count = perl_utils.length() / 16
            for i in range(count):
                slot = fsd_slot()
                slot.read(packet)
                self.slots.append(slot)

            if packet.resid() != 0:
                fail("data left " + packet.resid())
        else:
            self.slot_data = cf.r_chunk_data()

    def write_slots(self, cf, mode):
        cf.w_chunk_open(self.FSD_SLOTS)
        if mode and (mode == "full"):
            for i, slot in enumerate(self.slots):
                packet = data_packet()
                slot.write(packet)
                cf.w_chunk(i, packet.data())

        else:
            cf.w_chunk_data(self.slot_data)

        cf.w_chunk_close()

    def data(self):
        return self.data
