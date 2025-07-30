import pysam
from pybedtools import BedTool
import gradiv.pggraph as pggraph
import pathlib



bam_for_linear_parsing = pysam.AlignmentFile('/home/imbert/Bureau/gradiv/test_data/test_graph_GraTools_INDEX/bam_files/test_graph.bam', check_sq=False)
bam_for_query = pysam.AlignmentFile('/home/imbert/Bureau/gradiv/test_data/test_graph_GraTools_INDEX/bam_files/test_graph.bam', check_sq=False)
bam_index = pysam.IndexedReads(bam_for_query)

for segment in bam_for_linear_parsing:
    print(f'Parsing segment {segment.query_name}')
print("ok")

bam_for_linear_parsing.close()
bam_for_query.close()
