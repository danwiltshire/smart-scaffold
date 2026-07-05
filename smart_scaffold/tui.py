import pandas as pd
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static, Tree
from textual.widgets.tree import TreeNode


class _SelectFromDataFrameApp(App):
    """Two-column prompt: a selectable tree of labels (optionally grouped by
    a column) on the left, and the remaining fields of the highlighted row
    rendered on the right."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #tree {
        width: 40%;
        border: solid $accent;
    }

    #details {
        width: 60%;
        border: solid $accent;
        padding: 1 2;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]  # noqa

    def __init__(
        self,
        data: pd.DataFrame,
        label_column: str,
        detail_columns: list[str],
        group_by: str | None,
        title: str,
    ) -> None:
        super().__init__()
        self.data = data
        self.label_column = label_column
        self.detail_columns = detail_columns
        self.group_by = group_by
        self.title = title
        self.result: pd.Series | None = None
        self._first_leaf: TreeNode[int] | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal():
            tree: Tree[int] = Tree(self.title, id="tree")
            tree.show_root = False
            self._first_leaf = self._populate_tree(tree.root)
            yield tree
            yield Static(id="details")
        yield Footer()

    def _populate_tree(self, root: TreeNode[int]) -> TreeNode[int] | None:
        first_leaf: TreeNode[int] | None = None

        if self.group_by is None:
            for position, (_, row) in enumerate(self.data.iterrows()):
                leaf = root.add_leaf(str(row[self.label_column]), data=position)
                first_leaf = first_leaf or leaf
            return first_leaf

        groups: dict[object, list[int]] = {}
        for position, (_, row) in enumerate(self.data.iterrows()):
            groups.setdefault(row[self.group_by], []).append(position)

        for group_value, indexes in groups.items():
            branch = root.add(str(group_value), expand=True)
            for index in indexes:
                label = str(self.data.loc[index, self.label_column])
                leaf = branch.add_leaf(label, data=index)
                first_leaf = first_leaf or leaf

        return first_leaf

    def on_mount(self) -> None:
        tree = self.query_one("#tree", Tree)
        tree.focus()

        if self._first_leaf is not None and self._first_leaf.data is not None:
            tree.move_cursor(self._first_leaf)
            self._show_details(self._first_leaf.data)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        if event.node.data is not None:
            self._show_details(event.node.data)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        # Group nodes carry no data; selecting one just expands/collapses it.
        if event.node.data is not None:
            self.result = self.data.loc[event.node.data]
            self.exit()

    def action_cancel(self) -> None:
        self.result = None
        self.exit()

    def _show_details(self, index: int) -> None:
        row = self.data.loc[index]

        lines = [f"[b]{row[self.label_column]}[/b]"]
        for column in self.detail_columns:
            value = row[column]
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            lines.append(f"[b]{column.capitalize()}:[/b] {value}")

        self.query_one("#details", Static).update("\n\n".join(lines))


def select_from_dataframe(
    data: pd.DataFrame,
    label_column: str | None = None,
    detail_columns: list[str] | None = None,
    group_by: str | None = None,
    title: str = "Select an item",
) -> pd.Series | None:
    """Prompt the user to select a single row from `data` using an
    interactive Textual menu.

    Each row is shown by its `label_column` value; the right column shows
    the remaining fields for whichever row is currently highlighted. Arrow
    keys move the highlight, Enter selects (or expands/collapses a group),
    and Escape cancels.

    If `group_by` is given, rows are nested under collapsible group nodes
    keyed by that column's value, e.g.:

        + github-actions
            - Build Docker Image
        + local
            - Something else

    Returns the selected row as a `pandas.Series`, or `None` if the prompt
    was cancelled or `data` is empty.
    """
    if data.empty:
        return None

    data = data.reset_index(drop=True)

    if label_column is None:
        label_column = data.columns[0]

    if detail_columns is None:
        exclude = {label_column, group_by} if group_by else {label_column}
        detail_columns = [column for column in data.columns if column not in exclude]

    app = _SelectFromDataFrameApp(
        data=data,
        label_column=label_column,
        detail_columns=detail_columns,
        group_by=group_by,
        title=title,
    )
    app.run()

    return app.result
