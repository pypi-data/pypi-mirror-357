import pysam
import sqlite3
from pathlib import Path
import shutil
from pybedtools import BedTool

d_sens = {1:'+', -1:'-', '+':1, '-':-1} #used to convert segment sense from numeric to symbol and vice versa

class Node:
    """
    Node class representing a segment in a pangenome graph.

    Attributes:
        identifier: segment identifier (without sense)
        sense: sense of the segment (1: forward, -1: reverse)
        sequence: sequence of the segment
        samples: set of samples using the segment (only genome)
        complete_samples: set of samples using the segment (genome, chromosome and haplotype)
        current_nodes: dictionary storaging all nodes used: parent(s), children and grandchildren (only used in parent node)
        children: set of children nodes' full IDs (+/-ID)
        parents: set of parents nodes' full IDs (+/-ID)
    """
    def __init__(self, bam_segment:pysam.libcalignedsegment.AlignedSegment, sense:int) -> None:
        """
        Initialize node
        :param bam_segment: pysam BAM aligned segment from a GraTools index
        :param graph_index: GraphIndex instance
        :param sense: Sense of the segment: 1/-1
        """
        self.identifier = bam_segment.query_name
        self.sense = sense
        if sense == -1:
            self.sequence = Node.reverse_complement(bam_segment.query_sequence)
        else :
            self.sequence = bam_segment.query_sequence
        self.samples = None
        self.add_samples(bam_segment)
        self.complete_samples = None
        self.add_complete_samples(bam_segment)
        self.current_nodes = None # only used for parent node
        self.children = set()
        self.parents = set()

    def __str__(self) -> str:
        return f'Node {self.get_full_id()} : {self.sequence}. Parents: {self.parents}. Children: {self.children}. Samples: {self.samples}.'

    def __repr__(self) -> str:
        return f'Node {self.get_full_id()}'

    def add_samples (self, bam_segment) -> None:
        """
        Add samples supported by the node (only account sample name)
        :param bam_segment: BAM segment
        :return: None
        """
        txt_samples = bam_segment.get_tag('SW')
        samples_set = set(elm.split(";")[0] for elm in txt_samples.split(','))
        self.samples = samples_set

    def add_complete_samples (self, bam_segment) -> None:
        """
        Add samples supported by the node (account sample name, chromosome and haplotype)
        :param bam_segment: BAM segment
        :return:None
        """
        txt_samples = bam_segment.get_tag('SW')
        samples = txt_samples.split(',')
        samples_set = set(tuple(s.split(';')) for s in samples)
        self.complete_samples = samples_set

    def add_children(self, links:dict) -> None:
        """
        Add children nodes' full IDs to children attribute
        :param links: Dictionnary of current parent->child links
        :return: None
        """
        for parent_node in self.current_nodes.keys():
            if parent_node in links.keys():
                children = links[parent_node]
                for child in children:
                    if self.current_nodes[child].samples.intersection(self.current_nodes[parent_node].samples):
                        if not self.current_nodes[parent_node].children:
                            self.current_nodes[parent_node].children = {child}
                        else:
                            self.current_nodes[parent_node].children.add(child)

    def add_parents(self, graph_index:'GraphIndex') -> None:
        """
        Add parents nodes' full IDs to parents attribute
        :param graph_index: GraphIndex instance
        :return: None
        """
        for grandchild in self.get_grand_children():
            self.current_nodes[grandchild].parents = set()
            for link in graph_index.query_links(grandchild[1:]):
                if link[3] == grandchild[1:]:
                    if link[0] == grandchild[1:]:
                        raise ValueError('Cycle detected')
                    else:
                        self.current_nodes[grandchild].parents.add(f'{d_sens[link[1]]}{link[0]}')


    def get_links(self, graph_index:'GraphIndex') -> tuple:
        """
        Get all current parent->child links as a dictionary with IDs as keys and set of IDs as items.
        Returns 4 variables : links dictionary, forward nodes as a set, reverse nodes as a set and boolean (True if not enough children to find a bubble).
        :param graph_index: GraphIndex instance
        :return: tuple of a links dictionary, forward set and reverse set
        """
        links = {}
        children = set()
        forward_nodes = set()
        reverse_nodes = set()
        n_children_forward = 0
        n_children_reverse = 0
        # parse parent's children
        for link in graph_index.query_links(self.identifier):
            if link[0] == self.identifier: # only take links where the node is parent
                parent_id = d_sens[link[1]] + link[0]
                if link[3] == self.identifier:
                    raise ValueError('Cycle detected')
                else:
                    if link[1] == 1:
                        forward_nodes.add(link[0])
                        n_children_forward += 1
                    else:
                        reverse_nodes.add(link[0])
                        n_children_reverse += 1
                    child_id = d_sens[link[4]] + link[3]
                    children.add(child_id)
                    if link[4] == 1:
                        forward_nodes.add(link[3])
                    else:
                        reverse_nodes.add(link[3])
                    if parent_id not in links.keys():
                        links[parent_id] = {child_id}
                    else :
                        links[parent_id].add(child_id)
        if n_children_forward + n_children_reverse < 2 :
            return links, forward_nodes, reverse_nodes, True
        # parse children's children
        for child in children:
            for link in graph_index.query_links(child[1:]):
                if link[0] == child[1:]: # only take links where the node is parent
                    if link[3] == child[1:]:
                        raise ValueError('Cycle detected')
                    else:
                        grand_child_id = d_sens[link[4]] + link[3]
                        if link[4] == 1:
                            forward_nodes.add(link[3])
                        else:
                            reverse_nodes.add(link[3])
                        if child not in links.keys():
                            links[child] = {grand_child_id}
                        else :
                            links[child].add(grand_child_id)
        return links, forward_nodes, reverse_nodes, False

    def create_nodes(self, nodes_id_set:set[str], sense:int, graph_index:'GraphIndex') -> None:
        """
        Create nodes and store them in a dictionary (current_nodes attribute)
        :param nodes_id_set: Set of node IDs (without sense)
        :param sense: Sense + or -
        :param graph_index: GraphIndex instance
        :return: None
        """
        for node_id in nodes_id_set:
            full_id = str(d_sens[sense]) + node_id
            if full_id not in self.current_nodes.keys():
                segment = graph_index.query_segment(segment_id=node_id)
                self.current_nodes[full_id] = Node(bam_segment=segment, sense=sense)

    def get_grand_children(self) -> set[str] :
        """
        :return: Dictionary of all grand children nodes
        """
        grand_children = set()
        for child_id in self.children:
            for grandchild_id in self.current_nodes[child_id].children:
                grand_children.add(grandchild_id)
        return grand_children

    def get_full_id(self):
        """
        :return: Full ID of the node (+/-ID)
        """
        return f'{d_sens[self.sense]}{self.identifier}'

    def display_filiation(self):
        """
        Display the node's filiation tree (from parent to granchildren)
        """
        print(self.get_full_id())
        for child in self.children:
            print('\t|_', child)
            for grandchild in self.current_nodes[child].children:
                print('\t\t|_', grandchild)

    @classmethod
    def reverse_complement(cls, sequence:str) -> str:
        """
        :param sequence: DNA sequence
        :return: Reverse complement of the sequence
        """
        rc_seq = ''
        complements = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
        for c in reversed(sequence):
            if c in complements.keys():
                rc_seq += complements[c]
            else:
                rc_seq += c
        return rc_seq

    @classmethod
    def shared_samples(cls, node1:'Node', *args:'Node') -> set['Node']:
        """
        Get shared samples between two nodes or more
        :param node1: Node
        :param args: Node(s)
        :return: Set of samples
        """
        #TODO: base off genome + chr + haplotype
        intersection = node1.samples.copy()
        for node in args:
            intersection.intersection_update(node.samples)
        return intersection



