from _collections import defaultdict
def load_tuid2relt(content):
    tuid2relt = defaultdict(lambda: list())
    ### LOOK AT LINE IN DEBUGGER
    ### MY SYSTEM, EXAMPLE LINE FROM TERMSETS: 
    ### example: 'mediterranean\ttouch\t0.825498509999548',
    ### line from his code: '0\t117\t0.062002891680690154'
    for line in content.split('\n'):
        spl = line.split('\t')
        if len(spl) != 3:
            continue
        key = spl[0]
        value = (spl[1], float(spl[2]))
        tuid2relt[key].append(value)
    return tuid2relt