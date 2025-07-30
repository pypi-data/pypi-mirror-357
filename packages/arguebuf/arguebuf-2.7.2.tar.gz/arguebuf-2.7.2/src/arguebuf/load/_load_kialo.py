import re
import typing as t

from arguebuf.model import Graph, utils
from arguebuf.model.node import AtomNode, Attack, Rephrase, Support

from ._config import Config, DefaultConfig

__all__ = ("load_kialo",)


def load_kialo(
    obj: t.TextIO,
    name: str | None = None,
    config: Config = DefaultConfig,
) -> Graph:
    if name_match := re.search(r"Discussion Title: (.*)", obj.readline()):
        name = name_match[1]

    # After the title, an empty line should follow
    assert obj.readline().strip() == ""

    g = config.GraphClass(name)

    # Example: 1.1. Pro: Gold is better than silver.
    # Pattern: {ID}.{ID}. {STANCE (OPTIONAL)}: {TEXT}
    pattern = re.compile(r"^(1\.(?:\d+\.)+) (?:(Con|Pro): )?(.*)")
    current_line = obj.readline()
    next_line = obj.readline()

    mc_match = re.search(r"^((?:\d+\.)+) (.*)", current_line)

    if not mc_match:
        raise ValueError("The major claim is not present in the third line!")

    mc_id = mc_match[1]
    mc_text = mc_match[2]

    # See in the following while loop for explanation of this block
    while next_line and not pattern.search(next_line):
        mc_text = f"{mc_text}\n{next_line.strip()}"
        next_line = obj.readline()

    mc = _kialo_atom_node(mc_id, mc_text, config.nlp, config.AtomNodeClass)
    g.add_node(mc)
    g.major_claim = mc

    current_line = next_line
    next_line = obj.readline()

    while current_line:
        if current_match := pattern.search(current_line):
            source_id = current_match[1]
            source_id_parts = source_id[:-1].split(".")
            # level = len(source_id_parts)
            stance = current_match[2]
            text = current_match[3]

            # The text of a node is allowed to span multiple lines.
            # Thus, we need to look ahead to concatenate the complete text.
            # As long as the pattern is not found in the next line,
            # we assume that the text belongs to the previous statement.
            while next_line and not pattern.search(next_line):
                text = f"{text}\n{next_line.strip()}"
                next_line = obj.readline()

            assert source_id
            assert text

            if id_ref_match := re.search(r"^-> See ((?:\d+\.)+)", text):
                id_ref = id_ref_match[1]
                source = g.atom_nodes[id_ref]
            else:
                source = _kialo_atom_node(
                    source_id, text, config.nlp, config.AtomNodeClass
                )
                g.add_node(source)

            if stance:
                stance = stance.lower()
                scheme = config.SchemeNodeClass(
                    Attack.DEFAULT if stance == "con" else Support.DEFAULT,
                    id=f"{source_id}scheme",
                )
            else:
                scheme = config.SchemeNodeClass(
                    Rephrase.DEFAULT, id=f"{source_id}scheme"
                )

            target_id = ".".join(source_id_parts[:-1] + [""])
            target = g.atom_nodes[target_id]

            g.add_node(scheme)
            g.add_edge(config.EdgeClass(source, scheme, id=f"{source.id}->{scheme.id}"))
            g.add_edge(config.EdgeClass(scheme, target, id=f"{scheme.id}->{target.id}"))

            current_line = next_line
            next_line = obj.readline()

    return g


def _kialo_atom_node(
    id: str,
    text: str,
    nlp: t.Callable[[str], t.Any] | None,
    atom_class: type[AtomNode],
) -> AtomNode:
    # Remove backslashes before parentheses/brackets
    text = re.sub(r"\\([\[\]\(\)])", r"\1", text)

    # Remove markdown links
    text = re.sub(
        r"\[(.*?)\]\(.*?\)",
        r"\1",
        text,
    )

    # Apply user-provided nlp function
    text = utils.parse(text, nlp)

    return atom_class(text, id=id)
