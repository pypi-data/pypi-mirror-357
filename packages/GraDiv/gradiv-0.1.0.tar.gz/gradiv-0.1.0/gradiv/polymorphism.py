import gradiv.pggraph as pggraph

class Polymorphism:
    def __init__(self) -> None:
        """
        Class representing one polymorphism
        """
        self.node_per_sample = {}

    def __str__(self) -> str:
        return str(self.node_per_sample)

    def add_substitution(self, parent:pggraph.Node, substitution_nodes:set[pggraph.Node], grandchild:pggraph.Node) -> None:
        """
        Add alleles (as node IDs) corresponding to the samples involved in a substitution at this site. Can be used to add the node of an insertion.
        :param parent: Node before the substitution
        :param substitution_nodes: Set of node IDs involved in a substitution at this site
        :param grandchild: Node after the substitution
        :return: None
        """
        for site_node_id in substitution_nodes:
            allele_samples = pggraph.Node.shared_samples(parent, parent.current_nodes[site_node_id], grandchild)
            for sample in allele_samples:
                self.node_per_sample[sample] = parent.current_nodes[site_node_id].get_full_id()

    def add_deletion(self, parent:pggraph.Node, grandchild:pggraph.Node) -> None:
        """
        Add deletion (*) corresponding to the samples involved in a deletion at this site
        :param parent: Node before the deletion
        :param grandchild: Node after the deletion
        :return: None
        """
        excluded_nodes_id = parent.children.difference({grandchild.get_full_id()})
        excluded_samples = set()
        for en_id in excluded_nodes_id:
            excluded_samples.update(parent.current_nodes[en_id].samples)
        allele_samples = pggraph.Node.shared_samples(parent, grandchild).difference(excluded_samples)
        for sample in allele_samples:
            self.node_per_sample[sample] = "*"

    def add_undefined_values(self, all_samples:list[str]) -> None:
        """
        Add undefined values (?) to samples not involved in the polymorphism
        :param all_samples: List of all samples in the graph
        :return: None
        """
        for sample in all_samples:
            if sample not in self.node_per_sample.keys():
                self.node_per_sample[sample] = "?"
