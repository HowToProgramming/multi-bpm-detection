def exp_smoothing(xs, alpha):
    out = [xs[0]]
    for x in xs[1:]:
        out.append(out[-1] * (1 - alpha) + x * alpha)
    return out
