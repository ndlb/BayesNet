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


            num_of_cpts = int(file.readline().strip())

            # Read blank line
            file.readline()

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
            Sum of probabilities over the assignments to var in vars_list given current evidence.
            """
            if not vars_list:
                return 1.0
            Y = vars_list[0]
            rest = vars_list[1:]
            
            if Y in evidence:
                return prob(Y, evidence[Y], evidence) * enumerate_all(rest, evidence)
            else:
                total = 0.0
                # Sum over all possible values of Y.
                for y in self.domains[Y]:
                    new_evidence = evidence.copy()
                    new_evidence[Y] = y
                    total += prob(Y, y, new_evidence) * enumerate_all(rest, new_evidence)
                return total
        
        #unnormalized distribution for query_var.
        distribution = {}
        for q in self.domains[query_var]:
            new_evidence = evidence.copy()
            new_evidence[query_var] = q
            distribution[q] = enumerate_all(variables, new_evidence)
        
        #normalize
        total = sum(distribution.values())
        for key in distribution:
            distribution[key] /= total
        
        result_str = " ".join("{:.4f}".format(distribution[val]) for val in self.domains[query_var])
        return result_str


    def rquery(self, query_var, evidence, num_samples=100000):
        # Count accepted samples
        counts = {val: 0 for val in self.domains[query_var]}
        accepted = 0
        variables = list(self.domains.keys())

        for _ in range(num_samples):
            sample = {}

            for var in variables:
                if not self.parents[var]:
                    probs = self.cpt[var]
                else:
                    parent_vals = tuple(sample[p] for p in self.parents[var])
                    probs = self.cpt[var][parent_vals]

                # Sample based on probability distribution
                values = list(self.domains[var])
                weights = [probs[val] for val in values]
                sampled_val = random.choices(values, weights=weights)[0]
                sample[var] = sampled_val

            #Take sample matching evidence
            consistent = all(sample.get(var) == val for var, val in evidence.items())
            if consistent:
                accepted += 1
                counts[sample[query_var]] += 1


        distribution = {val: count / accepted for val, count in counts.items()} #normalize

        return " ".join("{:.4f}".format(distribution[val]) for val in self.domains[query_var])


    def gquery(self, query_var, evidence, num_samples=100000, burn_in = 1000):
        variables = list(self.domains.keys())
        non_evidence = []
        state = {}
        for var in variables:
            if var in evidence:
                state[var] = evidence[var]
            else:
                non_evidence.append(var)
                state[var] = random.choice(self.domains[var])
        
        counts = {val: 0 for val in self.domains[query_var]}

        def conditional(var, current_state):
            '''
            P(var | MB(var))
            '''
            cond_dist = {}
            for x in self.domains[var]:
                # P(var = x | parents(var))
                if not self.parents[var]:
                    p1 = self.cpt[var][x]
                else:
                    parent_vals = tuple(current_state[p] for p in self.parents[var])
                    p1 = self.cpt[var][parent_vals][x]

                # P(Y = current_state[Y] | parents(Y))
                p2 = 1.0
                for Y in variables:
                    if var in self.parents[Y]:
                        # Build parent's assignment for Y,
                        # using candidate x for var and current state for other parents.
                        parent_assignment = []
                        for p in self.parents[Y]:
                            if p == var:
                                parent_assignment.append(x)
                            else:
                                parent_assignment.append(current_state[p])
                        parent_assignment = tuple(parent_assignment)
                        p2 *= self.cpt[Y][parent_assignment][current_state[Y]]
                cond_dist[x] = p1 * p2

            #normalize
            total = sum(cond_dist.values())
            if total == 0:
                # Avoid division by zero
                norm_dist = {k: 1.0 / len(cond_dist) for k in cond_dist}
            else:
                norm_dist = {k: v / total for k, v in cond_dist.items()}
            return norm_dist
        
        # Gibbs sampling
        for i in range(num_samples):
            for var in non_evidence:
                cond_dist = conditional(var, state)
                values = list(self.domains[var])
                weights = [cond_dist[val] for val in values]
                new_val = random.choices(values, weights=weights)[0]
                state[var] = new_val

            # Record samples after burn-in
            if i >= burn_in:
                counts[state[query_var]] += 1

        #normalize
        total_samples = num_samples - burn_in
        distribution = {val: counts[val] / total_samples for val in self.domains[query_var]}

        return " ".join("{:.4f}".format(distribution[val]) for val in self.domains[query_var])


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
