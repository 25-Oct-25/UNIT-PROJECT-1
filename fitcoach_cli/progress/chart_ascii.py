def ascii_plot(values):
    if not values:
        return "No data."
    vmin, vmax = min(values), max(values)
    if vmax - vmin < 1e-9:
        vmax = vmin + 1.0
    height = 8
    lines = []
    for h in range(height, -1, -1):
        thresh = vmin + (vmax - vmin) * (h/height)
        row = []
        for v in values:
            row.append("█" if v >= thresh else " ")
        lines.append("".join(row))
    axis = "-"*len(values)
    return "\n".join(lines + [axis])
