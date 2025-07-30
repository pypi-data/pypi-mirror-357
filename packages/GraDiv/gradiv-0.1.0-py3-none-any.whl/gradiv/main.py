import click
from cloup import group, option, command, option_group
from cloup.constraints import ErrorFmt, RequireExactly
import egglib
from time import time
from gradiv.__init__ import __version__
import gradiv.algo as algo
import gradiv.pggraph as pggraph
from gradiv.functions import *

start_time = time()



# OPTION GROUPS

common_options = [
    option("-v", "--verbosity", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False), default="INFO"),
    option("-g", "--gratools-index", type=click.Path(exists=True, file_okay=False), required=True, help="Path to GraTools index"),
]

stat_options = RequireExactly(1).rephrased(
    help="""The compute command needs a list of statistics to compute. One of those options has to be provided.""",
    error=f'Exactly one statistic parameter must be provided:\n{ErrorFmt.param_list}'
)



# GRADIV COMMANDS

@group("gradiv",
       help="A tool for diversity analysis of pangenome graphs",
       no_args_is_help=True,
       invoke_without_command=True,
       context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__, "-v", "--version", message="%(prog)s, version %(version)s")
def main_command(verbosity:str="INFO"):
    pass


@command("call",
         short_help="Call polymorphisms from a GraTools pangenome graph index",
         help="Call polymorphisms from a GraTools index and output them as genotype tables in a GraDiv directory",
         no_args_is_help=True)
@option_group("call options", *common_options)
def call(gratools_index, verbosity:str="INFO"):
    """Generate genotype tables from a GraTools index and outputs them in a GraDiv directory"""
    logger = init_log(verbosity)

    gfa_index = pggraph.GraphIndex(gratools_index)
    gfa_index.make_gradiv_directory()
    gfa_index.make_bam_index_on_reads()
    gfa_index.open_bam_for_parsing()

    logger.info(f'Calling polymorphisms from "{gfa_index.gratools_directory}"')
    logger.info(f'Output directory : {gfa_index.gradiv_directory}')

    # call polymorphisms
    nb_poly = algo.call_polymorphisms(graph_index=gfa_index, id_table=True, seq_table=True)

    execution_time = time() - start_time
    logger.info(f'Found {nb_poly} polymorphisms')
    logger.info(f'Executed in {execution_time:.4f} seconds')

    gfa_index.close()


@command("compute",
         short_help="Compute statistics from a genotype table",
         help="""Compute given statistics from a GraTools index and a genotype table generated with gradiv call.
              To know which statistics ans options to provide, check out EggLib's documentation : https://www.egglib.org/.
              Analysis can be run on a specific region (query sample will be required).
              For more information, see GraDiv's documentation : https://forge.ird.fr/phim/gradiv.
              """,
         no_args_is_help=True,
         show_constraints=True)
@option_group("compute options",
              *common_options,
              stat_options(
                  option("--stat-list", type=str, required=False, help="Comma separated list of statistics to compute"),
                  option("--stat-type", type=str, required=False, help="Type of statistic to compute (can be a comma-separated list)"),
                  option("--stat-file", type=click.Path(exists=True), required=False, help="Path to file providing statistics to compute")
              ),
              option("-q", "--query", type=str, required=False, help="Sample name of query sequence to use as reference coordinates"),
              option("-c", "--chrom", type=str, required=False, help="Chromosome to use as reference coordinates"),
              option("-s", "--start-position", type=click.IntRange(min=0), required=False, help="Start position of specific region to compute statistics on"),
              option("-e", "--end-position", type=click.IntRange(min=0), required=False, help="End position of specific region to compute statistics on"),
              option("--structure", type=click.Path(exists=True), required=False, help="Path to file providing sample structure"),
              option("--max-missing", type=int, required=False, help="Ignore polymorphisms with more missing data than this threshold"),
              option("--maf", type=float, default=0, required=False, help="Ignore polymorphisms where the relative minority allele frequency is below this threshold"),
              option("--only-diallelic", is_flag=True, required=False, help="Ignore polymorphisms with more than two alleles"))
