import os
import shutil
import zipfile
from zoneinfo import ZoneInfo

from IPython.core.getipython import get_ipython
from IPython.display import FileLink, display
from kaggle.api.kaggle_api_extended import KaggleApi
from tabulate import tabulate


def zip_and_download(file_or_dir, output_filename='output.zip', compression_level=zipfile.ZIP_DEFLATED,
                     target_dir='/kaggle/working/'):
    """
    压缩文件/目录并根据环境提供下载方式
    """
    if not os.path.exists(file_or_dir):
        raise FileNotFoundError(f"源路径不存在: {file_or_dir}")

    original_dir = os.getcwd()
    output_path = os.path.join(target_dir, output_filename)

    try:
        os.chdir(target_dir)

        if not output_filename.endswith('.zip'):
            output_filename = f"{output_filename}.zip"

        with zipfile.ZipFile(output_filename, 'w',
                             compression=zipfile.ZIP_DEFLATED,
                             compresslevel=compression_level) as zipf:

            if os.path.isfile(file_or_dir):
                zipf.write(file_or_dir, os.path.basename(file_or_dir))
            else:
                for root, _, files in os.walk(file_or_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(file_or_dir))
                        zipf.write(file_path, arcname)

        # 检测是否在Jupyter环境中运行
        if 'IPKernelApp' in get_ipython().config:
            print("在Notebook中点击下方链接下载:")
            display(FileLink(output_filename))

        print(f"压缩完成！ZIP文件路径: {output_path}")
        print("在Kaggle中，您可以在右侧面板的Output标签中找到下载链接")

    except Exception as e:
        print(f"压缩失败: {str(e)}")
        return None
    finally:
        os.chdir(original_dir)


def copy_directory(source_dir, target_dir):
    """
    递归复制目录从源路径到目标路径

    参数:
    source_dir (str): 源目录路径
    target_dir (str): 目标目录路径
    """
    try:
        # 检查源目录是否存在
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"源文件不存在: {source_dir}")

        # 如果目标目录已存在，先删除（可选，根据需求决定）
        if os.path.exists(target_dir):
            print(f"目标目录已存在，将其删除: {target_dir}")
            shutil.rmtree(target_dir)

        # 递归复制目录
        shutil.copytree(source_dir, target_dir)
        print(f"目录复制完成: {source_dir} -> {target_dir}")

    except Exception as e:
        print(f"复制过程中出错: {e}")

def list_my_datasets():
    # 初始化Kaggle API
    api = KaggleApi()
    api.authenticate()

    # 获取用户名称（使用config_value方法）
    username = api.config_values['username']

    # 获取用户的所有数据集
    datasets = api.dataset_list(user=username, page=1)

    if not datasets:
        print("未找到你的数据集。")
        return

        # 准备数据集信息列表
    dataset_info = []
    for dataset in datasets:
        dataset_info.append({
                'title': dataset.title,
                'ref': dataset.ref,
                'creator_name': dataset.creator_name,
                'ID': dataset.id,
                'updated_time': dataset.last_updated.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
                'view_count': dataset.view_count,
                'vote_count': dataset.vote_count,
                'size(MB)': dataset.total_bytes / (1024 * 1024) if dataset.total_bytes else 0,
                'URL': f"https://www.kaggle.com/datasets/{dataset.ref}"
            })
    if not dataset_info:
        print("没有可用的数据集信息")
    else:
        # 提取表格数据（显式转换 headers 为列表）
        # headers = list(dataset_info[0].keys())  # 关键修改点
        headers = ['title', 'ref', 'creator_name', 'ID', 'updated_time', 'view_count','vote_count', 'size(MB)', 'URL']
        api.print_table(dataset_info, headers)
            # rows = [list(data.values()) for data in dataset_info]
            #
            # # 打印表格
            # print(tabulate(rows, headers=headers, tablefmt="grid", showindex=True))
            #
            # # 打印统计信息
            # print(f"\n共有 {len(dataset_info)} 个数据集")
            # total_size = sum(data['数据集大小(MB)'] for data in dataset_info)
            # print(f"总大小: {total_size:.2f} MB")


def list_my_kernels():
    # 初始化 Kaggle API
    api = KaggleApi()
    # 验证 API 凭证
    api.authenticate()

    try:
        # 获取用户名称（使用config_value方法）
        username = api.config_values['username']

        # 获取用户所有内核
        kernels = api.kernels_list(user=username, page_size=1000)

        if not kernels:
            print("未找到任何内核。")
            return

            # 准备数据集信息列表
        kernels_info = []
        for kernel in kernels:
            kernels_info.append({
                    '标题': kernel.title,
                    '链接': kernel.ref,
                    '创建人': kernel.author,
                    '数据集ID': kernel.id,
                    '更新日期': kernel.last_run_time.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
                    # '查看次数': kernel.view_count,
                    # '投票次数': kernel.vote_count,
                    'URL': f"https://www.kaggle.com/datasets/{kernel.ref}"
                })
        return kernels_info

    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("请确保已正确配置 Kaggle API 凭证 (kaggle.json)")
        print("更多信息请参考: https://www.kaggle.com/docs/api")
