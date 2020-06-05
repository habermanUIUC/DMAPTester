'''


'''


def partition_scores(data):
    num_tests = len(data["tests"])
    # assume tests are 'in order'
    # so 'bonus' questions are at the end
    total = 0
    regular = []
    bonus = []
    for c in data["tests"]:
        m = int(c["max_score"])
        if total < 100:
            total += m
            regular.append(c)
        else:
            bonus.append(c)
    return regular, bonus


def get_totals(data):
    total_possible = 0
    total_earned = 0
    total_correct = 0
    for c in data:
        m = int(c["max_score"])
        s = int(c["score"])
        total_possible += m
        total_earned += s
        if m == s:
            total_correct += 1
    return total_earned, total_possible, total_correct


def do_matplot(data, max_total=100):
    reg, bonus = partition_scores(data)

    e,p,c = get_totals(reg)
    print('regular', e,p,c, len(reg))
    pct = 0
    if p > 0:
        pct = 100 * e/p

    e,p,c = get_totals(bonus)
    print('bonus', e,p,c, len(bonus))
    pct = 0
    if p > 0:
        pct = 100 * e/p
