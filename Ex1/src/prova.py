def generate_all_possible_rows(rule, width):
    """ This is a bit complicated because the search space gets really large when
    there's a large nonogram grid. 
    Rule = (N0, N1, ...) consists of a number of groups
    We have to find all the combinations of spaces that fit between those groups to 
    make up a line with "width" 0/1
    i.e. [spaces0] [N0] [spaces1] [N1] [spaces2] ...  [spaces final]
    This function has to be flexible enough to deal with multiple groups of spaces, building them recursively
    such that we only ever consider rows where the total spaces and groups don't exceed the row width
    """
    total_spaces = width - sum(rule)          # total spaces in row
    seq_spaces = total_spaces - len(rule) + 2 # maximum sequential spaces
    ngroups = len(rule)                       # number of groups

    # For each sequence of spaces, there are many possible lengths
    # There may be zero or more spaces on the ends, and 1 or more spaces between groups
    space_ranges = [[0, seq_spaces+1]] + [[1, seq_spaces+1]] * (ngroups-1) + [[0, seq_spaces+1]]
    outputs = []

    # Do the generation of spaces in a function so I can do it recursively and 
    # exit early as soon as the sum of spaces is greater than the total_spaces expected
    def gen_spaces(group):
        start, end = space_ranges[group]
        for s in xrange(start, end):
            ss[group] = s
            if sum(ss) > total_spaces:
                # there's now no point in continuing with this loop
                # or any futher space_groups as we've already used too many
                # spaces. so go back one group and try again
                break
            if group == ngroups:
                # If we're looking at the final run of spaces,
                # then if we have the right number of spaces then
                # this is a valid sequence of space sizes to add to the output
                if sum(ss)==total_spaces:
                    outputs.append(ss[:])
            else:
                # If we reach here, then the number of spaces allocated so far does not 
                # exceed the possible total, consider the next group
                gen_spaces(group+1)
       
        # This set of spaces is exhausted or has failed.
        # Zero-out the count for this and following groups and return to the
        # previous group
        for ii in xrange(group, len(ss)):
            ss[ii] = 0

    # ss = array of sizes of each of the space groups
    ss = [0] * (ngroups + 1)
    gen_spaces(group=0)

    # Outputs = list( [spaces before group0, spaces after group1, spaces after group2, ... spaces after groupn] )
    # Now convert to list of 0/1s as list of possible rows
    possible_rows = []
    for ss in outputs:
        # Create the row by inter-mixing the zeros (from ss) and ones (from the rule)
        row = [0] * ss[0] # leading zeros
        for number_of_ones, number_of_zeros in zip(rule, ss[1:]):
            row += [1] * number_of_ones + [0] * number_of_zeros
        possible_rows.append(row)
    
    return possible_rows

if __name__ == "__main__":
	width = 9
	rule = [2,2,2]
	possible = generate_all_possible_rows(rule,width)
	print possible