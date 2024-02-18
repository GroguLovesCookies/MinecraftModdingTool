import os
import json
import shutil
import subprocess


class Compiler:
    def __init__(self, current_project):
        self.current_project = current_project

        with open(f"{self.current_project}/properties.json", "r") as f:
            self.properties = json.loads(f.read())

        self.domain = "net.minecraftmoddingtool." + self.properties["mod_id"]
        self.translations = {}
        self.items = []
        self.blocks = []

    def compile(self):
        self.copy_files()
        self.initialize_gradle_properties()
        self.initialize_mod_items()
        self.initialize_mod_item_groups()
        self.initialize_mod_main()
        self.initialize_fabric_mixins()
        self.initialize_fabric_mod()
        self.initialize_mod_blocks()
        self.initialize_mod_model_provider()
        self.initialize_textures()
        self.initialize_translations()

    def copy_files(self):
        if os.path.isdir(os.path.join(self.current_project, "compiled")):
            shutil.rmtree(os.path.join(self.current_project, "compiled"))

        shutil.copytree("templates/files", f"{self.current_project}/compiled")
        cur_domain = ""
        for folder in self.domain.split(".")[:-1]:
            cur_domain += folder
            os.mkdir(os.path.join(self.current_project, "compiled", "src", "main", "java", cur_domain))
            cur_domain += "/"
        shutil.copytree("templates/javaSRC", os.path.join(self.current_project, "compiled", "src", "main", "java", cur_domain, self.properties["mod_id"]))

        shutil.copytree("templates/assets/dummy", os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"]))

    def initialize_gradle_properties(self):
        contents = ""
        gradle_file = os.path.join(self.current_project, "compiled", "gradle.properties")
        with open(gradle_file, "r") as f:
            contents = str(f.read())
        contents = Compiler.bulk_replace(contents, {"%modVersion%": "0.1", f"%domain%": self.domain, "%modID%": self.properties["mod_id"]})
        print(contents)

        with open(gradle_file, "w") as f:
            f.write(contents)

    def initialize_mod_items(self):
        imports, content = Compiler.parse_template("templates/snippets/item_adder.txt")

        combined_contents = ""

        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path), "r") as f:
                self.items.append(json.loads(f.read()))

        for item in self.items:
            self.translations["item." + ".".join(item["id"].split(":"))] = item["name"]
            contents_copy = content[:]

            contents_copy = Compiler.bulk_replace(contents_copy, {f"%itemVar%": item["id"].split(":")[1].upper(), f"%itemID%": item["id"].split(":")[1]})

            combined_contents += contents_copy + "\n"

        contents = ""
        with open(os.path.join(self.current_project, "compiled", "src", "main", "java", *self.domain.split("."), "item", "ModItems.java"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%imports%": imports, f"%registerItems%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_item_groups(self):
        contents = ""
        imports, content = Compiler.parse_template("templates/snippets/item_group_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""

        item_groups = []
        for path in os.listdir(os.path.join(self.current_project, "item_groups")):
            with open(os.path.join(self.current_project, "item_groups", path), "r") as f:
                item_groups.append(json.loads(f.read()))
        
        for group in item_groups:
            content_copy = content[:]

            icon = group["icon"]
            group_items = group["items"]
            if icon.startswith("minecraft:"):
                iconItem = "Items." + icon.split(":")[1].upper()
            else:
                iconItem = "ModItems." + icon.split(":")[1].upper()

            content_copy = Compiler.bulk_replace(content_copy, {f"%GROUP_NAME%": group["id"].upper(), f"%groupID%": group["id"], 
            f"%modID%": self.properties["mod_id"], f"%iconItem%": iconItem, f"%Items%": Compiler.get_item_to_item_group_code(group_items)})
            combined_contents += content_copy + "\n"
            self.translations["itemgroup." + group["id"]] = group["name"]

        contents = ""
        with open(os.path.join(self.current_project, "compiled", "src", "main", "java", *self.domain.split("."), "item", "ModItemGroups.java"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%imports%": imports, f"%insertItemGroups%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_main(self):
        for path in ["ModMain.java", "ModClient.java", "ModDataGenerator.java"]:
            with open(os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), path), "r+") as f:
                contents = f.read()
                contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, "%modID%": self.properties["mod_id"]})
                f.seek(0)
                f.truncate(0)
                f.write(contents)

    def initialize_fabric_mixins(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/resources/")
        os.rename(os.path.join(resource_path, "dummy.mixins.json"), os.path.join(resource_path, f"{self.properties['mod_id']}.mixins.json"))
        
        with open(os.path.join(resource_path, f"{self.properties['mod_id']}.mixins.json"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%mixins%": ""})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_fabric_mod(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/resources/fabric.mod.json")

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%modID%": self.properties["mod_id"], f"%modName%": self.properties["title"],
            f"%modDescr%": "A Mod Created with MinecraftModdingTool!", f"%domain%": self.domain})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_blocks(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "block/ModBlocks.java")
        imports, content = Compiler.parse_template("templates/snippets/block_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for path in os.listdir(os.path.join(self.current_project, "blocks")):
            with open(os.path.join(self.current_project, "blocks", path), "r") as f:
                self.blocks.append(json.loads(f.read()))

        for block in self.blocks:
            content_copy = content[:]
            replacements = {
                f"%blockVar%": block["id"].split(":")[1].upper(),
                f"%handBreakable%": "true" if block["properties"]["handBreakable"] else "false",
                f"%breakInstantly%": ".breakInstantly()" if block["properties"]["instaminable"] else "",
                f"%requiresTool%": ".requiresTool()" if block["properties"]["requiresTool"] else "",
                f"%luminance%": f".luminance({block['properties']['lightLevel']})" if int(block["properties"]["lightLevel"]) > 0 else "",
                f"%blockID%": block["id"].split(":")[1]
            }
            content_copy = Compiler.bulk_replace(content_copy, replacements)
            combined_contents += content_copy + "\n"

            self.translations["block." + self.properties["mod_id"] + "." + block["id"].split(":")[1]] = block["name"]
        
        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {
                f"%domain%": self.domain, "%modID%": self.properties["mod_id"], 
                f"%imports%": imports, f"%registerBlocksHere%": combined_contents
            })
            f.seek(0)
            f.truncate(0)
            f.write(contents)
        

    
    def initialize_mod_model_provider(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModModelProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/register_generated_model.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for item in self.items:
            content_copy = content[:]
            content_copy = Compiler.bulk_replace(content_copy, {f"%itemVar%": item["id"].split(":")[1].upper()})
            combined_contents += content_copy + "\n"

        imports2, contents2 = Compiler.parse_template("templates/snippets/register_block_cube_all_model.txt")
        imports2 = Compiler.bulk_replace(imports2, {f"%domain%": self.domain})
        
        combined_contents2 = ""
        for block in self.blocks:
            content_copy = contents2[:]
            content_copy = Compiler.bulk_replace(content_copy, {f"%blockVar%": block["id"].split(":")[1].upper()})
            combined_contents2 += content_copy + "\n"
        
        with open(resource_path, "r+") as f:
            contents = Compiler.bulk_replace(f.read(), {f"%domain%": self.domain, f"%imports%": imports, f"%itemModelsHere%": combined_contents,
            f"%blockModelsHere%": combined_contents2, f"%blockImports%": imports2})
            f.seek(0)
            f.truncate(0)
            f.write(contents)
    
    def initialize_textures(self):
        for item in self.items:
            shutil.copy(item["texture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/item", item["id"].split(":")[1]+".png"))
        for block in self.blocks:
            shutil.copy(block["texture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/block", block["id"].split(":")[1]+".png"))
    
    def initialize_translations(self):
        with open(os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "lang/en_us.json"), "r+") as f:
            f.write(json.dumps(self.translations))

    def redo_gradle(self):
        os.chdir(os.path.join(self.current_project, "compiled"))
        subprocess.run(["./gradlew", "--daemon"])
        subprocess.run(["./gradlew", "runDatagen"])
        os.chdir("../..")

    def run_client(self):
        os.chdir(os.path.join(self.current_project, "compiled"))
        subprocess.run(["./gradlew", "runClient"])
        os.chdir("../..")
    
    @staticmethod
    def parse_template(template_file):
        imports = ""

        with open(template_file) as f:
            contents = f.read()
            imports_index = contents.find("!IMPORTS!")
            contents_index = contents.find("!CONTENT!")
            
            imports = contents[imports_index+9:contents_index].strip("\n")
            contents = contents[contents_index+9:].strip("\n")

        return imports, contents

    @staticmethod
    def bulk_replace(string, replacements):
        for src, dst in replacements.items():
            string = string.replace(src, dst)
        return string

    @staticmethod
    def get_item_to_item_group_code(items):
        imports, content = Compiler.parse_template("templates/snippets/item_to_item_group.txt")
        combined_contents = ""
        for item in items:
            content_copy = content[:]
            if item.startswith("minecraft:"):
                item_space = "Items"
            else:
                item_space = "ModItems"

            content_copy = Compiler.bulk_replace(content_copy, {f"%itemSpace%": item_space, f"%itemVar%": item.split(":")[1].upper()})
            combined_contents += content_copy + "\n"
        return combined_contents


compiler = Compiler("cool_minecraft_mod")
compiler.compile()
compiler.redo_gradle()
compiler.run_client()