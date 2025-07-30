# Module for handling level.geom/geomx stalker files
##################################################
from stkutils.chunked import chunked
from stkutils.level.level import (
    fsl_header,
    fsl_index_buffer,
    fsl_swis,
    fsl_vertex_buffer,
    level,
)


class level_geom(level):
    # use strict;
    # use base 'level::level';
    # 	sub new {
    # 		my $class = shift;
    # 		my self = universal_dict_object();
    # 		bless(self, $class);
    # 		return self;
    # 	}
    def init_data_fields(self, a):
        self.fsl_header = fsl_header()
        self.fsl_header.xrlc_version = a
        self.fsl_vertex_buffer = fsl_vertex_buffer(a)
        self.fsl_index_buffer = fsl_index_buffer(a)
        self.fsl_swis = fsl_swis(a)

    def prepare(self, level):
        self.fsl_header = level.fsl_header
        self.fsl_vertex_buffer = level.fsl_vertex_buffer
        self.fsl_index_buffer = level.fsl_index_buffer
        self.fsl_swis = level.fsl_swis

    def copy(self, copy):
        copy.fsl_vertex_buffer = self.fsl_vertex_buffer
        copy.fsl_index_buffer = self.fsl_index_buffer
        copy.fsl_swis = self.fsl_swis

    def write(self, fn):
        fh = chunked(fn, "w")
        self.fsl_header.write(fh)
        self.fsl_vertex_buffer.write(fh)
        self.fsl_index_buffer.write(fh)
        self.fsl_swis.write(fh)
        fh.close()

    def importing(self):
        self.fsl_header = fsl_header()
        self.fsl_header.import_ltx()
        self._init_data_fields(self.get_version())
        self.import_data(self.fsl_vertex_buffer)
        self.import_data(self.fsl_swis)
        self.import_data(self.fsl_index_buffer)

    def export(self):
        self.export_data(self.fsl_header, "ltx")
        self.export_data(self.fsl_vertex_buffer)
        self.export_data(self.fsl_swis)
        self.export_data(self.fsl_index_buffer)


##############################################
