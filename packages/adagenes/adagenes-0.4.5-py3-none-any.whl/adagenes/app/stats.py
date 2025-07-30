

def generate_stats(variants):
    stats = {}
    stats["mtype"] = []

    for var in variants:
        print(var)

        # mtype
        if "mtype" in var:
            stats["mtype"].append({"type": var["mtype"]})
        else:
            pass

    return stats