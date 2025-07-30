# Module for handling level.fog_vol stalker files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax
# 	05/08/2012 - initial release
##################################################
from stkutils.data_packet import data_packet
from stkutils.perl_utils import fail, universal_dict_object


class level_fog_vol:
    # use strict;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, data=""):
        self.data = data

    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	$self.data = '';
    # 	$self.data = $_[0] if $#_ == 0;
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self):
        packet = data_packet(self.data)
        (self.version, self.num_volumes) = packet.unpack("vV", 6)
        if not (self.version == 2 or self.version == 3):
            fail("unsupported version " + self.version)
        for i in range(self.num_volumes):
            volume = universal_dict_object()
            while True:
                char = packet.raw(1)
                if char == "\n" or char == "\r":
                    break
                volume.ltx += char

            char = packet.raw(1)
            if char != "\n":
                fail("unexpected string format")
            volume.xform = packet.unpack("f16", 64)
            # 		print "\n@{$volume.xform}[0..3]\n@{$volume.xform}[4..7]\n@{$volume.xform}[8..11]\n@{$volume.xform}[12..15]\n";
            (particle_count) = packet.unpack("V", 4)
            for j in range(particle_count):
                particle = packet.unpack("f16", 64)
                # 			print "\n	@particle[0..3]\n	@particle[4..7]\n	@particle[8..11]\n	@particle[12..15]\n";
                volume.particles.append(particle)

            self.volumes.append(volume)

    def write(self):
        packet = data_packet()
        packet.pack("vV", self.version, self.num_volumes)
        for volume in self.volumes:
            volume.ltx += "\r\n"
            packet.pack("A*f16V", volume.ltx, volume.xform, len(volume.particles))
            for particle in volume.particles:
                packet.pack("f16", particle)

        self.data = packet.data()


###########################################
