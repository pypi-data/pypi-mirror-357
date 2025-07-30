import json
import pandas as pd

from tdf_tool.modules.translate.flutter.flutter_tranalate_interface import (
    FlutterTranslateDartFileMixin,
    FlutterTranslateModuleTool,
)
from tdf_tool.tools.print import Print
from tdf_tool.tools.shell_dir import ShellDir


class ReflowFile(FlutterTranslateDartFileMixin):
    """回流文件相关操作的类"""

    def find(self, file_path: str) -> str:
        # 读取文件中的所有表
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        need_reflow_module = set()
        Print.stage(f"开始文件回流检查: {file_path}")

        for sheet_name in sheet_names:
            Print.title(f"开始检查模块: {sheet_name}")
            # 读取子表
            sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)
            # 获取表头数据并转换为数组
            header_array = sheet_df.columns.values.tolist()
            # header_array中的元素中包换”修改“两个字的，则需要回流
            for header in header_array:
                if "修改" in header:
                    need_reflow_module.add(sheet_name)
                    Print.step(f"需要回流模块: {sheet_name} 语言：{header}")
        need_json = json.dumps(list(need_reflow_module))
        Print.str(f"需要回流模块: {need_json}")
        return need_json

    def start(self, file_path: str, module: str = None):
        Print.stage(f"开始文件回流: {file_path}")
        # 读取文件中的所有表
        for module_name in FlutterTranslateModuleTool.businessModuleList():
            if module is not None and module_name != module:
                continue
            Print.title(f"开始回流模块: {module_name}")
            target_path = ShellDir.getInModuleIntlDir(module_name)
            # 读取第一列的数据
            sheet_df: pd.DataFrame = pd.read_excel(file_path, sheet_name=module_name)
            all_data_dict = {}
            # 读取列名中带"修改"两个字的列
            for column in sheet_df.columns:
                if "修改" in column:
                    # 去掉"修改"两个字
                    i18n_code = column.replace("修改", "")
                    # 获取第一列的数据作为key
                    first_column = sheet_df.iloc[:, 0]
                    # 获取当前列的数据作为value
                    column_data = sheet_df[column]
                    # 生成字典
                    data_dict = dict(zip(first_column, column_data))
                    # 去除value中是nan的数据
                    data_dict = {k: v for k, v in data_dict.items() if pd.notna(v)}
                    # 处理data_dict中的转义符， \xa0 替换为空字符串
                    for k, v in data_dict.items():
                        if isinstance(v, str):
                            # 检查k,v 中的占位符%s,%d,%f等的数量是否一致
                            k_count = k.count("%s") + k.count("%d") + k.count("%f")
                            v_count = v.count("%s") + v.count("%d") + v.count("%f")
                            if k_count != v_count:
                                Print.warning(
                                    f"不进行替换，占位符数量不一致:\n {k} \n {v}"
                                )
                                continue
                            data_dict[k] = v.replace("\xa0", " ")
                    all_data_dict[i18n_code] = data_dict
            # 将all_data_dict写入到对应的文件中
            for i18n_code, data_dict in all_data_dict.items():
                # 获取文件名
                file_name = f"{target_path}/i18n/{module_name}_{i18n_code}.dart"
                # 获取文件内容
                dart_data_dict = self.getDartFileParamsJson(file_name, i18n_code)
                for k, v in dart_data_dict.items():
                    if k in data_dict:
                        Print.line()
                        Print.str(f"修改文案: \n {v} \n {data_dict[k]}")
                        dart_data_dict[k] = data_dict[k]
                # 修改文件内容
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.generateDartMapFile(i18n_code, dart_data_dict))
