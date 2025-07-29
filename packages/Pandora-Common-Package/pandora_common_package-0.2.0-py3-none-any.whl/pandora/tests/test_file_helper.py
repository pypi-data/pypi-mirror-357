# write test cases for FileHelper
import time

from utils.file_helper import FileHelper


class TestFileHelper:
    def setup_class(self):
        self.file_helper = FileHelper()
        self.test_file_path = f"test_file_{time.time()}.txt"
        self.test_folder_path = f"test_folder_{time.time()}"

    def test_create_file(self):
        self.file_helper.create_file(self.test_file_path, "Test Create File")
        assert self.file_helper.verify_exists(self.test_file_path) == True
        self.file_helper.delete_file(self.test_file_path)  # Clean up after test

    # test create file with existing file
    def test_create_file_existing(self):
        self.file_helper.create_file(self.test_file_path, "Test Create File Existing")
        assert self.file_helper.verify_exists(self.test_file_path) == True
        # create another file with same name
        self.file_helper.create_file(self.test_file_path, "Duplicate content")
        assert self.file_helper.verify_exists(self.test_file_path) == True
        # check the content of the file
        content = self.file_helper.read_file_content(self.test_file_path)
        assert content == "Test Create File Existing"
        # clean up after test
        self.file_helper.delete_file(self.test_file_path)

    def test_create_folder(self):
        self.file_helper.create_folder(self.test_folder_path)
        assert self.file_helper.verify_exists(self.test_folder_path) == True
        # clean up after test
        self.file_helper.delete_folder(self.test_folder_path)

    # test create folder with existing folder
    def test_create_folder_existing(self):
        self.file_helper.create_folder(self.test_folder_path)
        assert self.file_helper.verify_exists(self.test_folder_path) == True
        # create another folder with same name
        self.file_helper.create_folder(self.test_folder_path)
        assert self.file_helper.verify_exists(self.test_folder_path) == True
        # clean up after test
        self.file_helper.delete_folder(self.test_folder_path)

    def test_delete_file(self):
        self.file_helper.create_file(self.test_file_path, "Test Create File for Deletion")
        self.file_helper.delete_file(self.test_file_path)
        assert self.file_helper.verify_exists(self.test_file_path) == False

    # test delete file with non-existing file
    def test_delete_file_non_existing(self):
        self.file_helper.delete_file(self.test_file_path)
        assert self.file_helper.verify_exists(self.test_file_path) == False

    def test_delete_folder(self):
        self.file_helper.create_folder(self.test_folder_path)
        self.file_helper.delete_folder(self.test_folder_path)
        assert self.file_helper.verify_exists(self.test_folder_path) == False

    # test read file
    def test_read_file(self):
        self.file_helper.create_file(self.test_file_path, "Test Read File")
        content = self.file_helper.read_file_content(self.test_file_path)
        assert content == "Test Read File"
        self.file_helper.delete_file(self.test_file_path)  # Clean up after test
