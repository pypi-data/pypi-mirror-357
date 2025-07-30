from tdf_tool.modules.multi_code.tools.reflow_file import ReflowFile


class FlutterReflow:
    """flutter 国际化回流"""

    def find(self, style: str = "file", file_path: str = ""):
        """
        查找需要回流的库
        """
        if style == "file":
            ReflowFile().find(file_path)
        elif style == "server":
            print("server")

    def start(self, style: str = "file", file_path: str = "", module: str = None):
        """
        开始回流，可以通过文件的方式: --style=file
        或者通过server的方式: --style=server
        """
        if style == "file":
            ReflowFile().start(file_path, module)
        elif style == "server":
            print("server")
