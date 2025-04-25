import os

def print_directory_tree(start_path, indent=''):
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        print(indent + '|-- ' + item)
        if os.path.isdir(item_path):
            print_directory_tree(item_path, indent + '    ')

# 修改为你的项目路径

project_path = 'C:/Users/chen/Desktop/crad_system'
print_directory_tree(project_path)