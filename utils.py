import os

def fetchEmailtemplate():
    email_folder_path = os.path.join('templates', 'email')
    email_files_array = []
    for index, filename in enumerate(os.listdir(email_folder_path)):
        file_name, file_extension = os.path.splitext(filename)
        if file_extension == '.html':
            email_files_array.append(file_name)
    return email_files_array
