import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class FileHelper:
    """
    A helper class for file and folder operations
    """

    @staticmethod
    def create_file(file_path, content=""):
        """
        Create a file. If the file already exists, skip creation.
        :param file_path: File path
        :param content: Content to write into the file
        """
        if os.path.exists(file_path):
            print(f"File already exists: {file_path}")
            return
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            print(f"File created: {file_path}")
        except Exception as e:
            print(f"Error occurred while creating file: {e}")

    @staticmethod
    def create_folder(folder_path):
        """
        Create a folder.
        :param folder_path: Folder path
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Folder created: {folder_path}")
        except Exception as e:
            print(f"Error occurred while creating folder: {e}")

    @staticmethod
    def delete_file(file_path):
        """
        Delete a specified file.
        :param file_path: File path
        """
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
            else:
                print(f"File does not exist: {file_path}")
        except Exception as e:
            print(f"Error occurred while deleting file: {e}")

    @staticmethod
    def delete_folder(folder_path):
        """
        Delete a specified folder.
        :param folder_path: Folder path
        """
        try:
            if os.path.isdir(folder_path):
                os.rmdir(folder_path)
                print(f"Folder deleted: {folder_path}")
            else:
                print(f"Folder does not exist: {folder_path}")
        except Exception as e:
            print(f"Error occurred while deleting folder: {e}")

    @staticmethod
    def verify_exists(path):
        """
        Verify whether a file or folder exists.
        :param path: File or folder path
        :return: Returns True if exists, otherwise False
        """
        return os.path.exists(path)

    @staticmethod
    def read_file_content(file_path):
        """
        Read the content of a file.
        :param file_path: File path
        :return: File content as a string
        """
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()
                return content
            else:
                print(f"File does not exist: {file_path}")
                return None
        except Exception as e:
            print(f"Error occurred while reading file content: {e}")
            return None
