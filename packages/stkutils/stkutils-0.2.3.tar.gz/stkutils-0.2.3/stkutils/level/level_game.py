# Module for handling level.game stalker files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax
##################################################
import math
import re

from stkutils import perl_utils
from stkutils.binary_data import pack, unpack
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, join, universal_dict_object


class level_game:
    # use strict;
    # use debug qw(fail);
    def __init__(self):
        self.points = []

    # 		my $class = shift;
    # 		my $self = universal_dict_object();
    # 		bless($self, $class);
    # 		return $self;
    # 	}
    def read(self, cf):
        while 1:
            (index, size) = cf.r_chunk_open()
            if index is None:
                break
            if index == 0:
                (self.name,) = unpack("Z*", cf.r_chunk_data())
            elif index == 1:
                while 1:
                    (index, size) = cf.r_chunk_open()
                    if index is None:
                        break
                    if index == 0:
                        if size != 4:
                            fail("point count size mismatch")
                        (self.point_count,) = unpack("V", cf.r_chunk_data())
                    elif index == 1:
                        self.read_points(cf)
                    elif index == 2:
                        self.read_links(cf)

                    cf.r_chunk_close()

            else:
                fail("unexpected index " + index)

            cf.r_chunk_close()

    def read_points(self, cf):
        while 1:
            (index, size) = cf.r_chunk_open()
            if index is None:
                break
            while 1:
                (index, size) = cf.r_chunk_open()
                if index is None:
                    break
                if index == 0:
                    if size != 4:
                        fail("point index size mismatch")
                    (point_index,) = unpack("V", cf.r_chunk_data())
                elif index == 1:
                    point = universal_dict_object()
                    point.position = [0, 0, 0]
                    (
                        point.name,
                        point.position[0],
                        point.position[1],
                        point.position[2],
                        point.flags,
                        point.level_vertex_id,
                        point.game_vertex_id,
                    ) = unpack("Z*f3VVv", cf.r_chunk_data())
                    self.points.append(point)

                cf.r_chunk_close()

            cf.r_chunk_close()

    def read_links(self, cf):
        packet = data_packet(cf.r_chunk_data())
        while 1:
            if not packet.resid() > 0:
                break
            (_from, to_count) = packet.unpack("VV", 8)
            point = self.points[_from]
            if point.links is None:
                point.links = []
            for i in range(to_count):
                link = universal_dict_object()
                (link.to, link.weight) = packet.unpack("Vf", 8)
                point.links.append(link)

    def write(self, cf):

        cf.w_chunk(0, pack("Z*", self.name))
        cf.w_chunk_open(1)
        cf.w_chunk(0, pack("V", len(self.points)))

        links_data = b""

        cf.w_chunk_open(1)
        point_id = 0
        for p in self.points:
            cf.w_chunk_open(point_id)
            cf.w_chunk(0, pack("V", point_id))
            data = pack(
                "Z*f3VVv",
                p.name,
                *p.position,
                p.flags,
                p.level_vertex_id,
                p.game_vertex_id,
            )
            cf.w_chunk(1, data)
            cf.w_chunk_close()

            if p.links:
                links_data += pack("VV", point_id, len(p.links))
                for l in p.links:
                    links_data += pack("Vf", l.to, l.weight)

            point_id += 1

        cf.w_chunk_close()

        cf.w_chunk(2, links_data)
        cf.w_chunk_close()

    def importing(self, _if, section):
        self.name = section

        points = _if.value(section, "points")
        if not points:
            fail("no points in path " + section)  # if not defined $points;
        index_by_id = universal_dict_object()
        # my $i = 0;
        for i, id in enumerate(perl_utils.split(",", points)):
            # id =~ s/^\s*|\s*$//g;

            point = universal_dict_object()
            point["name"] = _if.value(section, f"{id}:name")
            flags = _if.value(section, f"{id}:flags")
            if flags is None:
                flags = 0
            elif re.match(r"^\s*0[xX]", flags):
                flags = int(flags, base=16)

            point["flags"] = flags
            position = _if.value(section, f"{id}:position")
            point["position"] = [float(f) for f in perl_utils.split(",", position)]
            point["game_vertex_id"] = int(_if.value(section, f"{id}:game_vertex_id"))
            point["level_vertex_id"] = int(_if.value(section, f"{id}:level_vertex_id"))
            point["links0"] = _if.value(section, f"{id}:links")

            self.points.append(point)

            index_by_id[id] = i

        for p in self.points:
            if not p.links0:
                continue
            p.links = []
            for l in perl_utils.split(",", p.links0):
                rm = re.match(r"^\s*(?P<to>\w+)\s*\((?P<weight>\S+)\)\s*$", l)
                rm1 = rm.group("to")
                rm2 = rm.group("weight")
                # die if not defined $1;
                # die if not defined $2;
                link = universal_dict_object()
                link.to = index_by_id[rm1]
                link.weight = float(rm2)
                p.links.append(link)
            p.links0 = None

    def export(self, _if, id):
        fh = _if.fh

        fh.write(f"[{self.name}]\n")
        points = []

        for i, p in enumerate(self.points):
            points.append(f"p{i}")

        fh.write("points = " + join(",", points) + "\n")

        for i, p in enumerate(self.points):
            id = f"p{i}"
            fh.write(f"{id}:name = {p.name}\n")
            if p.flags != 0:
                fh.write(f"{id}:flags = %#x\n" % p.flags)
            fh.write(f"{id}:position = " + join(",", p.position) + "\n")
            fh.write(f"{id}:game_vertex_id = {p.game_vertex_id}\n")
            fh.write(f"{id}:level_vertex_id = %d\n" % p.level_vertex_id)
            if p.links:
                links = []
                for j, l in enumerate(p.links):
                    links.append(f"p{l.to}({self._format_float(l.weight)})")

                fh.write(f"{id}:links = " + join(",", links) + "\n")

            fh.write("\n")

        fh.write("\n")

    def _format_float(self, f: float) -> str:
        if math.isnan(f):
            return str(f)
        if abs(int(f) - f) < 1e-12:
            return str(int(f))
        return str(round(f, 13))

    def split_ways(self, cf, object_id):
        cf.w_chunk_open(object_id)
        cf.w_chunk_open(1)
        cf.w_chunk_data(pack("v", 0x13))
        cf.w_chunk_close()

        cf.w_chunk_open(5)
        cf.w_chunk_data(pack("Z*", self.name))
        cf.w_chunk_close()

        cf.w_chunk_open(2)
        cf.w_chunk_data(pack("v", len(self.points)))
        links_data = b""
        point_id = 0
        for p in self.points:
            data = pack("f3VZ*", *p.position, p.flags, p.name)
            cf.w_chunk_data(data)

        cf.w_chunk_close()
        cf.w_chunk_open(3)
        _id = 0
        for p in self.points:

            for l in p.links or []:
                links_data += pack("vvf", point_id, l.to, l.weight)
                _id += 1
            point_id += 1

        cf.w_chunk_data(pack("v", _id))
        cf.w_chunk_data(links_data)
        cf.w_chunk_close()
        cf.w_chunk_close()


#######################################################################
