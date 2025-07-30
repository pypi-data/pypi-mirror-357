import gradiv.pggraph as pggraph
import gradiv.polymorphism as polymorphism
from pybedtools import BedTool
import typing
import logging

def call_polymorphisms (graph_index:'pggraph.GraphIndex', id_table:bool=True, seq_table:bool=True) -> int :
    """
    First version of the "child" algorithm. Detects polymorphisms in a pangenome graph and outputs them in CSV files.
    :param graph_index: GraphIndex instance
    :param id_table : Flag to output genotype table with node IDs
    :param seq_table : Flag to output genotype table with sequences
    :return: None
    """
    logger = logging.getLogger("gradiv")
    logger.debug("Calling polymorphism functions")

    # output polymorphisms to a genotype table file
    header = "previous_node"
    for sample in graph_index.samples:
        header += f',{sample}'
    header += '\n'
    f_id = None
    f_seq = None
    if id_table:
        f_id = open(str(graph_index.id_table_path), 'w')
        f_id.write(header)
    if seq_table:
        f_seq = open(str(graph_index.seq_table_path), 'w')
        f_seq.write(header)

    # scan the graph for atomic polymorphisms
    nb_poly = 0
    for segment in graph_index.bam_file_for_parsing :
        # initialize variables
        reversed_parent = None
        is_reversed = False

        parent = pggraph.Node(bam_segment=segment, sense=1)
        parent.current_nodes = {parent.get_full_id(): parent}
        # get all nodes implicated
        links, forward_nodes, reverse_nodes, stop = parent.get_links(graph_index=graph_index)
        if stop:
            continue
        nodes_both_senses = forward_nodes.intersection(reverse_nodes)
        if parent.identifier in nodes_both_senses:
            is_reversed = True
            reversed_parent = pggraph.Node(bam_segment=segment, sense=-1)
            reversed_parent.current_nodes = parent.current_nodes
            parent.current_nodes[reversed_parent.get_full_id()] = reversed_parent

        # create nodes
        parent.create_nodes(nodes_id_set=forward_nodes, sense=1, graph_index=graph_index)
        parent.create_nodes(nodes_id_set=reverse_nodes, sense=-1, graph_index=graph_index)

        # resolve segments' samples when in both senses
        for node_id in nodes_both_senses:
            parent.current_nodes[f'+{node_id}'].samples, parent.current_nodes[f'-{node_id}'].samples = get_samples_per_sense(parent.current_nodes[f'+{node_id}'], graph_index=graph_index)

        parent.add_children(links=links)
        parent.add_parents(graph_index=graph_index)

        # call polymorphisms
        poly = call_polymorphism_from_parent(parent)
        if poly.node_per_sample:
            write_out_polymorphism(poly, parent, graph_index, f_id, f_seq)
            nb_poly += 1
        if is_reversed:
            poly = call_polymorphism_from_parent(reversed_parent)
            if poly.node_per_sample:
                write_out_polymorphism(poly, reversed_parent, graph_index, f_id, f_seq)
                nb_poly += 1
    if f_id:
         f_id.close()
    if f_seq:
         f_seq.close()
    return nb_poly


def get_samples_per_sense (node:pggraph.Node, graph_index:pggraph.GraphIndex) -> tuple[set, set] :
    """
    Associate samples to the forward or reverse segment. Used only when both segments are present.
    :param node: Node instance
    :param graph_index: GraphIndex instance
    :return: tuple of sets of samples (forward, reverse)
    """
    segment_info = (set(), set())
    for sample in node.samples:
        bed_file = BedTool(str(graph_index.bed_files[sample]))
        sample_node_presence = search_bed(node.identifier, bed_file)
        if sample_node_presence[0] :
            segment_info[0].add(sample)
        elif sample_node_presence[1] :
            segment_info[1].add(sample)
        else:
            raise ValueError("Segment not found")
    return segment_info

def search_bed (node_id:str, bed_file:BedTool) -> tuple[bool, bool] :
    """
    Browse BED files and return presence or absence of forward and reverse given segment per sample
    :param node_id: Full node ID (sign and ID)
    :param bed_file: pybedtools BED file
    :return: tuple of booleans (forward, reverse)
    """
    presence_forward = False
    presence_reverse = False
    for interval in bed_file:
        if len(interval.fields) >= 4:
            segment_id = interval.name
            if segment_id[1:] == node_id:
                if segment_id[0] == '+':
                    presence_forward = True
                else:
                    presence_reverse = True
        else:
            raise ValueError("Incorrect BED format")
        if presence_reverse and presence_forward:
            return presence_forward, presence_reverse
    return presence_forward, presence_reverse

def call_polymorphism_from_parent(parent:pggraph.Node) -> polymorphism.Polymorphism :
    """
    Call potential polymorphism right after parent node.
    :param parent: Node instance
    :return: Polymorphism instance
    """
    poly = polymorphism.Polymorphism()
    grand_children = parent.get_grand_children()
    for gc_id in grand_children:
        substitution_nodes = parent.current_nodes[gc_id].parents.intersection(parent.children)
        if len(substitution_nodes) > 1:
            poly.add_substitution(parent, substitution_nodes, parent.current_nodes[gc_id])
        if gc_id in parent.children:
            poly.add_deletion(parent, parent.current_nodes[gc_id])
            if len(substitution_nodes) == 1:
                poly.add_substitution(parent, substitution_nodes, parent.current_nodes[gc_id])
    return poly

def write_out_polymorphism(poly:polymorphism.Polymorphism, parent:pggraph.Node, graph_index:pggraph.GraphIndex, f_id:typing.TextIO=None, f_seq:typing.TextIO=None) -> None:
    """
    Write a single polymorphism to genotype tables.
    :param poly: Polymorphism instance
    :param parent: Node instance associated with the polymorphism
    :param graph_index: GraphIndex instance
    :param f_id: Flag to output genotype table with node IDs
    :param f_seq: Flag to output genotype table with sequences
    :return:  None
    """
    poly.add_undefined_values(graph_index.samples)
    if f_id:
        f_id.write(parent.get_full_id())
        for sample in graph_index.samples:
            f_id.write(f',{poly.node_per_sample[sample]}')
        f_id.write('\n')
    if f_seq:
        f_seq.write(parent.get_full_id())
        for sample in graph_index.samples:
            if poly.node_per_sample[sample] in ["?", "*"]:
                f_seq.write(f',{poly.node_per_sample[sample]}')
            else:
                f_seq.write(f',{parent.current_nodes[poly.node_per_sample[sample]].sequence}')
        f_seq.write('\n')