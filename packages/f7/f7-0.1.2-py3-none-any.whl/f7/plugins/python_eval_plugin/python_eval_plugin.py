# plugins/python_eval_plugin.py
import builtins
import contextlib
import io
import rlcompleter
import sys

from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QCompleter, QLabel, QTextEdit

from ...utils import WORD_BOUNDARY_RE, dotdict
from ..base_plugin import PluginInterface
from .cyber import ctx as cyber_ctx
from .python_utils import PyUtils, auto_parse, redirect_stdin, repr_as_json, smart_eval
from .static_globals import static_globals


class PythonEvalPlugin(PluginInterface):
    NAME = "Python Evaluator"
    PREFIX = None
    SUFFIX = None
    IS_DEFAULT = True  # This handles input if no other plugin matches
    PRIORITY = 90  # Lower than AI prefix plugin

    HAS_AUTOCOMPLETE = True  # Signal that this plugin provides completions

    def __init__(self, api, settings):
        super().__init__(api, settings)
        self.eval_context = self._create_context()

    def get_status_message(self) -> str:
        return "🐍 Python mode"

    def _evaluate(
        self, command: str, selected_text: str
    ) -> tuple[str | None, str | None]:
        """Internal helper to evaluate, returning result and error."""

        if not command:
            return None, None  # No command, no result or error

        try:
            self._update_context(selected_text)

            combined_buf = io.StringIO()
            fake_stdin = io.StringIO(selected_text)
            # security:ignore. this eval command is the intended use of this plugin.
            with redirect_stdin(fake_stdin), contextlib.redirect_stdout(
                combined_buf
            ), contextlib.redirect_stderr(combined_buf):

                result = smart_eval(command, self.eval_context)

            output = combined_buf.getvalue()
            if result is None and output:
                result_str = output
            else:
                result_str = repr_as_json(result, selected_text)
                if output:
                    result_str = output + "\n" + result_str
            return result_str, None
        except Exception as e:
            return None, f"🚨 Error: {str(e)}"

    def update_preview(self, command: str, selected_text: str, manual: bool) -> None:
        """
        Update the preview area with the evaluation result or error.
        Called on input change (if not manual) or on Ctrl+Enter (manual).
        """
        # Only run preview if manually triggered or if there's a command
        if not manual and not command.strip():
            self.api.update_preview_content(
                ""
            )  # Clear preview if no command and not manual
            self.api.reset_status()  # Reset to default python status
            return

        result_str, error_str = self._evaluate(command, selected_text)

        if error_str:
            self.api.update_preview_content(error_str)
            self.api.set_status("🐍 Evaluation Error", self.NAME)
        elif (
            result_str is not None
        ):  # result_str can be empty string for successful eval with no output
            self.api.update_preview_content(result_str)
            if manual:
                self.api.set_status("🐍 Preview updated (manual)", self.NAME)
            else:
                self.api.set_status(
                    "🐍 Python Ready", self.NAME
                )  # Or a more dynamic status
        else:  # No result and no error (e.g., empty command was evaluated)
            self.api.update_preview_content("")  # Clear preview
            self.api.reset_status()

    def execute(self, command: str, selected_text: str) -> str | None:
        result_str, error_str = self._evaluate(command, selected_text)

        if error_str:
            print(f"Execution Error: {error_str}", file=sys.stderr)
            self.api.set_status(f"💥 Error (not copied)")
            return None  # Indicate error or no clipboard action needed
        elif result_str is not None:
            return result_str  # Return the result string to copy
        else:
            return None  # No command entered

    def _create_context(self):
        ctx = dotdict(builtins.__dict__)

        ctx.update(static_globals)
        ctx.update(cyber_ctx)
        return ctx

    def _update_context(self, text: str):
        ctx = dotdict()
        ctx.raw = ctx.text = ctx.s = ctx.txt = text
        ctx.lines = text.split("\n")
        ctx.words = text.split()
        ctx.chars = ctx.characters = list(text)

        str_methods = [
            "count",
            "split",
            "replace",
            "lower",
            "upper",
            "title",
            "center",
            "format",
        ]
        for method in str_methods:
            ctx[method] = getattr(text, method)
        # shortcuts/logcuts
        ctx.split_on = ctx.split
        # utility functions
        utils = PyUtils(text)
        ctx.fork = ctx.lines_map = utils.lines_map
        ctx.grep = utils.grep
        ctx.sub = utils.sub
        ctx.auto_parse = auto_parse
        # auto parse
        try:
            auto = auto_parse(text) or text
        except Exception:
            ctx.parse_error = sys.exc_info()
            # do not block user on error
            auto = text

        ctx._ = ctx.auto = auto

        self.eval_context.update(ctx)

    def update_completions(self, command: str, cursor_pos: int) -> None:
        """Generate Python completions using rlcompleter and update via API."""
        if not command:  # No command, no completions
            self.api.hide_completion_popup()
            return

        text_before_cursor = command[:cursor_pos]

        # Determine the fragment to complete (e.g., "my_dict.ke" or "my_var")
        # WORD_BOUNDARY_RE helps find the start of a Python identifier or dotted path
        match = WORD_BOUNDARY_RE.search(text_before_cursor)
        if not match:
            self.api.hide_completion_popup()
            return

        prefix_to_complete = match.group(1)
        if not prefix_to_complete:  # Empty prefix found
            self.api.hide_completion_popup()
            return

        # Use rlcompleter with the plugin's current evaluation context
        # rlcompleter is stateful, so a new instance or careful state management is needed.
        # For simplicity, creating a new one each time is safer with dynamic contexts.
        rl_cmp = rlcompleter.Completer(self.eval_context)

        completions = []
        for i in range(200):  # Limit number of completion attempts
            comp = rl_cmp.complete(prefix_to_complete, i)
            if comp is None:
                break
            completions.append(comp)

        model = self.api.get_completion_model()
        completer_widget = self.api.get_completer()

        if completions:
            model.setStringList(completions)
            completer_widget.setCompletionPrefix(
                prefix_to_complete
            )  # Crucial for QCompleter
            self.api.show_completion_popup()
        else:
            model.setStringList([])  # Clear previous completions
            self.api.hide_completion_popup()

    def register_settings(self, settings):
        return super().register_settings(settings)  # TODO
