from compiler import Compiler
import os, json, shutil


class CustomCompiler:
    def __init__(self, current_project):
        self.current_project = current_project

        with open(f"{self.current_project}/properties.json", "r") as f:
            self.properties = json.loads(f.read())

        self.domain = "net.minecraftmoddingtool." + self.properties["mod_id"]
        self.initialize_custom_items()

    def initialize_custom_items(self):
        if not os.path.isdir(os.path.join(self.current_project, "items")):
            return

        if not os.path.isdir(os.path.join(self.current_project, "custom_java")):
            os.mkdir(os.path.join(self.current_project, "custom_java"))

        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path), "r") as f:
                item = json.loads(f.read())
            if not "customProperties" in item.keys():
                continue

            filename = path.replace(".json", "").split("_")
            filename = "".join([part.title() for part in filename]) + "Item"
            shutil.copy("templates/custom/CustomItem.java", os.path.join(self.current_project, "custom_java", filename+".java"))
            self.replace_custom_item_placeholders(filename)

    
    def replace_custom_item_placeholders(self, item_class):
        path = os.path.join(self.current_project, "custom_java", item_class+".java")
        with open(path, "r+") as f:
            content = f.read()
            content = Compiler.bulk_replace(content, {f"%domain%": self.domain, f"%itemClass%": item_class, f"%args%": ""})
            content = Compiler.replace_conditionals(content, {"IfUseOnBlock": True, "IfAppendTooltip": False})
            f.seek(0)
            f.truncate(0)
            f.write(content)


ccompiler = CustomCompiler("cool_minecraft_mod")