def compute(gratools_index, query: str = None, chrom: str = None, start_position: int = None, end_position: int = None,
            structure=None, stat_list: str = None, stat_type: str = None,
            stat_file=None, max_missing: int = None, maf: float = 0, only_diallelic: bool = False,
            verbosity: str = "INFO"):
    """Compute statistics from a GraDiv directory."""
    logger = init_log(verbosity)

    gfa_index = pggraph.GraphIndex(gratools_index)
    gfa_index.make_bam_index_on_reads()

    logger.info(f'Computing statistics from {gfa_index.id_table_path}')
    logger.info(f'Output file : {gfa_index.stats_path}')

    # open genotype table
    f = open(str(gfa_index.id_table_path), "r")
    f.readline()

    # configure ComputeStats
    cs = egglib.stats.ComputeStats(multi=True, multi_hits=False)
    cs.configure(maf=maf)

    # get structure
    if structure:
        structure_file = open(structure, "r")
        ingroup_dict = {}
        outgroup_dict = {}
        samples = []
        fields = structure_file.readline().strip().split(',')
        field_to_index = {}
        sample_index = 0
        for i in range(len(fields)):
            field_to_index[fields[i]] = i

        legal_fields = {'cluster', 'population', 'outgroup'}
        if fields[0] != 'sample':
            logger.error('Structure file : First field must be "sample"')
            raise ValueError('Structure file : First field must be "sample"')
        for field in fields[1:]:
            if field not in legal_fields:
                logger.error(f'Structure file : "{field}" is not a valid field')
                raise ValueError(f'Structure file : "{field}" is not a valid field')

        for line in structure_file:
            line = line.strip().split(',')
            samples.append(line[0])
            if 'outgroup' in fields and line[field_to_index['outgroup']] == "yes":
                outgroup_dict[line[0]] = [sample_index] # list of a single element as only haploidy is supported
            else:
                if 'cluster' not in fields:
                    cluster = None
                else:
                    cluster = line[field_to_index['cluster']]
                if cluster not in ingroup_dict.keys():
                    ingroup_dict[cluster] = {}
                if line[field_to_index['population']] not in ingroup_dict[cluster].keys():
                    ingroup_dict[cluster][line[field_to_index['population']]] = {}
                ingroup_dict[cluster][line[field_to_index['population']]][line[0]] = [sample_index] # list of a single element as only haploidy is supported
            sample_index += 1

        # check if all samples are included
        samples.sort()
        if samples != gfa_index.samples:
            logging.error('Structure file : incorrect sample names or missing samples')
            raise ValueError('Structure file : incorrect sample names or missing samples')

        struct = egglib.Structure()
        struct.from_dict(ingroup_dict, outgroup=outgroup_dict)
        cs.configure(struct=struct)

    # passing statistics to compute
    if stat_list :
        cs.add_stats(*stat_list.split(","))
    elif stat_type :
        cs.add_stats(*[f"+{item}" for item in stat_type.split(",")])
    elif stat_file :
        open_stat_file = open(str(stat_file), "r")
        stat_list_from_file = open_stat_file.readline().strip().split(",")
        cs.add_stats(*stat_list_from_file)
        open_stat_file.close()
    #TODO: add debug : computed stats

    by_position = False
    if query and chrom:
        by_position = True
        logger.debug('Computing statistics by position')
    else:
        if query or chrom or start_position or end_position:
            logger.error('Both query and chrom options are needed to compute statistics by region.')
            raise ValueError('Both query and chrom options are needed to compute statistics by region.')

    # compute stats
    for line in f:
        anchor_node = line.rstrip().split(',')[0]
        allele_position = None
        if by_position:
            allele_position = gfa_index.get_site_position(node_id=anchor_node, query=query, chrom=chrom)
            if allele_position == -1:
                continue
            if start_position and end_position and (allele_position < start_position or allele_position > end_position):
                continue
        split_line = line.rstrip().split(',')[1:]
        sequences = []
        for part in split_line:
            if part not in ["?", "*"] :
                segment = gfa_index.query_segment(part[1:])
                if part[0] == '+' :
                    sequences.append(segment.query_sequence)
                else:
                    sequences.append(pggraph.Node.reverse_complement(segment.query_sequence))
            else :
                sequences.append(part)
        alleles = set(sequences) #TODO: get polymorphism type from it (filter on type/length)
        alleles.discard("?")
        alph = egglib.Alphabet("string", list(alleles), ["?"])
        site = egglib.site_from_list(sequences, alph)
        if by_position:
            site.position = allele_position
        # filter out polymorphisms
        ignore_site = False
        if max_missing is not None and site.num_missing > max_missing:
            ignore_site=True
        if only_diallelic and alph.num_exploitable > 2 :
            ignore_site=True
        if not ignore_site:
            cs.process_site(site)
    logger.debug('Computing all statistics')
    stats = cs.results()
    logger.debug('Statistics computed')

    # outputs stats in CSV file
    stat_names = []
    for stat_name in stats.keys():
        stat_names.append(stat_name)

    canon_stat_order = [key for grp in ('site', 'unphased', 'phased', 'allelesize') for key in cs.stats_group(grp)]
    stat_names.sort(key=canon_stat_order.index)

    f_stats = open(str(gfa_index.stats_path), 'w')
    f_stats.write("stat_name,value\n")
    for stat_name in stat_names:
        f_stats.write(f'{stat_name},{format_stat_output(stats[stat_name])}\n')
    f_stats.close()

    execution_time = time() - start_time
    logger.info(f'Executed in {execution_time:.4f} seconds')


# add commands to main
main_command.add_command(call)
main_command.add_command(compute)