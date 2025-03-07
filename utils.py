from re import match

def green_or_red(i: int | float | str) -> str:
    return ("[green]" if float(i)>0 else "[red]") + str(i)

def long_or_short_color(s: str) -> str:
    if isinstance(s, str):
        if s == "long":  return "[green]long[/]"
        if s == "short": return "[red]short[/]"
        if s.upper() in ['P', 'PUT']:  return "[red]"
        if s.upper() in ['C', 'CALL']: return "[green]"

    raise ValueError(f"Not long/short - {s!s}")

def price_color_leading_zeros(s: str) -> str:
    pass

def option_name_coloring(s: str) -> str:
    if len(s) <= 6:
        return f"[cyan]{s}"

    groups = match("([A-Z]{3,6})(\d{6})([CP])([0]{0,4})(\d{1,5})(\d{2})(\d)", s).groups()
    colors = ["[cyan]", "[yellow]", long_or_short_color(groups[2]), "[gray30]","[blue]", "[gray70]", "[gray30]"]

    return "[/]".join(color+data for color,data in zip(colors, groups))+"[/]"