class GraphIndex :
    """
    Class representing a GraTools index and GraDiv genotype tables

    Attributes:
        gratools_directory: Path to GraTools index directory
        pg_name: Pangenome graph name
        samples: list of samples (used for outputs)
        bam_path: path to BAM file
        bam_file: open pysam alignment file
        bam_index: index of BAM file on segment ID
        bam_file_for_parsing: second open pysam alignment file for linear parsing
        bed_directory_path: path to BED files directory
        bed_files: dictionary of BED files path with sample name as key
        db_path: path to links database
        conn: sqlite3 connector to the link database
        gradiv_directory: output directory path
        id_table_path: path to genotype table with node IDs
        seq_table_path: path to genotype table with node sequences
        stats_path: path to statistics file output
    """
    def __init__(self, gratools_directory:str):
        """
        Initialize a graph index
        :param gratools_directory: Path to GraTools index directory
        """
        self.gratools_directory = Path(gratools_directory).resolve()
        self.pg_name = self.gratools_directory.name.split('_GraTools_INDEX')[0]
        self.samples = [] #TODO: add chromosome ?

        # BAM related attributes
        self.bam_path = self.gratools_directory / f'bam_files/{self.pg_name}.bam'
        self.bam_file = pysam.AlignmentFile(str(self.bam_path), 'rb', check_sq=False) # intended for query
        self.bam_index = None
        self.bam_file_for_parsing = None

        # BED related attributes
        self.bed_directory_path = self.gratools_directory / 'bed_files'
        self.bed_files = {}
        for file in self.bed_directory_path.iterdir():
            if file.suffix == '.bed':
                self.bed_files[file.stem] = file
                self.samples.append(file.stem)
        self.samples = sorted(self.samples)

        # Links DB related attributes
        self.db_path = self.gratools_directory / f'links_{self.pg_name}.db'
        self.conn = sqlite3.connect(str(self.db_path))

        # Genotype tables related attributes
        self.gradiv_directory = self.gratools_directory.parent / f'{self.pg_name}_gradiv'
        self.id_table_path = self.gradiv_directory / f'{self.pg_name}_id_table.csv'
        self.seq_table_path = self.gradiv_directory / f'{self.pg_name}_seq_table.csv'
        self.stats_path = self.gradiv_directory / f'{self.pg_name}_stats.csv'

    def make_bam_index_on_reads(self) -> None:
        """
        Index BAM file on segment ID
        :return: None
        """
        self.bam_index = pysam.IndexedReads(self.bam_file)
        self.bam_index.build()

    def query_segment (self, segment_id:str) -> pysam.AlignedSegment|None:
        """
        Query segment from BAM file on ID
        :param segment_id: Segment ID
        :return: BAM segment or None
        """
        read_iterator = self.bam_index.find(segment_id)
        for read in read_iterator:
            return read
        return None

    def open_bam_for_parsing(self) -> None:
        """
        Make temporary BAM file to parallelize BAM parsing and node query
        :return: None
        """
        self.bam_file_for_parsing = pysam.AlignmentFile(str(self.bam_path), 'rb', check_sq=False)

    def close(self):
        """
        Closes connections, files and removes temporary file
        :return:
        """
        self.conn.close()
        self.bam_file.close()
        if self.bam_file_for_parsing :
            self.bam_file_for_parsing.close()

    def query_links(self, segment_id: str) -> list:
        """
        Fetch links from or to the segment
        :param segment_id: query segment id
        :return: list of rows
        """
        cursor = self.conn.cursor()
        cursor.execute('''
                    SELECT * FROM links WHERE seg_id_1 = ? OR seg_id_2 = ?
                ''', (segment_id, segment_id))
        return cursor.fetchall()

    def query_all_links(self) -> list:
        """
        Fetch all links from the link database (intended for debug)
        :return: list of rows
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM links')
        return cursor.fetchall()

    def make_gradiv_directory(self) -> None:
        """
        Make gradiv directory if it does not exist
        :return: None
        """
        self.gradiv_directory.mkdir(parents=True, exist_ok=True)

    def get_site_position(self, node_id:str, query:str, chrom:str) -> int:
        """
        Get polymorphism position
        :param node_id: ID (with sense) of node before the polymorphism
        :param query: Query to use as a coordinate reference
        :param chrom: Chromosome
        :return: Position of
        """
        bed_file = BedTool(str(self.bed_files[query]))
        for interval in bed_file :
            if interval.name == node_id and interval.chrom == chrom:
                return interval.stop
        return -1