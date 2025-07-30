import shutil
from pathlib import Path


def chunks(lst: list, n: int) -> list:
    """
    Yield successive n-sized chunks from lst.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_abspath_files_directory(directory: str, extension: str = "fna") -> tuple:
    """
    Takes in a directory and returns the abspath of all the files in the directory as a list

    Parameters
    ----------
    extension : str
        The extension of the files to return. Default is fna
    directory : str
        The directory to get the abspaths for

    Returns
    -------
    list
        A list of the abspaths of all the files in the directory
    """
    pabs = Path(directory).resolve()
    p = pabs.glob(f"**/*.{extension}")
    return pabs, [x for x in p if x.is_file()]


def split_to_subdirectories(
    file_paths: list, abs_path_out: str, amount_per_folder: int
):
    """Take in a list of file absolute paths, and copy them to folders

    Parameters
    ----------
    file_paths : list
        The list of abspaths to the file folders
    abs_path_out : str
        The absolute path to the output directory, inside input directory.
    amount_per_folder : int
        The amount of files per folder to split the files into
    """
    files = chunks(file_paths, amount_per_folder)
    for index, chunk in enumerate(files, 1):
        output_dir = Path(abs_path_out) / f"vamb{index}"
        output_dir.mkdir(parents=True, exist_ok=True)
        for file_path in chunk:
            shutil.move(file_path, output_dir / file_path.name)


if __name__ == "__main__":
    SIZE = 200
    path_abs, path_list = get_abspath_files_directory("TMP")
    split_to_subdirectories(path_list, path_abs, SIZE)
