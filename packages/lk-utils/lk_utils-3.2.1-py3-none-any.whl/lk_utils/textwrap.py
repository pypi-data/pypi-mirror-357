import re
import textwrap
import typing as t


def dedent(text: str, lstrip: bool = True, join_sep: str = None) -> str:
    """
    params:
        join_sep: suggest: '-', '|' or '\\'.
    """
    out = textwrap.dedent(text).rstrip()
    if join_sep:
        if '\\' in join_sep:
            # escape for regular expression
            join_sep = join_sep.replace('\\', '\\\\')
        out = re.sub(rf' +{join_sep} *\n *', ' ', out)
    return out.lstrip() if lstrip else out


def indent(text: str, spaces: int = 4, rstrip: bool = True) -> str:
    out = textwrap.indent(text, ' ' * spaces)
    return out.rstrip() if rstrip else out


def reindent(text: str, spaces: int = 4, **kwargs) -> str:
    return indent(dedent(text, **kwargs), spaces)


def join(
    parts: t.Iterable[str],
    indent_: int = 0,
    sep: str = '\n',
    lstrip: bool = True
) -> str:
    if indent_:
        out = indent(sep.join(parts), indent_)
        if lstrip:
            return out.lstrip()
        return out
    return sep.join(parts)
