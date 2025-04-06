'''
Ngoc Dao: ndao2@u.rochester.edu
Luka Avno: lavni@u.rochester.edu
'''

import random

def cartesian_product(lists):
    '''
    To generate combination of values of nodes (eg: A = [0,1] B = [2,3] --> [(0,2),(0,3),(1,2),(1,3)])
    '''
    if not lists:
        return [()]
    rest = cartesian_product(lists[1:])
    return [(item,) + r for item in lists[0] for r in rest]   

class BayesianNetwork:
    def __init__(self):
        self.parents = {} # a dict with key as a node's name and value as list of parents
        self.domains = {} # a dict with key as a node's name and value as list of its possible values
        self.cpt = {} # a dict with key as nodes and value as its cpt

    def add_node(self, nodename, parent, cpt):
        self.parents[nodename] = parent
        self.cpt[nodename] = cpt

    def get_parents(self, nodename):
        return self.parents[nodename]

    def get_cpt(self, nodename):
        return self.cpt[nodename]




    def load_network(self, filename):
        with open(filename, 'r') as file:
            num_of_vars = int(file.readline().strip())

            for _ in range(num_of_vars):
                line = file.readline().strip().split()
                var_name = line[0]
                var_values = line[1:]

                self.domains[var_name] = var_values
                self.parents[var_name] = []
                self.cpt[var_name] = {}

            # Read blank line
            file.readline()

            num_of_cpts = int(file.readline().strip())

            for _ in range(num_of_cpts):
                line = file.readline().strip().split()
                child = line[0]
                cpt = {}

                if len(line) == 1:  # Variable has no parents
                    dist_line = file.readline().strip().split()
                    for i, value in enumerate(self.domains[child]):
                        cpt[value] = float(dist_line[i])

                    self.parents[child] = []
                    self.add_node(child, [], cpt)

                else:
                    parents = line[1:]
                    self.parents[child] = parents
                    combos = cartesian_product([self.domains[p] for p in parents])

                    for combo in combos:
                        dist_line = file.readline().strip().split()
                        value_probs = {}
                        for i, value in enumerate(self.domains[child]):
                            value_probs[value] = float(dist_line[i])
                        cpt[tuple(combo)] = value_probs

                    self.add_node(child, parents, cpt)
                file.readline() # consume blank line
            
            file.close()


    def xquery(self, query_var, evidence):    
        # For enumeration, we need an ordering of all variables.
        # Here, we assume the variables in the network were added in topological order.
        variables = list(self.domains.keys())
        
        def prob(var, value, evidence):
            """
            Probability P(var = value | parents(var))
            """
            # Get the list of parents for var.
            parents = self.parents[var]
            if not parents:
                # No parents: CPT is a simple mapping from value to probability.
                return self.cpt[var][value]
            else:
                # Create a tuple of parent's values (assumed to be in order).
                key = tuple(evidence[p] for p in parents)
                return self.cpt[var][key][value]
        
        def enumerate_all(vars_list, evidence):
            """
            Recursively compute the sum of probabilities over the assignments
            to the variables in vars_list given the current evidence.
            """
            if not vars_list:
                return 1.0
            Y = vars_list[0]
            rest = vars_list[1:]
            
            if Y in evidence:
                # Y's value is fixed in the evidence; multiply its probability factor.
                return prob(Y, evidence[Y], evidence) * enumerate_all(rest, evidence)
            else:
                total = 0.0
                # Sum over all possible values of Y.
                for y in self.domains[Y]:
                    new_evidence = evidence.copy()
                    new_evidence[Y] = y
                    total += prob(Y, y, new_evidence) * enumerate_all(rest, new_evidence)
                return total
        
        # Compute the unnormalized distribution for query_var.
        distribution = {}
        for q in self.domains[query_var]:
            new_evidence = evidence.copy()
            new_evidence[query_var] = q
            distribution[q] = enumerate_all(variables, new_evidence)
        
        # Normalize the distribution.
        total = sum(distribution.values())
        for key in distribution:
            distribution[key] /= total
        
        # Format the output: list probabilities in the same order as self.domains[query_var]
        result_str = " ".join("{:.4f}".format(distribution[val]) for val in self.domains[query_var])
        return result_str


    def rquery(self, query_var, evidence, num_samples=10000):
        """
        Compute P(query_var | evidence) using rejection sampling.
        
        query_var: a string
        evidence: dict of {var_name: value}
        num_samples: number of samples to generate
        returns: dict of {query_val: probability}
        """
        print(f"[INFO] Performing REJECTION SAMPLING for {query_var} given evidence {evidence}")
        # TODO: implement rejection sampling
        # dummy output for demonstration:
        return "{:.4f} {:.4f}".format(T, F)

    def gquery(self, query_var, evidence, num_samples=10000):
        """
        Compute P(query_var | evidence) using Gibbs sampling.
        
        query_var: a string
        evidence: dict of {var_name: value}
        num_samples: number of iterations in the Gibbs chain
        returns: dict of {query_val: probability}
        """
        print(f"[INFO] Performing GIBBS SAMPLING for {query_var} given evidence {evidence}")
        # TODO: implement Gibbs sampling
        # dummy output for demonstration:
        return "{:.4f} {:.4f}".format(T, F)


def parse_query_command(line):
    if '|' in line:
        left, right = line.split('|', 1)
        query_var = left.strip()
        evidence_str = right.strip()
    else:
        #if there is no evidence
        query_var = line.strip()
        evidence_str = ""

    evidence = {}
    if evidence_str: #if there is evidence
        assignments = evidence_str.split()
        for assign in assignments:
            var, val = assign.split('=')
            evidence[var.strip()] = val.strip()

    return query_var, evidence


def main():
    bn = BayesianNetwork()

    while True:
        line = input().strip()
        parts = line.split(maxsplit=1)
        command = parts[0].lower()

        if command == "quit":
            break

        elif command == "load":
            filename = parts[1]
            bn.load_network(filename)

        elif command in ["xquery", "rquery", "gquery"]:
            query_part = parts[1]
            query_var, evidence = parse_query_command(query_part)

            if command == "xquery":
                result = bn.xquery(query_var, evidence)
            elif command == "rquery":
                result = bn.rquery(query_var, evidence)
            else: #command == "gquery"
                result = bn.gquery(query_var, evidence)

            print(result)

if __name__ == "__main__":
    main()
