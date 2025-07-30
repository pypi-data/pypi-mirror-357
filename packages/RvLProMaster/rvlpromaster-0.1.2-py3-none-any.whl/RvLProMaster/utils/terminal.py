import subprocess
import io
import sys
import textwrap
import traceback
import ast
from .create_log import CreateLog

class _Terminal:
    def __init__(self):
        self.output_terminal = ''

    def Bash(self, command: str):
        """
        Run a bash command and return the output.
        """
        try:
            pr = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                capture_output=True,
            )
            self.output_terminal = pr.stdout or pr.stderr
            return self
        except subprocess.CalledProcessError as e:
            CreateLog("ERROR", f"{e}")
            return self

    async def Python(self, command: str):
        # Dedent input code for proper formatting
        corrected_code = textwrap.dedent(command)
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = output_buffer
        sys.stderr = output_buffer

        error_message = ""
        try:
            parsed = ast.parse(corrected_code)

            last_expr = None
            if parsed.body and isinstance(parsed.body[-1], ast.Expr):
                last_expr = parsed.body.pop()

            code_body = ''.join(ast.unparse(stmt) + '\n' for stmt in parsed.body)

            if last_expr is not None and isinstance(last_expr, ast.Expr):
                expr_code = ast.unparse(last_expr.value)
                code_body += f"\n__last_expr = {expr_code}"
            else:
                code_body += "\n__last_expr = None"

            func_code = f"""
async def __eval_async():
{textwrap.indent(code_body, '    ')}
    if callable(__last_expr):
        result = __last_expr()
        if result is not None:
            print(result)
    elif __last_expr is not None:
        print(__last_expr)
"""

            exec_locals = {}
            exec_globals = globals()
            exec(func_code, exec_globals, exec_locals)

            await exec_locals["__eval_async"]()

        except Exception:
            error_message = traceback.format_exc()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        return output_buffer.getvalue() + (error_message if error_message else "")


Terminal = _Terminal()
